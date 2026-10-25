//! HORIX's Home screen: the shared HORIX Home (horix_home.rs) with HORIX's names,
//! recent files and commands. It replaces the old start card and covers the whole window below
//! the title bar, as Photoshop's Home does; closing it leaves the empty workspace.

use crate::PhotocraftApp;
use crate::horix_home as home;
use serde_json::json;

/// The document count when the person left Home for the empty workspace: Home stays away while
/// the documents are the same, and comes back with the Home button.
fn dismissed_id() -> egui::Id {
    egui::Id::new("horix-home-dismissed")
}

/// Is Home up?
pub fn showing(app: &mut PhotocraftApp, ctx: &egui::Context) -> bool {
    if !app.jobs.opens.is_empty() {
        return false;
    }
    let n = app.session.documents().len();
    let auto = app.session.prefs().general.auto_show_home_screen;
    let base = app.ui.chrome.shows_home(n, auto);
    let dismissed: Option<usize> = ctx.data(|d| d.get_temp(dismissed_id()));
    if dismissed.is_some_and(|d| d != n) {
        ctx.data_mut(|d| d.remove::<usize>(dismissed_id()));
        return base;
    }
    base && dismissed != Some(n)
}

/// The Home button: Home over the documents (or the empty workspace), or back to them.
pub fn toggle(app: &mut PhotocraftApp, ctx: &egui::Context) {
    let n = app.session.documents().len();
    if showing(app, ctx) {
        leave(app, ctx);
    } else {
        ctx.data_mut(|d| d.remove::<usize>(dismissed_id()));
        app.ui.chrome.home = Some(n);
    }
}

fn leave(app: &mut PhotocraftApp, ctx: &egui::Context) {
    let n = app.session.documents().len();
    app.ui.chrome.home = None;
    ctx.data_mut(|d| d.insert_temp(dismissed_id(), n));
}

const TOOLS: &[home::Tool<'static>] = &[
    home::Tool { icon: home::Icon::Masks, title: "Select with AI", text: "Subject, object and background masks." },
    home::Tool { icon: home::Icon::Layers, title: "Layered documents", text: "Layers, masks and smart objects." },
    home::Tool { icon: home::Icon::Brush, title: "Retouch & filters", text: "Healing, Camera Raw and color." },
];

pub fn show(app: &mut PhotocraftApp, ui: &mut egui::Ui) {
    let ctx = ui.ctx().clone();
    let paths: Vec<String> = if cfg!(target_arch = "wasm32") || !app.session.prefs().interface.show_home_recent_files {
        Vec::new()
    } else {
        app.ui.recent_files.iter().take(12).cloned().collect()
    };
    let recent: Vec<home::Recent> = paths
        .iter()
        .map(|p| {
            let folder = std::path::Path::new(p).parent().map(|d| d.display().to_string()).unwrap_or_default();
            let mut r = home::Recent::new(crate::file_open::display_name(p), folder);
            if !matches!(r.badge.as_str(), "PSD" | "PSB" | "PCRAFT" | "") {
                r.kind = "Image document".into();
            }
            #[cfg(not(target_arch = "wasm32"))]
            if let Some((tex, aspect)) = thumbnails::get(&ctx, p) {
                r.thumbnail = Some(tex);
                r.aspect = aspect;
                r.fill = true;
            }
            r
        })
        .collect();
    let shortcut = crate::shortcuts::shortcut_label(app, "file.new").unwrap_or_default().replace('+', " ");
    let version = format!("v{}", photocraft_engine::build_info::horix_version());
    let screen = home::Home {
        id: "horix",
        name: "HORIX",
        version: &version,
        headline: "Your next idea starts here.",
        kicker: "THE VISIONARY AI EDITOR",
        drop_title: "Drop an image or PSD to get started",
        drop_icon: home::Icon::Image,
        formats: "PSD / PSB / JPG / PNG / WEBP",
        new_label: "New file",
        open_label: "Open file",
        new_shortcut: &shortcut,
        recent_title: "Recent projects",
        recent: &recent,
        tools: TOOLS,
        web: cfg!(target_arch = "wasm32"),
    };
    match home::show(ui, &screen) {
        Some(home::Action::New | home::Action::Tool(_)) => {
            let _ = crate::menus::invoke(app, &ctx, "file.new", json!({}));
        }
        Some(home::Action::Open) => {
            let _ = app.open_dialog_file();
        }
        Some(home::Action::OpenRecent(i)) => {
            if let Some(path) = paths.get(i).cloned()
                && let Err(e) = app.open_path(&path)
            {
                app.open_failed(&crate::file_open::display_name(&path), &e);
            }
        }
        Some(home::Action::Workspace) => leave(app, &ctx),
        Some(home::Action::Url(url)) => {
            crate::links::open(app, &ctx, &url);
        }
        None => {}
    }
}

/// Pictures of the recent files, made once a session on a thread of their own (opening a large
/// PSD takes a while) and kept as textures.
#[cfg(not(target_arch = "wasm32"))]
mod thumbnails {
    use std::collections::HashMap;
    use std::sync::{Arc, Mutex};

    /// Larger files go without a picture.
    const MAX_BYTES: u64 = 400 << 20;
    const SIDE: u32 = 480;

    enum Slot {
        Making,
        Made(egui::ColorImage),
        Shown(egui::TextureHandle),
        None,
    }

    type Cache = Arc<Mutex<HashMap<String, Slot>>>;

    pub fn get(ctx: &egui::Context, path: &str) -> Option<(egui::TextureId, f32)> {
        let id = egui::Id::new("horix-home-thumbnails");
        let cache: Cache = ctx.data_mut(|d| d.get_temp_mut_or_default::<Cache>(id).clone());
        let mut slots = cache.lock().ok()?;
        match slots.remove(path) {
            None => {
                slots.insert(path.to_owned(), Slot::Making);
                let (cache, ctx, path) = (cache.clone(), ctx.clone(), path.to_owned());
                std::thread::spawn(move || {
                    let slot = make(&path).map_or(Slot::None, Slot::Made);
                    if let Ok(mut slots) = cache.lock() {
                        slots.insert(path, slot);
                    }
                    ctx.request_repaint();
                });
                None
            }
            Some(Slot::Made(image)) => {
                let tex = ctx.load_texture(format!("horix-home-{path}"), image, egui::TextureOptions::LINEAR);
                let shown = shown(&tex);
                slots.insert(path.to_owned(), Slot::Shown(tex));
                Some(shown)
            }
            Some(Slot::Shown(tex)) => {
                let shown = shown(&tex);
                slots.insert(path.to_owned(), Slot::Shown(tex));
                Some(shown)
            }
            Some(slot) => {
                slots.insert(path.to_owned(), slot);
                None
            }
        }
    }

    fn shown(tex: &egui::TextureHandle) -> (egui::TextureId, f32) {
        let [w, h] = tex.size();
        (tex.id(), w as f32 / h.max(1) as f32)
    }

    fn make(path: &str) -> Option<egui::ColorImage> {
        if std::fs::metadata(path).ok()?.len() > MAX_BYTES {
            return None;
        }
        let bytes = std::fs::read(path).ok()?;
        let doc = photocraft_io::import(path, &bytes).ok()?.document;
        let img = photocraft_compose::thumbnail(&doc, SIDE);
        Some(egui::ColorImage::from_rgba_unmultiplied([img.width as usize, img.height as usize], &img.pixels))
    }
}
