//! Horix Layout's Home screen: the shared HORIX Home (horix_home.rs) with Horix Layout's names,
//! recent files (with their first-page pictures) and commands. It replaces the old start
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

const TOOLS: &[home::Tool<'static>] = &[
    home::Tool { icon: home::Icon::Book, title: "Sample magazine", text: "Explore an editable four-page spread." },
    home::Tool { icon: home::Icon::Columns, title: "Beautiful type", text: "Text frames, columns and paragraph styles." },
    home::Tool { icon: home::Icon::Print, title: "Print & share", text: "Prepare publications for print or screen." },
];

pub fn show(app: &mut DesignApp, ui: &mut egui::Ui) {
    let ctx = ui.ctx().clone();
    let paths: Vec<String> = if cfg!(target_arch = "wasm32") { Vec::new() } else { app.session.prefs.recent_files.iter().take(12).cloned().collect() };
    let recent: Vec<home::Recent> = paths
        .iter()
        .map(|p| {
            let name = crate::menus::recent_label(p);
            let folder = std::path::Path::new(p).parent().map(|d| d.display().to_string()).unwrap_or_default();
            let stat = crate::chrome::recent_file_stat(&ctx, p);
            let thumb = stat.exists.then(|| crate::chrome::recent_preview_texture(&ctx, p, stat.modified)).flatten();
            let mut r = home::Recent::new(name, folder);
            r.kind = "Publication".into();
            if r.badge == "DESIGNCRAFT" || r.badge.is_empty() {
                r.badge = "LAYOUT".into();
            }
            r.name = r.name.strip_suffix(".designcraft").map(str::to_owned).unwrap_or(r.name);
            if let Some(tex) = thumb {
                let [w, h] = tex.size();
                r.aspect = w as f32 / h.max(1) as f32;
                r.thumbnail = Some(tex.id());
            }
            r
        })
        .collect();
    let screen = home::Home {
        id: "horix-layout",
        name: "HORIX Layout",
        version: "v@HORIX_APP_VERSION@",
        headline: "Give your ideas a place.",
        kicker: "THE PAGE LAYOUT STUDIO",
        drop_title: "Start a publication or continue a document",
        drop_icon: home::Icon::Book,
        formats: "IDML / INDD / PDF / EPUB",
        new_label: "New document",
        open_label: "Open document",
        new_shortcut: if cfg!(target_os = "macos") { "Cmd N" } else { "Ctrl N" },
        recent_title: "Recent projects",
        recent: &recent,
        tools: TOOLS,
        web: cfg!(target_arch = "wasm32"),
    };
    match home::show(ui, &screen) {
        Some(home::Action::New | home::Action::Tool(1)) => {
            let _ = app.run("app.newDocumentDialog", json!({}));
        }
        Some(home::Action::Tool(0)) => {
            let _ = app.run("file.newSample", json!({}));
        }
        Some(home::Action::Open | home::Action::Tool(_)) => {
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
