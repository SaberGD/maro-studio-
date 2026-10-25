//! HORIX One for Windows and macOS: one window with the persona bar and its personas, Vector and
//! Pixel. It is the HORIX One web build (apps/horix-one/build.sh) served from the app's own folder
//! to the system web view (WebView2 on Windows, WKWebView on macOS), so the desktop and the web
//! are the same app. Nothing is fetched from horix.live; the AI runtime still comes from its CDN
//! the first time (the browser keeps it).
//!
//! The site is served on a custom scheme (`https://horixone.localhost/` on Windows,
//! `horixone://localhost/` on macOS), a secure context, so WebGPU and the clipboard work. Saving
//! asks where with the system's save dialog; links to other sites open in the default browser.

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::borrow::Cow;
use std::path::{Path, PathBuf};

use tao::dpi::LogicalSize;
use tao::event::{Event, WindowEvent};
use tao::event_loop::{ControlFlow, EventLoop};
use tao::window::{Icon, WindowBuilder};
use wry::http::{Request, Response, StatusCode, header};
use wry::{NewWindowResponse, WebContext, WebViewBuilder};

const SCHEME: &str = "horixone";
const ICON: &[u8] = include_bytes!("../../assets/app-icon/icon-256.png");

/// Where the start page is, as the web view addresses the custom scheme.
fn start_url() -> &'static str {
    if cfg!(windows) { "https://horixone.localhost/" } else { "horixone://localhost/" }
}

/// The HORIX One site shipped with the app: `site/` beside the exe (Windows), the bundle's
/// Resources (macOS), or `HORIX_ONE_SITE` (development).
fn site_dir() -> Option<PathBuf> {
    if let Some(dir) = std::env::var_os("HORIX_ONE_SITE") {
        return Some(PathBuf::from(dir));
    }
    let exe = std::env::current_exe().ok()?;
    let dir = exe.parent()?;
    [dir.join("site"), dir.join("../Resources/site")].into_iter().find(|d| d.join("index.html").is_file())
}

fn mime(path: &Path) -> &'static str {
    match path.extension().and_then(|e| e.to_str()).unwrap_or_default().to_ascii_lowercase().as_str() {
        "html" => "text/html; charset=utf-8",
        "js" | "mjs" => "text/javascript; charset=utf-8",
        "wasm" => "application/wasm",
        "css" => "text/css; charset=utf-8",
        "json" => "application/json",
        "svg" => "image/svg+xml",
        "png" => "image/png",
        "jpg" | "jpeg" => "image/jpeg",
        "webp" => "image/webp",
        "woff2" => "font/woff2",
        "ttf" => "font/ttf",
        "otf" => "font/otf",
        "txt" => "text/plain; charset=utf-8",
        _ => "application/octet-stream",
    }
}

/// The file `request` names inside `root`, or `None` for anything outside it (`..`, links out).
fn resolve(root: &Path, request: &Request<Vec<u8>>) -> Option<PathBuf> {
    let raw = request.uri().path();
    let decoded = percent_decode(raw)?;
    let rel = decoded.trim_start_matches('/');
    if rel.split('/').any(|part| part == ".." || part.contains('\\') || part.contains(':')) {
        return None;
    }
    let mut path = root.join(rel);
    if path.is_dir() || rel.is_empty() || rel.ends_with('/') {
        path = path.join("index.html");
    }
    let root = root.canonicalize().ok()?;
    let path = path.canonicalize().ok()?;
    path.starts_with(&root).then_some(path)
}

fn percent_decode(s: &str) -> Option<String> {
    let b = s.as_bytes();
    let mut out = Vec::with_capacity(b.len());
    let mut i = 0;
    while i < b.len() {
        if b[i] == b'%' {
            let hex = std::str::from_utf8(b.get(i + 1..i + 3)?).ok()?;
            out.push(u8::from_str_radix(hex, 16).ok()?);
            i += 3;
        } else {
            out.push(b[i]);
            i += 1;
        }
    }
    String::from_utf8(out).ok()
}

fn serve(root: &Path, request: &Request<Vec<u8>>) -> Response<Cow<'static, [u8]>> {
    let reply = |status: StatusCode, kind: &str, body: Vec<u8>| {
        Response::builder()
            .status(status)
            .header(header::CONTENT_TYPE, kind)
            .header(header::CACHE_CONTROL, "no-cache")
            .header("X-Content-Type-Options", "nosniff")
            .body(Cow::Owned(body))
            .unwrap_or_else(|_| Response::new(Cow::Borrowed(&[][..])))
    };
    match resolve(root, request).map(|p| (std::fs::read(&p), p)) {
        Some((Ok(bytes), path)) => reply(StatusCode::OK, mime(&path), bytes),
        _ => reply(StatusCode::NOT_FOUND, "text/plain; charset=utf-8", b"not found".to_vec()),
    }
}

/// Only the app's own pages load in the window; anything else opens in the default browser.
fn is_own(url: &str) -> bool {
    url.starts_with(start_url()) || url.starts_with("about:") || url.starts_with("blob:") || url.starts_with("data:")
}

fn open_outside(url: &str) {
    if url.starts_with("https://") || url.starts_with("http://") || url.starts_with("mailto:") {
        let _ = open::that_detached(url);
    }
}

fn fail(message: &str) -> ! {
    eprintln!("HORIX One: {message}");
    rfd::MessageDialog::new().set_title("HORIX One").set_description(message).set_level(rfd::MessageLevel::Error).show();
    std::process::exit(1);
}

