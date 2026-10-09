//! SG - PS: Select Subject IoU and edge alpha error against soft ground-truth alpha.
//! Usage: cargo run --release -p photocraft-algo --example subjeval -- <dir> [name filter]
//! <dir> holds <name>.ppm images with <name>.pgm alpha; masks go to <dir>/../out/.
use std::time::Instant;
use photocraft_algo::segment::{ImageSampler, RgbImage, subject};
use photocraft_geom::Rect;

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

fn main() {
    let dir = std::env::args().nth(1).expect("dir");
    let only = std::env::args().nth(2);
    let mut names: Vec<String> = std::fs::read_dir(&dir).unwrap().filter_map(|e| {
        let n = e.ok()?.file_name().into_string().ok()?;
        n.strip_suffix(".ppm").map(String::from)
    }).filter(|n| only.as_ref().is_none_or(|o| n.contains(o.as_str()))).collect();
    names.sort();
    let (mut si, mut se, mut sm, mut k) = (0.0, 0.0, 0u128, 0.0);
    for n in &names {
        let (w, h, rgb) = read_pnm(&format!("{dir}/{n}.ppm"));
        let (_, _, gt) = read_pnm(&format!("{dir}/{n}.pgm"));
        let img = RgbImage::from_fn(w, h, |x, y| { let p = &rgb[(y * w + x) * 3..]; [p[0] as f32 / 255.0, p[1] as f32 / 255.0, p[2] as f32 / 255.0] });
        let sampler = ImageSampler { img: &img, origin: (0, 0) };
        let t = Instant::now();
        let r = subject::select_subject(&sampler, Rect::new(0, 0, w as i32, h as i32));
        let ms = t.elapsed().as_millis();
        let mut m = vec![0f32; w * h];
        if let Some(r) = r { for y in 0..h { for x in 0..w { m[y * w + x] = r.at(x as i32, y as i32); } } }
        let (mut inter, mut uni) = (0usize, 0usize);
        for (a, g) in m.iter().zip(&gt) { let (a, b) = (*a >= 0.5, *g >= 128); inter += (a && b) as usize; uni += (a || b) as usize; }
        let iou = inter as f32 / uni.max(1) as f32;
        // Edge band: within 4 px of a ground-truth boundary (alpha crossing 128) or partial alpha.
        let hard: Vec<bool> = gt.iter().map(|g| *g >= 128).collect();
        let (mut e, mut c) = (0f64, 0f64);
        for y in 0..h { for x in 0..w {
            let i = y * w + x;
            let mut band = gt[i] > 8 && gt[i] < 247;
            if !band { 'o: for dy in -4i32..=4 { for dx in -4i32..=4 {
                let (nx, ny) = (x as i32 + dx, y as i32 + dy);
                if nx >= 0 && ny >= 0 && (nx as usize) < w && (ny as usize) < h && hard[ny as usize * w + nx as usize] != hard[i] { band = true; break 'o; }
            } } }
            if band { e += (m[i] - gt[i] as f32 / 255.0).abs() as f64; c += 1.0; }
        } }
        let edge = (e / c.max(1.0)) as f32;
        println!("{n:20} IoU {iou:.4}  edgeMAE {edge:.4}  ({ms} ms)");
        let out: Vec<u8> = m.iter().map(|v| (v * 255.0).round() as u8).collect();
        let mut f = format!("P5\n{w} {h}\n255\n").into_bytes();
        f.extend(out);
        std::fs::write(format!("{dir}/../out/{n}.pgm"), f).unwrap();
        si += iou; se += edge; sm += ms; k += 1.0;
    }
    println!("MEAN IoU {:.4}  edgeMAE {:.4}  ({} ms avg)", si / k, se / k, sm / k as u128);
}
