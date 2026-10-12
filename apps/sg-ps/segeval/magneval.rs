//! Magnetic Lasso evaluation: a simulated hand traces each object's outline (ground truth) with
//! a smooth wobble; IoU of the resulting selection for a plain lasso, the old point-snapping
//! magnetic lasso and the Intelligent Scissors live wire.
//! Usage: cargo run --release -p photocraft-algo --example magneval -- <dir of NAME.ppm/.pgm> [wobble px] [frequency]
use photocraft_algo::scissors::Scissors;

fn read_pnm(path: &str) -> (usize, usize, Vec<u8>) {
    let data = std::fs::read(path).expect("read");
    let mut fields = Vec::new();
    let mut i = 0;
    while fields.len() < 4 {
        while data[i].is_ascii_whitespace() { i += 1; }
        if data[i] == b'#' { while data[i] != b'\n' { i += 1; } continue; }
        let s = i;
        while !data[i].is_ascii_whitespace() { i += 1; }
        fields.push(String::from_utf8_lossy(&data[s..i]).to_string());
    }
    i += 1;
    (fields[1].parse().unwrap(), fields[2].parse().unwrap(), data[i..].to_vec())
}

/// Largest 4-connected component's outer boundary, traced (Moore neighbourhood), as pixel centres.
fn contour(m: &[bool], w: usize, h: usize) -> Vec<(f32, f32)> {
    // Largest component.
    let mut lab = vec![0u32; w * h];
    let (mut best, mut best_n, mut next) = (0u32, 0usize, 1u32);
    for s in 0..w * h {
        if !m[s] || lab[s] != 0 { continue; }
        let mut st = vec![s]; lab[s] = next; let mut n = 0;
        while let Some(k) = st.pop() {
            n += 1;
            let (x, y) = (k % w, k / w);
            for (a, b) in [(x.wrapping_sub(1), y), (x + 1, y), (x, y.wrapping_sub(1)), (x, y + 1)] {
                if a < w && b < h && m[b * w + a] && lab[b * w + a] == 0 { lab[b * w + a] = next; st.push(b * w + a); }
            }
        }
        if n > best_n { best_n = n; best = next; }
        next += 1;
    }
    let inside = |x: i32, y: i32| x >= 0 && y >= 0 && (x as usize) < w && (y as usize) < h && lab[y as usize * w + x as usize] == best;
    let start = (0..w * h).find(|k| lab[*k] == best).unwrap();
    let s = ((start % w) as i32, (start / w) as i32);
    let dirs = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)];
    let mut out = vec![s];
    let (mut p, mut d) = (s, 6usize);
    for _ in 0..4 * (w + h) * 4 {
        let mut found = false;
        for k in 0..8 {
            let nd = (d + 6 + k) % 8;
            let q = (p.0 + dirs[nd].0, p.1 + dirs[nd].1);
            if inside(q.0, q.1) { p = q; d = nd; found = true; break; }
        }
        if !found || p == s { break; }
        out.push(p);
    }
    out.into_iter().map(|(x, y)| (x as f32 + 0.5, y as f32 + 0.5)).collect()
}

/// Even-odd polygon fill at pixel centres.
fn fill(poly: &[(f32, f32)], w: usize, h: usize) -> Vec<bool> {
    let mut m = vec![false; w * h];
    for y in 0..h {
        let yc = y as f32 + 0.5;
        let mut xs = Vec::new();
        for i in 0..poly.len() {
            let (a, b) = (poly[i], poly[(i + 1) % poly.len()]);
            if (a.1 <= yc) != (b.1 <= yc) { xs.push(a.0 + (yc - a.1) / (b.1 - a.1) * (b.0 - a.0)); }
        }
        xs.sort_by(f32::total_cmp);
        for pr in xs.chunks_exact(2) {
            let (x0, x1) = ((pr[0] - 0.5).ceil().max(0.0) as usize, ((pr[1] - 0.5).floor() as i64).min(w as i64 - 1));
            for x in x0..=(x1.max(0) as usize) { if (x as i64) <= x1 { m[y * w + x] = true; } }
        }
    }
    m
}

fn iou(a: &[bool], b: &[bool]) -> f32 {
    let i = a.iter().zip(b).filter(|(x, y)| **x && **y).count();
    let u = a.iter().zip(b).filter(|(x, y)| **x || **y).count();
    i as f32 / u.max(1) as f32
}