fn main() {
    let Some(root) = site_dir() else { fail("HORIX One's files are missing. Install it again from HORIX Launcher.") };
    let event_loop = EventLoop::new();
    let icon = image::load_from_memory(ICON).ok().map(|i| i.into_rgba8()).and_then(|i| {
        let (w, h) = i.dimensions();
        Icon::from_rgba(i.into_raw(), w, h).ok()
    });
    let window = match WindowBuilder::new()
        .with_title("HORIX One")
        .with_inner_size(LogicalSize::new(1440.0, 900.0))
        .with_min_inner_size(LogicalSize::new(900.0, 600.0))
        .with_window_icon(icon)
        .build(&event_loop)
    {
        Ok(w) => w,
        Err(e) => fail(&format!("HORIX One couldn't open its window: {e}")),
    };
    window.set_maximized(true);
    // The web view's storage (preferences, brushes, the AI models it downloaded) in the user's
    // data folder, not beside the exe.
    let data = dirs::data_local_dir().map(|d| d.join("HORIX One").join("WebView"));
    let mut context = WebContext::new(data);
    let builder = WebViewBuilder::new_with_web_context(&mut context)
        .with_custom_protocol(SCHEME.into(), move |_id, request| serve(&root, &request))
        .with_url(start_url())
        .with_devtools(cfg!(debug_assertions))
        .with_background_color((14, 14, 15, 255))
        .with_navigation_handler(|url| {
            if is_own(&url) {
                return true;
            }
            open_outside(&url);
            false
        })
        .with_new_window_req_handler(|url, _features| {
            open_outside(&url);
            NewWindowResponse::Deny
        })
        // A download (Save, Export) asks where to save it, as the desktop apps do.
        .with_download_started_handler(|url, path| {
            let suggested = path.file_name().map(|n| n.to_string_lossy().to_string()).filter(|n| !n.is_empty()).unwrap_or_else(|| {
                url.rsplit('/').next().filter(|n| !n.is_empty() && !n.contains(':')).unwrap_or("HORIX One export").to_string()
            });
            let mut dialog = rfd::FileDialog::new().set_title("Save").set_file_name(&suggested);
            if let Some(dir) = dirs::document_dir().or_else(dirs::download_dir) {
                dialog = dialog.set_directory(dir);
            }
            match dialog.save_file() {
                Some(chosen) => {
                    *path = chosen;
                    true
                }
                None => false,
            }
        });
    #[cfg(windows)]
    let builder = {
        use wry::WebViewBuilderExtWindows;
        builder.with_https_scheme(true)
    };
    // (Linux is not shipped; it runs here for testing, inside the window's GTK box.)
    #[cfg(target_os = "linux")]
    let built = {
        use tao::platform::unix::WindowExtUnix;
        use wry::WebViewBuilderExtUnix;
        builder.build_gtk(window.default_vbox().expect("tao's default vbox"))
    };
    #[cfg(not(target_os = "linux"))]
    let built = builder.build(&window);
    let webview = match built {
        Ok(v) => v,
        Err(e) => fail(&format!(
            "HORIX One needs the system web view (Microsoft Edge WebView2 on Windows), and it couldn't start: {e}\n\nOn Windows, install \"WebView2 Runtime\" from Microsoft and open HORIX One again."
        )),
    };
    event_loop.run(move |event, _, control_flow| {
        *control_flow = ControlFlow::Wait;
        let _ = &webview;
        if let Event::WindowEvent { event: WindowEvent::CloseRequested, .. } = event {
            *control_flow = ControlFlow::Exit;
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    fn req(path: &str) -> Request<Vec<u8>> {
        Request::builder().uri(format!("{}{}", start_url().trim_end_matches('/'), path)).body(Vec::new()).unwrap()
    }

    #[test]
    fn serves_only_inside_the_site() {
        let root = std::env::temp_dir().join(format!("horix-one-site-{}", std::process::id()));
        std::fs::create_dir_all(root.join("pixel")).unwrap();
        std::fs::write(root.join("index.html"), "<p>one").unwrap();
        std::fs::write(root.join("pixel/index.html"), "<p>pixel").unwrap();
        std::fs::write(root.join("pixel/sg-ps_bg.wasm"), b"\0asm").unwrap();
        std::fs::write(root.parent().unwrap().join("secret.txt"), "no").unwrap();
        assert_eq!(resolve(&root, &req("/")).unwrap(), root.join("index.html").canonicalize().unwrap());
        assert_eq!(resolve(&root, &req("/pixel/")).unwrap(), root.join("pixel/index.html").canonicalize().unwrap());
        assert_eq!(resolve(&root, &req("/pixel")).unwrap(), root.join("pixel/index.html").canonicalize().unwrap());
        assert!(resolve(&root, &req("/../secret.txt")).is_none());
        assert!(resolve(&root, &req("/%2e%2e/secret.txt")).is_none());
        assert!(resolve(&root, &req("/nope.js")).is_none());
        let r = serve(&root, &req("/pixel/sg-ps_bg.wasm"));
        assert_eq!(r.status(), StatusCode::OK);
        assert_eq!(r.headers()[header::CONTENT_TYPE], "application/wasm");
        assert_eq!(serve(&root, &req("/missing")).status(), StatusCode::NOT_FOUND);
        std::fs::remove_dir_all(&root).unwrap();
    }

    #[test]
    fn other_sites_open_outside() {
        assert!(is_own(start_url()));
        assert!(is_own(&format!("{}pixel/", start_url())));
        assert!(!is_own("https://horix.si/"));
        assert!(!is_own("https://wa.me/201103221873"));
    }
}
