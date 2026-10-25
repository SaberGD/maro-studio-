//! Horix Light's Home screen: the shared HORIX Home (horix_home.rs) with Horix Light's names,
//! colours, recent libraries and commands. It shows at start and from the Home button, and covers
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

fn palette(ctx: &egui::Context) -> home::Palette {
    let t = crate::theme::Tokens::get(ctx);
    home::Palette {
        background: t.grid_bg,
        chrome: t.chrome,
        card: t.cell,
        card_hover: t.hover,
        border: t.divider,
        text: t.text,
        text_strong: t.text,
        text_dim: t.text_dim,
        accent: egui::Color32::from_rgb(0xea, 0x99, 0x3f),
        accent_strong: t.accent,
    }
}

/// The Horix Light falcon, 64 x 64 RGBA (the app icon), as the Home's logo.
fn logo(ctx: &egui::Context) -> egui::Image<'static> {
    let id = egui::Id::new("horix-light-home-logo");
    let tex = ctx.data_mut(|d| d.get_temp::<egui::TextureHandle>(id)).unwrap_or_else(|| {
        let image = egui::ColorImage::from_rgba_unmultiplied([64, 64], include_bytes!("horix-light-logo-64.rgba"));
        let tex = ctx.load_texture("horix-light-home-logo", image, egui::TextureOptions::LINEAR);
        ctx.data_mut(|d| d.insert_temp(id, tex.clone()));
        tex
    });
    egui::Image::from_texture(egui::load::SizedTexture::new(tex.id(), egui::vec2(30.0, 30.0))).corner_radius(7.0)
}

const FEATURES: &[home::Feature<'static>] = &[
    home::Feature { mark: "AI", title: "AI masks", text: "Subject, Background and Object masks with HORIX AI, on your device." },
    home::Feature { mark: "RAW", title: "Develop your photos", text: "White balance, tone, curves, colour grading and lens corrections." },
    home::Feature { mark: "Lr", title: "Bring your library", text: "Import folders and Lightroom catalogs; rate, flag and keyword." },
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
            r.when = "Library".into();
            r
        })
        .collect();
    let screen = home::Home {
        id: "horix-light",
        name: "Horix Light",
        tagline: "The photo developer",
        version: "v@HORIX_APP_VERSION@",
        logo: Some(logo(&ctx)),
        paint_logo: None,
        new_label: "Import photos",
        open_label: if desktop { "Open library" } else { "Add photos" },
        features: FEATURES,
        recent: &recent,
        palette: palette(&ctx),
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
        home::Action::New | home::Action::Feature(0 | 1) => run(app, "file.addPhotos", json!({})),
        home::Action::Open if desktop => run(app, "app.openLibrary", json!({})),
        home::Action::Open => run(app, "file.addPhotos", json!({})),
        home::Action::Feature(_) if desktop => run(app, "file.importLightroom", json!({})),
        home::Action::Feature(_) => run(app, "file.addPhotos", json!({})),
        home::Action::OpenRecent(i) => {
            if let Some(path) = paths.get(i) {
                run(app, "app.openLibrary", json!({"path": path}));
            }
        }
        home::Action::Workspace => {}
    }
    SHOWN.set(false);
}