/// The old engine's per-point snap (selection_cmds.rs magnetic_lasso).
fn old_snap(s: &Scissors, raw: &[(f32, f32)], radius: i32, w: usize, h: usize) -> Vec<(f32, f32)> {
    let mut out: Vec<(f32, f32)> = Vec::new();
    for &(rx, ry) in raw {
        let (cx, cy) = (rx.round() as i32, ry.round() as i32);
        let (mut best, mut bs) = ((rx, ry), f32::NEG_INFINITY);
        for dy in -radius..=radius { for dx in -radius..=radius {
            let d = ((dx * dx + dy * dy) as f32).sqrt();
            let (x, y) = (cx + dx, cy + dy);
            if d > radius as f32 || x < 0 || y < 0 || x >= w as i32 || y >= h as i32 { continue; }
            let cont = out.last().map_or(0.0, |q| { let st = (rx - q.0).hypot(ry - q.1); ((x as f32 - q.0).hypot(y as f32 - q.1) - st).abs() });
            let sc = s.strength(x, y) - d * 5.0 - cont * 1.5;
            if sc > bs { bs = sc; best = (x as f32, y as f32); }
        }}
        if out.last().is_none_or(|q| (q.0 - best.0).hypot(q.1 - best.1) >= 1.0) { out.push(best); }
    }
    out
}

/// Live wire in the detection corridor, with automatic anchors every `seg` pixels of wire.
fn live_wire(s: &Scissors, cursor: &[(f32, f32)], width: f32, contrast: f32, seg: f32) -> Vec<(f32, f32)> {
    let first = s.snap(cursor[0], width, contrast);
    let mut fixed: Vec<(i32, i32)> = vec![first];
    let mut anchor = first;
    let mut track: Vec<(f32, f32)> = Vec::new();
    let mut last = vec![first];
    let plen = |p: &[(i32, i32)]| -> f32 { p.windows(2).map(|w| (((w[1].0 - w[0].0).pow(2) + (w[1].1 - w[0].1).pow(2)) as f32).sqrt()).sum() };
    for &c in cursor.iter().skip(1) {
        let path = s.wire(anchor, &track, c, width, contrast);
        track.push(c);
        let len = plen(&path);
        if len > seg {
            let mut run = 0.0; let mut cut = path.len() - 1;
            for (i, w) in path.windows(2).enumerate() {
                run += (((w[1].0 - w[0].0).pow(2) + (w[1].1 - w[0].1).pow(2)) as f32).sqrt();
                if run >= len * 0.7 { cut = i + 1; break; }
            }
            fixed.extend(&path[1..=cut]);
            anchor = path[cut];
            // The track restarts at the new anchor (the pointer's recent points stay).
            let keep = track.len().saturating_sub(3);
            track.drain(..keep);
            last = vec![anchor];
        } else {
            last = path;
        }
    }
    fixed.extend(last.iter().skip(1));
    let end = *fixed.last().unwrap();
    let closing = s.wire(end, &[], (first.0 as f32, first.1 as f32), width, contrast);
    fixed.extend(closing.iter().skip(1));
    fixed.into_iter().map(|(x, y)| (x as f32 + 0.5, y as f32 + 0.5)).collect()
}

