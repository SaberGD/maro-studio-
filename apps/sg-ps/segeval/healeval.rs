//! HORIX evaluation harness: Spot Healing / Healing Brush on photos with synthetic blemishes
//! (spots, specks, wires) whose clean original is known.
//! Copy into crates/engine/examples/ of the rebranded tree, then:
//!   cargo run --release -p photocraft-engine --example healeval -- <dir of .ppm> [contentAware|proximityMatch|createTexture|healing] [hardness 0..100]
//! Prints the mean error (0..255) left on the blemish ("core") and in the rest of the brushed area
//! ("ring"); DUMP=1 writes damaged | healed | original crops to /tmp.
use photocraft_color::{ColorMode, PixelFormat, SampleType};
use photocraft_doc::{Document, Layer};
use photocraft_engine::Session;
use photocraft_geom::{Rect, Size};
use serde_json::json;

fn read_ppm(path: &str) -> (usize, usize, Vec<f32>) {
    let data = std::fs::read(path).expect("read");
    let mut fields = Vec::new();
    let mut i = 0;
    while fields.len() < 4 {
        while data[i].is_ascii_whitespace() {
            i += 1;
        }
        let s = i;
        while !data[i].is_ascii_whitespace() {
            i += 1;
        }
        fields.push(String::from_utf8_lossy(&data[s..i]).to_string());
    }
    i += 1;
    let (w, h): (usize, usize) = (fields[1].parse().unwrap(), fields[2].parse().unwrap());
    let px = data[i..i + w * h * 3].iter().map(|v| *v as f32 / 255.0).collect();
    (w, h, px)
}

struct Rng(u64);
impl Rng {
    fn f(&mut self) -> f32 {
        self.0 = self.0.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        ((self.0 >> 33) as f32) / (1u64 << 31) as f32
    }
}

/// A blemish: its stroke (points, brush size) and per-pixel damage weight.
struct Case {
    name: &'static str,
    pts: Vec<[f64; 2]>,
    size: f32,
    /// (center x, y, radius) spots or a segment (x0,y0,x1,y1,width)
    spot: Option<(f32, f32, f32)>,
    line: Option<(f32, f32, f32, f32, f32)>,
    color: [f32; 3],
}

fn seg_dist(px: f32, py: f32, l: (f32, f32, f32, f32)) -> f32 {
    let (x0, y0, x1, y1) = l;
    let (dx, dy) = (x1 - x0, y1 - y0);
    let t = (((px - x0) * dx + (py - y0) * dy) / (dx * dx + dy * dy).max(1e-6)).clamp(0.0, 1.0);
    ((px - x0 - t * dx).powi(2) + (py - y0 - t * dy).powi(2)).sqrt()
}

fn damage(c: &Case, x: f32, y: f32) -> f32 {
    if let Some((cx, cy, r)) = c.spot {
        let d = ((x - cx).powi(2) + (y - cy).powi(2)).sqrt();
        return (1.0 - ((d - r * 0.7) / (r * 0.3)).max(0.0)).clamp(0.0, 1.0);
    }
    if let Some((x0, y0, x1, y1, wdt)) = c.line {
        let d = seg_dist(x, y, (x0, y0, x1, y1));
        return (1.0 - (d - wdt * 0.5 + 0.5).max(0.0)).clamp(0.0, 1.0);
    }
    0.0
}

