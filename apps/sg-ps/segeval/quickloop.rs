//! Quick Selection with simulated corrections (largest error component, deepest pixel): IoU after
//! the stroke and after 1..3 Shift / Alt corrections. Reads cNNN.ppm / .pgm / .json.
use photocraft_algo::segment::{ImageSampler, RgbImage, quick};
use photocraft_geom::Rect;

fn pnm(path: &str) -> (usize, usize, Vec<u8>) {
    let d = std::fs::read(path).unwrap();
    let mut f = Vec::new();
    let mut i = 0;
    while f.len() < 4 {
        while d[i].is_ascii_whitespace() { i += 1; }
        let s = i;
        while !d[i].is_ascii_whitespace() { i += 1; }
        f.push(String::from_utf8_lossy(&d[s..i]).to_string());
    }
    i += 1;
    (f[1].parse().unwrap(), f[2].parse().unwrap(), d[i..].to_vec())
}

fn label(m: &[bool], w: usize, h: usize) -> Vec<Vec<usize>> {
    let mut seen = vec![false; w * h];
    let mut out = Vec::new();
    for s in 0..w * h {
        if !m[s] || seen[s] { continue; }
        let mut c = vec![s];
        seen[s] = true;
        let mut k = 0;
        while k < c.len() {
            let i = c[k]; k += 1;
            let (x, y) = (i % w, i / w);
            for (nx, ny) in [(x.wrapping_sub(1), y), (x + 1, y), (x, y.wrapping_sub(1)), (x, y + 1)] {
                if nx < w && ny < h && m[ny * w + nx] && !seen[ny * w + nx] { seen[ny * w + nx] = true; c.push(ny * w + nx); }
            }
        }
        out.push(c);
    }
    out
}

/// Deepest pixel of a component (chamfer distance to its outside).
fn deepest(c: &[usize], w: usize, h: usize) -> usize {
    let mut inside = vec![false; w * h];
    for i in c { inside[*i] = true; }
    let mut d: Vec<f32> = inside.iter().map(|v| if *v { 1e9 } else { 0.0 }).collect();
    for _ in 0..2 {
        for y in 0..h { for x in 0..w { let i = y * w + x; if x > 0 { d[i] = d[i].min(d[i - 1] + 1.0); } if y > 0 { d[i] = d[i].min(d[i - w] + 1.0); } } }
        for y in (0..h).rev() { for x in (0..w).rev() { let i = y * w + x; if x + 1 < w { d[i] = d[i].min(d[i + 1] + 1.0); } if y + 1 < h { d[i] = d[i].min(d[i + w] + 1.0); } } }
    }
    *c.iter().max_by(|a, b| d[**a].total_cmp(&d[**b])).unwrap()
}

fn iou(a: &[bool], b: &[bool]) -> f32 {
    a.iter().zip(b).filter(|(x, y)| **x && **y).count() as f32 / a.iter().zip(b).filter(|(x, y)| **x || **y).count().max(1) as f32
}

fn main() {
    let dir = std::env::args().nth(1).unwrap();
    let mut names: Vec<String> = std::fs::read_dir(&dir).unwrap().filter_map(|e| e.ok()?.file_name().into_string().ok()?.strip_suffix(".json").map(String::from)).collect();
    names.sort();
    let mut tot = [0.0f32; 4];
    for n in &names {
        let (w, h, rgb) = pnm(&format!("{dir}/{n}.ppm"));
        let (_, _, g) = pnm(&format!("{dir}/{n}.pgm"));
        let gt: Vec<bool> = g.iter().map(|v| *v > 127).collect();
        let meta: serde_json::Value = serde_json::from_str(&std::fs::read_to_string(format!("{dir}/{n}.json")).unwrap()).unwrap();
        let size = meta["size"].as_f64().unwrap() as f32;
        let pts: Vec<(f32, f32)> = meta["pts"].as_array().unwrap().iter().map(|p| (p[0].as_f64().unwrap() as f32, p[1].as_f64().unwrap() as f32)).collect();
        let img = RgbImage::from_fn(w, h, |x, y| { let p = &rgb[(y * w + x) * 3..]; [p[0] as f32 / 255.0, p[1] as f32 / 255.0, p[2] as f32 / 255.0] });
        let smp = ImageSampler { img: &img, origin: (0, 0) };
        let canvas = Rect::new(0, 0, w as i32, h as i32);
        let mut sel = vec![false; w * h];
        let apply = |sel: &mut Vec<bool>, pts: &[(f32, f32)], size: f32, on: bool| {
            if let Some(r) = quick::quick_select(&smp, canvas, pts, size, quick::WORK_PX) {
                for y in r.bbox.y0..r.bbox.y1 { for x in r.bbox.x0..r.bbox.x1 { if r.at(x, y) >= 0.5 { sel[y as usize * w + x as usize] = on; } } }
            }
        };
        apply(&mut sel, &pts, size, true);
        let mut res = vec![iou(&sel, &gt)];
        for _ in 0..3 {
            let fp: Vec<bool> = sel.iter().zip(&gt).map(|(s, g)| *s && !*g).collect();
            let fnn: Vec<bool> = sel.iter().zip(&gt).map(|(s, g)| !*s && *g).collect();
            let a = label(&fp, w, h).into_iter().max_by_key(|c| c.len());
            let b = label(&fnn, w, h).into_iter().max_by_key(|c| c.len());
            let (c, add) = match (a, b) {
                (Some(a), Some(b)) => if a.len() >= b.len() { (a, false) } else { (b, true) },
                (Some(a), None) => (a, false),
                (None, Some(b)) => (b, true),
                _ => break,
            };
            if c.len() < 50 { break; }
            let p = deepest(&c, w, h);
            let pt = ((p % w) as f32 + 0.5, (p / w) as f32 + 0.5);
            apply(&mut sel, &[pt], (size * 0.6).max(6.0), add);
            res.push(iou(&sel, &gt));
        }
        while res.len() < 4 { let l = *res.last().unwrap(); res.push(l); }
        for k in 0..4 { tot[k] += res[k]; }
        println!("{n} {:.3} {:.3} {:.3} {:.3}", res[0], res[1], res[2], res[3]);
    }
    let k = names.len() as f32;
    println!("current mean IoU after stroke, +1, +2, +3 corrections: {:.3} {:.3} {:.3} {:.3}", tot[0] / k, tot[1] / k, tot[2] / k, tot[3] / k);
}
