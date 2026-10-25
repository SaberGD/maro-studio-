//! Horix Vectors' Home screen: the shared HORIX Home (horix_home.rs) with Horix Vectors' names,
//! colours, recent files and commands. It replaces the old welcome screen and covers the window
//! below the app bar, as Photoshop's Home does; closing it leaves the empty workspace.

use std::cell::Cell;

use crate::VectorcraftApp;
use crate::horix_home as home;
use serde_json::json;

type Key = (Option<u64>, usize);

thread_local! {
    /// The documents when the person left Home for the workspace: Home stays away while they are
    /// the same, and comes back with the Home button.
    static DISMISSED: Cell<Option<Key>> = const { Cell::new(None) };
}

/// Is Home up?
pub fn showing(app: &mut VectorcraftApp) -> bool {
    let key = crate::menus::home_key(app);
    // A document that opened, closed or became active since Home was chosen replaces it.
    if app.ui.home.is_some_and(|k| k != key) {
        app.ui.home = None;
    }
    if DISMISSED.get().is_some_and(|d| d != key) {
        DISMISSED.set(None);
    }
    crate::menus::home_showing(app) && DISMISSED.get() != Some(key)
}

/// The Home button: Home over the documents (or the empty workspace), or back to them.
pub fn toggle(app: &mut VectorcraftApp) {
    let key = crate::menus::home_key(app);
    if showing(app) {
        app.ui.home = None;
        DISMISSED.set(Some(key));
    } else {
        DISMISSED.set(None);
        app.ui.home = Some(key);
    }
}

fn palette(ctx: &egui::Context) -> home::Palette {
    let t = crate::theme::Tokens::get(ctx);
    home::Palette {
        background: t.panel_darker,
        chrome: t.app_bar,
        card: t.panel,
        card_hover: t.hover,
        border: t.border,
        text: t.text,
        text_strong: t.text_strong,
        text_dim: t.text_dim,
        accent: t.accent,
        accent_strong: t.accent_strong,
    }
}

const FEATURES: &[home::Feature<'static>] = &[
    home::Feature { mark: "Pen", title: "Draw with precision", text: "Pen, shape builder, live corners and blends for logos and icons." },
    home::Feature { mark: "Aa", title: "Type, including Arabic", text: "Area and path type, variable fonts, and Arabic text that joins right." },
    home::Feature { mark: "AI", title: "Open your files", text: "Illustrator .ai, EPS, PDF and SVG in; SVG, PDF and PNG out." },
];

pub fn show(app: &mut VectorcraftApp, ui: &mut egui::Ui) {
    let ctx = ui.ctx().clone();
    let paths: Vec<String> = if cfg!(target_arch = "wasm32") { Vec::new() } else { crate::io::recent_files(app).iter().take(12).cloned().collect() };
    let recent: Vec<home::Recent> = paths
        .iter()
        .map(|p| {
            let path = std::path::Path::new(p);
            let name = path.file_name().map(|n| n.to_string_lossy().to_string()).unwrap_or_else(|| p.clone());
            let folder = path.parent().map(|d| d.display().to_string()).unwrap_or_default();
            home::Recent::new(name, folder)
        })
        .collect();
    let logo = egui::Image::from_texture(egui::load::SizedTexture::new(crate::brand::texture(&ctx).id(), egui::vec2(30.0, 30.0)));
    let screen = home::Home {
        id: "horix-vectors",
        name: "Horix Vectors",
        tagline: "The vector studio",
        version: "v@HORIX_APP_VERSION@",
        logo: Some(logo),
        paint_logo: None,
        new_label: "New file",
        open_label: "Open",
        features: FEATURES,
        recent: &recent,
        palette: palette(&ctx),
        web: cfg!(target_arch = "wasm32"),
    };
    match home::show(ui, &screen) {
        Some(home::Action::New | home::Action::Feature(_)) => {
            app.run("file.newDialog", json!({})).ok();
        }
        Some(home::Action::Open) => {
            app.run("file.open", json!({})).ok();
        }
        Some(home::Action::OpenRecent(i)) => {
            if let Some(path) = paths.get(i) {
                let _ = crate::io::open_recent_reporting(app, path);
            }
        }
        Some(home::Action::Workspace) => {
            app.ui.home = None;
            DISMISSED.set(Some(crate::menus::home_key(app)));
        }
        Some(home::Action::Url(url)) => app.open_url(&url),
        None => {}
    }
}