fn cases(w: usize, h: usize, seed: u64) -> Vec<Case> {
    let mut r = Rng(seed);
    let mut out = Vec::new();
    let pos = |r: &mut Rng, m: f32| (m + r.f() * (w as f32 - 2.0 * m), m + r.f() * (h as f32 - 2.0 * m));
    for (name, rad, col) in [("spot5", 5.0, [0.12, 0.08, 0.06]), ("spot9", 9.0, [0.2, 0.12, 0.1]), ("spot14", 14.0, [0.1, 0.1, 0.1]), ("speck4", 4.0, [0.98, 0.98, 0.95])] {
        let (cx, cy) = pos(&mut r, 40.0);
        out.push(Case { name, pts: vec![[cx as f64, cy as f64]], size: rad * 2.0 * 1.5 + 4.0, spot: Some((cx, cy, rad)), line: None, color: col });
    }
    for (name, wdt) in [("wire2", 2.0), ("wire4", 4.0)] {
        let (cx, cy) = pos(&mut r, 60.0);
        let a = r.f() * std::f32::consts::PI;
        let (dx, dy) = (a.cos() * 40.0, a.sin() * 40.0);
        let l = (cx - dx, cy - dy, cx + dx, cy + dy, wdt);
        let n = 40;
        let pts = (0..=n).map(|i| { let t = i as f32 / n as f32; [(l.0 + t * (l.2 - l.0)) as f64, (l.1 + t * (l.3 - l.1)) as f64] }).collect();
        out.push(Case { name, pts, size: wdt * 3.0 + 8.0, spot: None, line: Some(l), color: [0.05, 0.05, 0.05] });
    }
    out
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let dir = &args[1];
    let kind = args.get(2).cloned().unwrap_or_else(|| "contentAware".into());
    let hardness: f32 = args.get(3).and_then(|s| s.parse().ok()).unwrap_or(100.0);
    let mut names: Vec<String> = std::fs::read_dir(dir).unwrap().filter_map(|e| e.ok()?.file_name().into_string().ok()?.strip_suffix(".ppm").map(String::from)).collect();
    names.sort();
    let mut tot: std::collections::BTreeMap<&str, (f32, f32, usize)> = Default::default();
    let t0 = std::time::Instant::now();
    for (ni, n) in names.iter().enumerate() {
        let (w, h, orig) = read_ppm(&format!("{dir}/{n}.ppm"));
        for c in cases(w, h, 1000 + ni as u64) {
            // Damaged image.
            let mut img: Vec<f32> = Vec::with_capacity(w * h * 4);
            let mut core = vec![false; w * h];
            for y in 0..h {
                for x in 0..w {
                    let d = damage(&c, x as f32 + 0.5, y as f32 + 0.5);
                    core[y * w + x] = d > 0.2;
                    let o = &orig[(y * w + x) * 3..];
                    for k in 0..3 {
                        img.push(o[k] * (1.0 - d) + c.color[k] * d);
                    }
                    img.push(1.0);
                }
            }
            let mut doc = Document::new("t", Size::new(w as u32, h as u32), ColorMode::Rgb, SampleType::U8);
            let mut l = Layer::raster("bg", PixelFormat::RGBA8);
            l.surface_mut().unwrap().write_region(Rect::new(0, 0, w as i32, h as i32), &img);
            doc.layers.push(l);
            let mut s = Session::new();
            s.add_document(doc, None);
            let id = s.active().unwrap().doc.layers[0].id;
            s.select_layer(id).unwrap();
            if kind == "healing" {
                // Healing Brush from a clean spot beside the blemish (the user's Alt-click).
                let off = (c.size + 12.0) as f64;
                // Across a wire (not along it, which would sample the wire itself).
                let (ux, uy) = match c.line {
                    Some((x0, y0, x1, y1, _)) => {
                        let (dx, dy) = ((x1 - x0) as f64, (y1 - y0) as f64);
                        let n = (dx * dx + dy * dy).sqrt().max(1e-6);
                        (-dy / n, dx / n)
                    }
                    None => (1.0, 0.0),
                };
                let ok = |sx: f64, sy: f64| c.pts.iter().all(|p| (0.0..w as f64).contains(&(p[0] + sx)) && (0.0..h as f64).contains(&(p[1] + sy)));
                let (dx, dy) = if ok(ux * off, uy * off) { (ux * off, uy * off) } else { (-ux * off, -uy * off) };
                let p = json!({"points": c.pts, "size": c.size, "hardness": hardness, "offset": [dx, dy]});
                s.execute("paint.healingBrush", p).expect("heal");
            } else {
                let p = json!({"points": c.pts, "size": c.size, "hardness": hardness, "type": kind});
                s.execute("paint.spotHealing", p).expect("heal");
            }
            let out = s.active().unwrap().doc.layers[0].surface().unwrap().read_region(Rect::new(0, 0, w as i32, h as i32));
            // Error in the damaged core and in the brushed area (vs the clean original), 0..255.
            let (mut e_core, mut n_core, mut e_ring, mut n_ring) = (0.0f32, 0usize, 0.0f32, 0usize);
            for y in 0..h {
                for x in 0..w {
                    let i = y * w + x;
                    let near = c.pts.iter().any(|p| ((p[0] as f32 - x as f32 - 0.5).powi(2) + (p[1] as f32 - y as f32 - 0.5).powi(2)).sqrt() <= c.size * 0.5);
                    if !near && !core[i] {
                        continue;
                    }
                    let e: f32 = (0..3).map(|k| (out[i * 4 + k] - orig[i * 3 + k]).abs()).sum::<f32>() / 3.0 * 255.0;
                    if core[i] {
                        e_core += e;
                        n_core += 1;
                    } else {
                        e_ring += e;
                        n_ring += 1;
                    }
                }
            }
            let a = tot.entry(c.name).or_default();
            a.0 += e_core / n_core.max(1) as f32;
            a.1 += e_ring / n_ring.max(1) as f32;
            a.2 += 1;
            if std::env::var("DUMP").is_ok() {
                // Damaged | healed | original, cropped around the stroke.
                let (mut x0, mut y0, mut x1, mut y1) = (f64::MAX, f64::MAX, f64::MIN, f64::MIN);
                for p in &c.pts {
                    x0 = x0.min(p[0]);
                    y0 = y0.min(p[1]);
                    x1 = x1.max(p[0]);
                    y1 = y1.max(p[1]);
                }
                let m = c.size as f64 + 24.0;
                let (cx0, cy0) = ((x0 - m).max(0.0) as usize, (y0 - m).max(0.0) as usize);
                let (cx1, cy1) = (((x1 + m) as usize).min(w), ((y1 + m) as usize).min(h));
                let (cw, chh) = (cx1 - cx0, cy1 - cy0);
                let mut ppm = format!("P6\n{} {}\n255\n", cw * 3, chh).into_bytes();
                let b = |v: f32| (v.clamp(0.0, 1.0) * 255.0).round() as u8;
                for y in cy0..cy1 {
                    for x in cx0..cx1 {
                        let i = y * w + x;
                        ppm.extend([b(img[i * 4]), b(img[i * 4 + 1]), b(img[i * 4 + 2])]);
                    }
                    for x in cx0..cx1 {
                        let i = y * w + x;
                        ppm.extend([b(out[i * 4]), b(out[i * 4 + 1]), b(out[i * 4 + 2])]);
                    }
                    for x in cx0..cx1 {
                        let i = y * w + x;
                        ppm.extend([b(orig[i * 3]), b(orig[i * 3 + 1]), b(orig[i * 3 + 2])]);
                    }
                }
                std::fs::write(format!("/tmp/heal-{n}-{}.ppm", c.name), ppm).unwrap();
            }
        }
    }
    let (mut sc, mut sr, mut k) = (0.0, 0.0, 0);
    for (name, (c, r, n)) in &tot {
        println!("{name:8} core {:6.2}  ring {:6.2}", c / *n as f32, r / *n as f32);
        sc += c;
        sr += r;
        k += n;
    }
    println!("ALL      core {:6.2}  ring {:6.2}   ({} cases, {:.1}s)", sc / k as f32, sr / k as f32, k, t0.elapsed().as_secs_f32());
}