fn main() {
    let dir = std::env::args().nth(1).expect("dir");
    let wobble: f32 = std::env::args().nth(2).map_or(4.0, |v| v.parse().unwrap());
    let seg: f32 = std::env::args().nth(3).map_or(40.0, |v| v.parse().unwrap());
    let mut names: Vec<String> = std::fs::read_dir(&dir).unwrap().filter_map(|e| e.ok()?.file_name().into_string().ok()?.strip_suffix(".ppm").map(String::from)).collect();
    names.sort();
    let mut tot = [0.0f32; 3];
    let mut ms = [0.0f64; 3];
    let mut n = 0;
    for name in &names {
        let (w, h, rgb) = read_pnm(&format!("{dir}/{name}.ppm"));
        let (_, _, g) = read_pnm(&format!("{dir}/{name}.pgm"));
        let gt: Vec<bool> = g.iter().map(|v| *v > 127).collect();
        if gt.iter().filter(|v| **v).count() < 200 { continue; }
        let c = contour(&gt, w, h);
        if c.len() < 30 { continue; }
        // The user zooms so the object is about 600 screen pixels across: the wobble, Width and
        // anchor spacing are screen pixels, divided by that zoom here.
        let (mut bx0, mut by0, mut bx1, mut by1) = (f32::MAX, f32::MAX, f32::MIN, f32::MIN);
        for &(x, y) in &c { bx0 = bx0.min(x); by0 = by0.min(y); bx1 = bx1.max(x); by1 = by1.max(y); }
        let min_size: f32 = std::env::var("MIN_SIZE").ok().and_then(|v| v.parse().ok()).unwrap_or(0.0);
        if (bx1 - bx0).max(by1 - by0) < min_size { continue; }
        let zoom = (600.0 / (bx1 - bx0).max(by1 - by0).max(1.0)).clamp(0.25, 16.0);
        let (wobble, width, seg) = (wobble / zoom, (10.0 / zoom).max(1.5), seg / zoom);
        let step = ((3.0 / zoom).round() as usize).max(1);
        // The hand: every 3rd outline point, pushed off the outline by a smooth wobble.
        let mut seed = 1234567u64 ^ name.len() as u64 * 7919;
        let mut rnd = || { seed ^= seed << 13; seed ^= seed >> 7; seed ^= seed << 17; (seed % 10000) as f32 / 10000.0 * 2.0 - 1.0 };
        let (p1, p2) = (rnd() * 3.0, rnd() * 3.0);
        let hand: Vec<(f32, f32)> = c.iter().enumerate().step_by(step).map(|(i, &(x, y))| {
            let a = c[(i + c.len() - 3) % c.len()]; let b = c[(i + 3) % c.len()];
            let (tx, ty) = (b.0 - a.0, b.1 - a.1); let l = tx.hypot(ty).max(1e-3);
            let t = i as f32 / c.len() as f32 * std::f32::consts::TAU;
            let off = wobble * (0.6 * (t * 5.0 + p1).sin() + 0.4 * (t * 13.0 + p2).sin());
            ((x - ty / l * off).clamp(0.0, w as f32 - 1.0), (y + tx / l * off).clamp(0.0, h as f32 - 1.0))
        }).collect();
        let s = Scissors::new(&rgb, w, h, 3);
        let t0 = std::time::Instant::now();
        let r0 = iou(&fill(&hand, w, h), &gt); ms[0] += t0.elapsed().as_secs_f64() * 1e3;
        let t0 = std::time::Instant::now();
        let r1 = iou(&fill(&old_snap(&s, &hand, width.round() as i32, w, h), w, h), &gt); ms[1] += t0.elapsed().as_secs_f64() * 1e3;
        let t0 = std::time::Instant::now();
        let wire = live_wire(&s, &hand, width, 0.1, seg);
        if std::env::var("DBG").ok().as_deref() == Some(name.as_str()) {
            let txt: String = wire.iter().map(|p| format!("{} {}\n", p.0, p.1)).collect();
            std::fs::write("/tmp/claude-0/-home-user/1b2b81d1-2014-57b1-90cc-6d868aaeeb2b/scratchpad/wire.txt", txt).unwrap();
            let txt: String = hand.iter().map(|p| format!("{} {}\n", p.0, p.1)).collect();
            std::fs::write("/tmp/claude-0/-home-user/1b2b81d1-2014-57b1-90cc-6d868aaeeb2b/scratchpad/hand.txt", txt).unwrap();
        }
        let wm = fill(&wire, w, h);
        let er: Vec<bool> = (0..w * h).map(|k| { let (x, y) = (k % w, k / w);
            wm[k] && x > 0 && y > 0 && x + 1 < w && y + 1 < h && wm[k - 1] && wm[k + 1] && wm[k - w] && wm[k + w] }).collect();
        let dl: Vec<bool> = (0..w * h).map(|k| { let (x, y) = (k % w, k / w);
            wm[k] || (x > 0 && wm[k - 1]) || (x + 1 < w && wm[k + 1]) || (y > 0 && wm[k - w]) || (y + 1 < h && wm[k + w]) }).collect();
        if std::env::var("OFF").is_ok() { println!("  off: erode {:.3} as-is {:.3} dilate {:.3}", iou(&er, &gt), iou(&wm, &gt), iou(&dl, &gt)); }
        let r2 = iou(&wm, &gt); ms[2] += t0.elapsed().as_secs_f64() * 1e3;
        println!("{name} lasso {r0:.3} old {r1:.3} wire {r2:.3}");
        tot[0] += r0; tot[1] += r1; tot[2] += r2; n += 1;
    }
    let k = n.max(1) as f32;
    println!("MEAN ({n}) lasso {:.4}  old magnetic {:.4}  live wire {:.4}   ms: {:.0} {:.0} {:.0}", tot[0] / k, tot[1] / k, tot[2] / k, ms[0] / k as f64, ms[1] / k as f64, ms[2] / k as f64);
}
