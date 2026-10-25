//! Horix Layout's Home screen: the shared HORIX Home (horix_home.rs) with Horix Layout's names,
//! colours, recent files (with their first-page pictures) and commands. It replaces the old start
//! screen and covers the window below the app bar, as Photoshop's Home does; closing it leaves the
//! empty workspace.

use std::cell::Cell;

use crate::DesignApp;
use crate::horix_home as home;
use serde_json::json;

thread_local! {
    /// Home over open documents (the Home button): the document count it was opened at.
    static OVER: Cell<Option<usize>> = const { Cell::new(None) };
    /// The document count when the person left Home for the workspace.
    static DISMISSED: Cell<Option<usize>> = const { Cell::new(None) };
}

/// Is Home up? With no document it is, until the person leaves it for the empty workspace.
pub fn showing(app: &DesignApp) -> bool {
    let n = app.session.documents().len();
    if OVER.get().is_some_and(|o| o != n) {
        OVER.set(None);
    }
    if DISMISSED.get().is_some_and(|d| d != n) {
        DISMISSED.set(None);
    }
    (n == 0 || OVER.get() == Some(n)) && DISMISSED.get() != Some(n)
}

/// The Home button: Home over the documents (or the empty workspace), or back to them.
pub fn toggle(app: &DesignApp) {
    let n = app.session.documents().len();
    if showing(app) {
        leave(n);
    } else {
        DISMISSED.set(None);
        OVER.set(Some(n));
    }
}

fn leave(n: usize) {
    OVER.set(None);
    DISMISSED.set(Some(n));
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
    home::Feature { mark: "Mag", title: "Open the sample magazine", text: "A four-page spread with threaded text, styles and swatches to explore." },
    home::Feature { mark: "Aa", title: "Beautiful type", text: "Threaded frames, paragraph and character styles, columns, wrap and Arabic." },
    home::Feature { mark: "PDF", title: "Print and share", text: "PDF/X-4 for print, EPUB and PowerPoint; IDML and InDesign files open." },
];

pub fn show(app: &mut DesignApp, ui: &mut egui::Ui) {
    let ctx = ui.ctx().clone();
    let paths: Vec<String> = if cfg!(target_arch = "wasm32") { Vec::new() } else { app.session.prefs.recent_files.iter().take(12).cloned().collect() };
    let recent: Vec<home::Recent> = paths
        .iter()
        .map(|p| {
            let name = crate::menus::recent_label(p);
            let name = name.strip_suffix(".designcraft").map(str::to_owned).unwrap_or(name);
            let folder = std::path::Path::new(p).parent().map(|d| d.display().to_string()).unwrap_or_default();
            let stat = crate::chrome::recent_file_stat(&ctx, p);
            let thumb = stat.exists.then(|| crate::chrome::recent_preview_texture(&ctx, p, stat.modified)).flatten();
            let mut r = home::Recent::new(name, folder);
            if let Some(tex) = thumb {
                let [w, h] = tex.size();
                r.aspect = w as f32 / h.max(1) as f32;
                r.thumbnail = Some(tex.id());
            }
            r
        })
        .collect();
    let paint_logo = |ui: &egui::Ui, r: egui::Rect| crate::about::paint_mark(ui, r, crate::about::BRAND);
    let screen = home::Home {
        id: "horix-layout",
        name: "Horix Layout",
        tagline: "The page layout studio",
        version: "v@HORIX_APP_VERSION@",
        logo: None,
        paint_logo: Some(&paint_logo),
        new_label: "New file",
        open_label: "Open",
        features: FEATURES,
        recent: &recent,
        palette: palette(&ctx),
        web: cfg!(target_arch = "wasm32"),
    };
    match home::show(ui, &screen) {
        Some(home::Action::New | home::Action::Feature(1)) => {
            let _ = app.run("app.newDocumentDialog", json!({}));
        }
        Some(home::Action::Feature(0)) => {
            let _ = app.run("file.newSample", json!({}));
        }
        Some(home::Action::Open | home::Action::Feature(_)) => {
            let _ = app.run("app.openDialog", json!({}));
        }
        Some(home::Action::OpenRecent(i)) => {
            let _ = app.run("app.openRecent", json!({"index": i}));
        }
        Some(home::Action::Workspace) => leave(app.session.documents().len()),
        Some(home::Action::Url(url)) => app.ui.pending_urls.push(url),
        None => {}
    }
}
