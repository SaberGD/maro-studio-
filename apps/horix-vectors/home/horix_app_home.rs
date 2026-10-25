//! Horix Vectors' Home screen: the shared HORIX Home (horix_home.rs) with Horix Vectors' names,
//! recent files and commands. It replaces the old welcome screen and covers the window
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

const TOOLS: &[home::Tool<'static>] = &[
    home::Tool { icon: home::Icon::Pen, title: "Draw with precision", text: "Pen tools, shapes and live corners." },
    home::Tool { icon: home::Icon::Type, title: "Type, including Arabic", text: "Expressive type, on paths or in frames." },
    home::Tool { icon: home::Icon::Files, title: "Open your files", text: "Illustrator, EPS, PDF and SVG." },
];

pub fn show(app: &mut VectorcraftApp, ui: &mut egui::Ui) {
    let paths: Vec<String> = if cfg!(target_arch = "wasm32") { Vec::new() } else { crate::io::recent_files(app).iter().take(12).cloned().collect() };
    let recent: Vec<home::Recent> = paths
        .iter()
        .map(|p| {
            let path = std::path::Path::new(p);
            let name = path.file_name().map(|n| n.to_string_lossy().to_string()).unwrap_or_else(|| p.clone());
            let folder = path.parent().map(|d| d.display().to_string()).unwrap_or_default();
            let mut r = home::Recent::new(name, folder);
            r.kind = "Vector document".into();
            r
        })
        .collect();
    let screen = home::Home {
        id: "horix-vectors",
        name: "HORIX Vectors",
        version: "v@HORIX_APP_VERSION@",
        headline: "Make your next mark.",
        kicker: "THE VECTOR STUDIO",
        drop_title: "Drop vector artwork to continue creating",
        drop_icon: home::Icon::Pen,
        formats: "AI / EPS / SVG / PDF",
        new_label: "New file",
        open_label: "Open file",
        new_shortcut: if cfg!(target_os = "macos") { "Cmd N" } else { "Ctrl N" },
        recent_title: "Recent projects",
        recent: &recent,
        tools: TOOLS,
        web: cfg!(target_arch = "wasm32"),
    };
    match home::show(ui, &screen) {
        Some(home::Action::New | home::Action::Tool(0 | 1)) => {
            app.run("file.newDialog", json!({})).ok();
        }
        Some(home::Action::Open | home::Action::Tool(_)) => {
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
