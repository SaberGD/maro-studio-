//! SG - PS evaluation harness: Select Subject and Quick Selection against ground-truth masks.
//! Usage: cargo run --release -p photocraft-algo --example segeval -- <dir>
use std::time::Instant;

use photocraft_algo::segment::{ImageSampler, RgbImage, quick, subject};
use photocraft_geom::Rect;

fn read_pnm(path: &str) -> (usize, usize, usize, Vec<u8>) {
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
    let ch = if fields[0] == "P6" { 3 } else { 1 };
    (fields[1].parse().unwrap(), fields[2].parse().unwrap(), ch, data[i..].to_vec())
}

fn iou(mask: &[f32], gt: &[u8]) -> f32 {
    let (mut inter, mut uni) = (0usize, 0usize);
    for (m, g) in mask.iter().zip(gt) {
        let (a, b) = (*m >= 0.5, *g >= 128);
        if a && b { inter += 1; }
        if a || b { uni += 1; }
    }
    inter as f32 / uni.max(1) as f32
}

fn main() {
    let dir = std::env::args().nth(1).expect("dir");
    let mut names: Vec<String> = std::fs::read_dir(&dir).unwrap().filter_map(|e| {
        let n = e.ok()?.file_name().into_string().ok()?;
        n.strip_suffix(".ppm").map(String::from)
    }).collect();
    names.sort();
    let (mut s_sum, mut q_sum, mut s_ms, mut q_ms) = (0.0, 0.0, 0u128, 0u128);
    for n in &names {
        let (w, h, _, rgb) = read_pnm(&format!("{dir}/{n}.ppm"));
        let (_, _, _, gt) = read_pnm(&format!("{dir}/{n}.pgm"));
        let img = RgbImage::from_fn(w, h, |x, y| {
            let p = &rgb[(y * w + x) * 3..];
            [p[0] as f32 / 255.0, p[1] as f32 / 255.0, p[2] as f32 / 255.0]
        });
        let sampler = ImageSampler { img: &img, origin: (0, 0) };
        let canvas = Rect::new(0, 0, w as i32, h as i32);
        let to_full = |r: Option<photocraft_algo::segment::Region>| -> Vec<f32> {
            let mut out = vec![0.0; w * h];
            if let Some(r) = r {
                for y in 0..h { for x in 0..w { out[y * w + x] = r.at(x as i32, y as i32); } }
            }
            out
        };
        let t = Instant::now();
        let s = to_full(subject::select_subject(&sampler, canvas));
        let sms = t.elapsed().as_millis();
        // Quick Selection: one stroke down the middle of the subject, like a user would brush.
        let (mut xs, mut ys, mut c) = (0f32, Vec::new(), 0f32);
        for y in 0..h { for x in 0..w { if gt[y * w + x] >= 128 { xs += x as f32; c += 1.0; ys.push(y); } } }
        let cx = xs / c;
        let (y0, y1) = (*ys.iter().min().unwrap() as f32, *ys.iter().max().unwrap() as f32);
        // Keep only stroke points whose whole brush disc (radius 30) is on the subject.
        let inside = |px: f32, py: f32| (-30i32..=30).step_by(10).all(|dy| (-30i32..=30).step_by(10).all(|dx| {
            let (x, y) = (px as i32 + dx, py as i32 + dy);
            x >= 0 && y >= 0 && (x as usize) < w && (y as usize) < h && gt[y as usize * w + x as usize] >= 128
        }));
        let pts: Vec<(f32, f32)> = (0..40).map(|k| (cx, y0 + (y1 - y0) * (0.1 + 0.8 * k as f32 / 39.0))).filter(|p| inside(p.0, p.1)).collect();
        let t = Instant::now();
        let q = to_full(quick::quick_select(&sampler, canvas, &pts, 60.0, quick::WORK_PX));
        let qms = t.elapsed().as_millis();
        let (si, qi) = (iou(&s, &gt), iou(&q, &gt));
        let (qin, qall) = q.iter().zip(&gt).fold((0usize, 0usize), |(a, b), (m, g)| if *m >= 0.5 { (a + (*g >= 128) as usize, b + 1) } else { (a, b) });
        let qprec = qin as f32 / qall.max(1) as f32;
        println!("{n:20} subject IoU {si:.3} ({sms} ms)   quick IoU {qi:.3} prec {qprec:.3} ({qms} ms)");
        let out: Vec<u8> = s.iter().map(|v| (v * 255.0) as u8).collect();
        let mut f = format!("P5\n{w} {h}\n255\n").into_bytes();
        f.extend(out);
        std::fs::write(format!("{dir}/out_{n}.pgm"), f).unwrap();
        s_sum += si; q_sum += qi; s_ms += sms; q_ms += qms;
    }
    let k = names.len() as f32;
    println!("MEAN subject IoU {:.3} ({} ms avg)   quick IoU {:.3} ({} ms avg)", s_sum / k, s_ms / names.len() as u128, q_sum / k, q_ms / names.len() as u128);
}
