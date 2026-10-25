//! Horix Light's Home screen: the shared HORIX Home (horix_home.rs) with Horix Light's names,
//! recent libraries and commands. It shows at start and from the Home button, and covers
//! the window below the top bar, as Photoshop's Home does; closing it leaves the library.

use std::cell::Cell;

use crate::LightcraftApp;
use crate::horix_home as home;
use serde_json::json;

thread_local! {
    /// Home is up: at start, and after the Home button.
    static SHOWN: Cell<bool> = const { Cell::new(true) };
}

pub fn showing() -> bool {
    SHOWN.get()
}

/// The Home button.
pub fn toggle() {
    SHOWN.set(!SHOWN.get());
}

const TOOLS: &[home::Tool<'static>] = &[
    home::Tool { icon: home::Icon::Masks, title: "AI masks", text: "Subject, background and object masks." },
    home::Tool { icon: home::Icon::Sliders, title: "Develop photos", text: "White balance, tone, curves and color." },
    home::Tool { icon: home::Icon::Layers, title: "Import Lightroom catalog", text: "Bring your folders, ratings and keywords." },
];

pub fn show(app: &mut LightcraftApp, ui: &mut egui::Ui) {
    let ctx = ui.ctx().clone();
    let desktop = app.services.pick_folder.is_some();
    let paths: Vec<String> = if desktop { app.ui.settings.recent_libraries.iter().take(12).cloned().collect() } else { Vec::new() };
    let recent: Vec<home::Recent> = paths
        .iter()
        .map(|p| {
            let path = std::path::Path::new(p);
            let folder = path.parent().map(|d| d.display().to_string()).unwrap_or_default();
            let mut r = home::Recent::new(crate::panels::settings::library_name(path), folder);
            r.kind = "Photo library".into();
            r.badge = "LIBRARY".into();
            r
        })
        .collect();
    let screen = home::Home {
        id: "horix-light",
        name: "HORIX Light",
        version: "v@HORIX_APP_VERSION@",
        headline: "Your next edit starts here.",
        kicker: "THE PHOTO DEVELOPER",
        drop_title: "Drop photos or folders to start editing",
        drop_icon: home::Icon::Camera,
        formats: "RAW / JPEG / PNG / TIFF",
        new_label: "Import photos",
        open_label: if desktop { "Open library" } else { "Add photos" },
        new_shortcut: "",
        recent_title: "Recent libraries",
        recent: &recent,
        tools: TOOLS,
        web: !desktop,
    };
    let Some(action) = home::show(ui, &screen) else { return };
    let run = |app: &mut LightcraftApp, id: &str, params: serde_json::Value| {
        if let Err(e) = app.run(id, params) {
            app.toast_error(&ctx, e);
        }
    };
    match action {
        home::Action::Url(url) => {
            let _ = crate::links::open(app, &url);
            return;
        }
        home::Action::New | home::Action::Tool(0 | 1) => run(app, "file.addPhotos", json!({})),
        home::Action::Open if desktop => run(app, "app.openLibrary", json!({})),
        home::Action::Open => run(app, "file.addPhotos", json!({})),
        home::Action::Tool(_) if desktop => run(app, "file.importLightroom", json!({})),
        home::Action::Tool(_) => run(app, "file.addPhotos", json!({})),
        home::Action::OpenRecent(i) => {
            if let Some(path) = paths.get(i) {
                run(app, "app.openLibrary", json!({"path": path}));
            }
        }
        home::Action::Workspace => {}
    }
    SHOWN.set(false);
}
