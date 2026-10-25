//! HORIX's Home screen: the shared HORIX Home (horix_home.rs) with HORIX's names, colours,
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

fn palette(ctx: &egui::Context) -> home::Palette {
    let t = crate::theme::Tokens::get(ctx);
    home::Palette {
        background: t.canvas,
        chrome: t.chrome,
        card: t.card,
        card_hover: t.hover,
        border: t.card_border,
        text: t.text,
        text_strong: t.text,
        text_dim: t.text_dim,
        accent: egui::Color32::from_rgb(0xea, 0x99, 0x3f),
        accent_strong: egui::Color32::from_rgb(0xd6, 0x3c, 0x32),
    }
}

const FEATURES: &[home::Feature<'static>] = &[
    home::Feature { mark: "AI", title: "Select with AI", text: "Select Subject, Object Selection and Remove Background, on your own computer." },
    home::Feature { mark: "PSD", title: "Real layered files", text: "PSD and PSB with layers, masks, smart objects and adjustment layers." },
    home::Feature { mark: "Fx", title: "Retouch and filters", text: "Healing, clone, Camera Raw, Liquify and hundreds of filters." },
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
            home::Recent::new(crate::file_open::display_name(p), folder)
        })
        .collect();
    let new_label = crate::shortcuts::command_label(app, "New file", "file.new");
    let open_label = crate::shortcuts::command_label(app, "Open", "file.open");
    let version = format!("v{}", photocraft_engine::build_info::horix_version());
    let screen = home::Home {
        id: "horix",
        name: "HORIX",
        tagline: "The visionary AI editor",
        version: &version,
        logo: Some(crate::links::logo(30.0)),
        paint_logo: None,
        new_label: &new_label,
        open_label: &open_label,
        features: FEATURES,
        recent: &recent,
        palette: palette(&ctx),
        web: cfg!(target_arch = "wasm32"),
    };
    match home::show(ui, &screen) {
        Some(home::Action::New | home::Action::Feature(_)) => {
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
