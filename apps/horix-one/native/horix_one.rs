//! HORIX One: Horix Vectors (Vector), HORIX (Pixel) and Horix Layout (Layout) in one window, the
//! way Affinity's personas are. The three apps run natively in this process on the window's
//! graphics device; the persona bar at the top shows one of them at a time, and its hand-off
//! buttons take the shown persona's work to another one:
//!
//! - Vector → Pixel as SVG (type as outlines, it opens as shape layers), Vector → Layout as PDF.
//! - Pixel → Vector as PNG, Pixel → Layout as PNG.
//! - Layout → Vector as PDF (the first page).
//!
//! What goes to Layout is placed on the spread in view (a new document when none is open).
//!
//! Each persona keeps its own documents, preferences, fonts and style: switching puts the shown
//! one's fonts and style back on the context ([`PhotocraftApp::horix_one_restyle`]). Only the shown
//! persona runs its frame. Quitting asks about Layout's unsaved documents, then Vector's, then
//! Pixel's.

use horix_layout_app as layout;
use horix_vectors_app as vectors;
use photocraft_ui_egui::PhotocraftApp;

/// The bar's height in points.
const BAR: f32 = 34.0;
/// How long a hand-off message stays up, in seconds.
const NOTE_SECONDS: f64 = 4.0;
/// The persona shown last, in eframe's storage.
const PERSONA_KEY: &str = "horix-one-persona";

const BACKGROUND: egui::Color32 = egui::Color32::from_rgb(14, 14, 15);
const TEXT: egui::Color32 = egui::Color32::from_rgb(232, 232, 234);
const ACCENT: egui::Color32 = egui::Color32::from_rgb(245, 166, 35);
const ON_ACCENT: egui::Color32 = egui::Color32::from_rgb(24, 18, 8);

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Persona {
    Vector,
    Pixel,
    Layout,
}

impl Persona {
    fn key(self) -> &'static str {
        match self {
            Self::Vector => "vector",
            Self::Pixel => "pixel",
            Self::Layout => "layout",
        }
    }

    fn from_key(key: &str) -> Option<Self> {
        match key {
            "vector" => Some(Self::Vector),
            "pixel" => Some(Self::Pixel),
            "layout" => Some(Self::Layout),
            _ => None,
        }
    }
}

pub struct One {
    pixel: PhotocraftApp,
    vector: vectors::App,
    layout: layout::Persona,
    persona: Persona,
    /// A message from the last hand-off and when it went up (the context's time).
    note: Option<(String, f64)>,
}

impl One {
    pub fn new(cc: &eframe::CreationContext<'_>, pixel: PhotocraftApp, custom_titlebar: bool, opened_files: bool) -> Self {
        let vector = vectors::horix_one_persona(cc, custom_titlebar);
        let layout = layout::horix_one_persona(custom_titlebar);
        // Files from the command line or the OS open in Pixel; otherwise the persona shown last.
        let saved = cc.storage.and_then(|s| s.get_string(PERSONA_KEY)).and_then(|k| Persona::from_key(&k));
        let persona = if opened_files { Persona::Pixel } else { saved.unwrap_or(Persona::Pixel) };
        // Pixel's start-up styled nothing yet; Vector and Layout style themselves on their first frame.
        let mut one = Self { pixel, vector, layout, persona: Persona::Pixel, note: None };
        one.switch(persona);
        one
    }

    /// Show `to`, with its own fonts and style from the next frame.
    pub fn switch(&mut self, to: Persona) {
        if to == self.persona {
            return;
        }
        self.persona = to;
        match to {
            Persona::Pixel => self.pixel.horix_one_restyle(),
            Persona::Vector => self.vector.app().horix_one_restyle(),
            Persona::Layout => self.layout.app().horix_one_restyle(),
        }
    }

    fn say(&mut self, ctx: &egui::Context, message: impl Into<String>) {
        self.note = Some((message.into(), ctx.input(|i| i.time)));
        ctx.request_repaint();
    }

    /// The persona each hand-off button of the shown persona goes to.
    fn targets(&self) -> &'static [Persona] {
        match self.persona {
            Persona::Vector => &[Persona::Pixel, Persona::Layout],
            Persona::Pixel => &[Persona::Vector, Persona::Layout],
            Persona::Layout => &[Persona::Vector],
        }
    }

    /// A hand-off button: the shown persona's document goes to `to`.
    pub fn hand_off(&mut self, ctx: &egui::Context, to: Persona) {
        let result = match (self.persona, to) {
            (Persona::Vector, Persona::Pixel) => self.vector_to_pixel(),
            (Persona::Pixel, Persona::Vector) => self.pixel_to_vector(),
            (Persona::Vector, Persona::Layout) => self.vector_to_layout(),
            (Persona::Pixel, Persona::Layout) => self.pixel_to_layout(),
            (Persona::Layout, Persona::Vector) => self.layout_to_vector(),
            _ => return,
        };
        match result {
            Ok(message) => self.say(ctx, message),
            Err(message) => self.say(ctx, message),
        }
    }

    fn vector_to_pixel(&mut self) -> Result<String, String> {
        let stem = self.vector_stem();
        let svg = match self.vector.export_svg() {
            Ok(Some(svg)) => svg,
            Ok(None) => return Err("Nothing to open: open or make a drawing in Vector first.".into()),
            Err(e) => return Err(format!("The drawing couldn't be exported: {e}")),
        };
        self.pixel.open_bytes(&format!("{stem}.svg"), &svg).map_err(|e| format!("Pixel couldn't open the drawing: {e}"))?;
        self.switch(Persona::Pixel);
        Ok("The drawing opened in Pixel as shape layers.".into())
    }

    /// Pixel's active image as PNG, and its name without the extension.
    fn pixel_png(&mut self) -> Result<(String, Vec<u8>), String> {
        let Some(name) = self.pixel.session.active().map(|d| d.doc.name.clone()) else {
            return Err("Nothing to send: open or make an image in Pixel first.".into());
        };
        let stem = file_stem(&name);
        let path = std::env::temp_dir().join(format!("horix-one-{}-{stem}.png", std::process::id()));
        let exported = self.pixel.run("file.export.quickExport", serde_json::json!({"path": path.to_string_lossy()}));
        let bytes = exported.and_then(|_| std::fs::read(&path).map_err(|e| e.to_string()));
        let _ = std::fs::remove_file(&path);
        let bytes = bytes.map_err(|e| format!("The image couldn't be exported: {e}"))?;
        Ok((stem, bytes))
    }

    fn pixel_to_vector(&mut self) -> Result<String, String> {
        let (stem, bytes) = self.pixel_png()?;
        self.vector.open_bytes(&format!("{stem}.png"), &bytes).map_err(|e| format!("Vector couldn't open the image: {e}"))?;
        self.switch(Persona::Vector);
        Ok("The image opened in Vector.".into())
    }

    fn pixel_to_layout(&mut self) -> Result<String, String> {
        let (stem, bytes) = self.pixel_png()?;
        self.layout.place_bytes(&format!("{stem}.png"), &bytes).map_err(|e| format!("Layout couldn't place the image: {e}"))?;
        self.switch(Persona::Layout);
        Ok("The image is placed in Layout.".into())
    }

    fn vector_to_layout(&mut self) -> Result<String, String> {
        let stem = self.vector_stem();
        let pdf = match self.vector.export_pdf() {
            Ok(Some(pdf)) => pdf,
            Ok(None) => return Err("Nothing to send: open or make a drawing in Vector first.".into()),
            Err(e) => return Err(format!("The drawing couldn't be exported: {e}")),
        };
        self.layout.place_bytes(&format!("{stem}.pdf"), &pdf).map_err(|e| format!("Layout couldn't place the drawing: {e}"))?;
        self.switch(Persona::Layout);
        Ok("The drawing is placed in Layout.".into())
    }

    fn layout_to_vector(&mut self) -> Result<String, String> {
        let session = &self.layout.app().session;
        let active = session.active_index().and_then(|i| session.documents().get(i));
        let stem = active.map(|d| file_stem(&d.title())).unwrap_or_else(|| "from-layout".into());
        let pdf = match self.layout.export_pdf() {
            Ok(Some(pdf)) => pdf,
            Ok(None) => return Err("Nothing to send: open or make a document in Layout first.".into()),
            Err(e) => return Err(format!("The page couldn't be exported: {e}")),
        };
        self.vector.open_bytes(&format!("{stem}.pdf"), &pdf).map_err(|e| format!("Vector couldn't open the page: {e}"))?;
        self.switch(Persona::Vector);
        Ok("The first page opened in Vector.".into())
    }

    /// The name of Vector's active drawing without its folder and extension.
    fn vector_stem(&mut self) -> String {
        self.vector.app().session.active().and_then(|d| d.path.as_deref().map(file_stem)).unwrap_or_else(|| "from-vector".into())
    }

    fn bar(&mut self, ui: &mut egui::Ui) {
        let mac = cfg!(target_os = "macos");
        egui::Panel::top("horix-one-personas")
            .exact_size(BAR)
            .frame(egui::Frame::NONE.fill(BACKGROUND).inner_margin(egui::Margin { left: if mac { 78 } else { 10 }, right: 10, top: 0, bottom: 0 }))
            .show(ui, |ui| {
                // The bar's free space moves the window, and a double click maximizes it.
                let whole = ui.max_rect();
                let drag = ui.interact(whole, ui.id().with("drag"), egui::Sense::click_and_drag());
                if drag.drag_started_by(egui::PointerButton::Primary) {
                    ui.ctx().send_viewport_cmd(egui::ViewportCommand::StartDrag);
                }
                if drag.double_clicked() {
                    let max = ui.ctx().input(|i| i.viewport().maximized.unwrap_or(false));
                    ui.ctx().send_viewport_cmd(egui::ViewportCommand::Maximized(!max));
                }
                ui.horizontal_centered(|ui| {
                    ui.spacing_mut().item_spacing.x = 6.0;
                    ui.label(egui::RichText::new("HORIX").strong().size(14.0).color(TEXT));
                    ui.label(egui::RichText::new("ONE").strong().size(14.0).color(ACCENT));
                    ui.add_space(14.0);
                    for (persona, label) in [(Persona::Vector, "Vector"), (Persona::Pixel, "Pixel"), (Persona::Layout, "Layout")] {
                        if persona_button(ui, label, self.persona == persona).clicked() {
                            self.switch(persona);
                        }
                    }
                    ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                        // Right to left: the last target first.
                        for &to in self.targets().iter().rev() {
                            let (label, tip) = match (self.persona, to) {
                                (Persona::Vector, Persona::Pixel) => ("Open in Pixel  →", "Open this drawing in Pixel as shape layers (type as outlines)"),
                                (Persona::Pixel, Persona::Vector) => ("Open in Vector  →", "Open this image in Vector"),
                                (Persona::Layout, Persona::Vector) => ("Open in Vector  →", "Open this document's first page in Vector"),
                                (Persona::Vector, _) => ("Place in Layout  →", "Place this drawing on the spread in Layout"),
                                _ => ("Place in Layout  →", "Place this image on the spread in Layout"),
                            };
                            let button = egui::Button::new(egui::RichText::new(label).size(13.0).color(TEXT))
                                .fill(egui::Color32::from_rgb(34, 34, 38))
                                .stroke(egui::Stroke::new(1.0, egui::Color32::from_rgb(60, 60, 66)))
                                .corner_radius(6.0);
                            if ui.add(button).on_hover_text(tip).clicked() {
                                self.hand_off(ui.ctx(), to);
                            }
                        }
                    });
                });
            });
    }

    fn note(&mut self, ctx: &egui::Context) {
        let Some((message, at)) = &self.note else { return };
        let left = NOTE_SECONDS - (ctx.input(|i| i.time) - at);
        if left <= 0.0 {
            self.note = None;
            return;
        }
        ctx.request_repaint_after(std::time::Duration::from_secs_f64(left.min(0.5)));
        let message = message.clone();
        egui::Area::new(egui::Id::new("horix-one-note"))
            .order(egui::Order::Tooltip)
            .anchor(egui::Align2::CENTER_BOTTOM, egui::vec2(0.0, -48.0))
            .interactable(false)
            .show(ctx, |ui| {
                egui::Frame::NONE.fill(BACKGROUND).stroke(egui::Stroke::new(1.0, ACCENT)).corner_radius(8.0).inner_margin(egui::Margin::symmetric(14, 9)).show(
                    ui,
                    |ui| {
                        ui.label(egui::RichText::new(message).size(13.0).color(TEXT));
                    },
                );
            });
    }
}

fn persona_button(ui: &mut egui::Ui, label: &str, active: bool) -> egui::Response {
    let text = egui::RichText::new(label).size(13.0).color(if active { ON_ACCENT } else { TEXT });
    let button = egui::Button::new(text).corner_radius(6.0).min_size(egui::vec2(64.0, 24.0));
    let button = if active { button.fill(ACCENT) } else { button.fill(egui::Color32::TRANSPARENT) };
    ui.add(button)
}

/// A file name without its folder and extension.
fn file_stem(name: &str) -> String {
    let base = name.rsplit(['/', '\\']).next().unwrap_or(name);
    let stem = base.rsplit_once('.').map_or(base, |(stem, _)| stem);
    if stem.is_empty() { "untitled".into() } else { stem.into() }
}

impl eframe::App for One {
    fn logic(&mut self, ctx: &egui::Context, frame: &mut eframe::Frame) {
        // Quitting: Layout, then Vector, ask about their unsaved documents; once they have none, Pixel asks
        // about its own and leaves (on macOS through AppKit).
        if ctx.input(|i| i.viewport().close_requested()) {
            let first = if self.layout.unsaved() {
                Persona::Layout
            } else if self.vector.app().horix_one_unsaved() {
                Persona::Vector
            } else {
                Persona::Pixel
            };
            self.switch(first);
        }
        match self.persona {
            Persona::Pixel => self.pixel.logic(ctx, frame),
            Persona::Vector => self.vector.logic(ctx, frame),
            Persona::Layout => self.layout.logic(ctx, frame),
        }
    }

    fn raw_input_hook(&mut self, ctx: &egui::Context, raw_input: &mut egui::RawInput) {
        match self.persona {
            Persona::Pixel => self.pixel.raw_input_hook(ctx, raw_input),
            Persona::Vector | Persona::Layout => {
                // The window stays borderless whichever persona shows (Pixel made it, #2246).
                if let Some(window_frame) = self.pixel.services.window_frame.as_mut() {
                    window_frame();
                }
                if self.persona == Persona::Vector {
                    self.vector.raw_input_hook(ctx, raw_input);
                } else {
                    self.layout.raw_input_hook(ctx, raw_input);
                }
            }
        }
    }

    fn ui(&mut self, ui: &mut egui::Ui, frame: &mut eframe::Frame) {
        self.bar(ui);
        match self.persona {
            Persona::Pixel => self.pixel.ui(ui, frame),
            Persona::Vector => self.vector.ui(ui, frame),
            Persona::Layout => self.layout.ui(ui, frame),
        }
        self.note(ui.ctx());
    }

    fn save(&mut self, storage: &mut dyn eframe::Storage) {
        storage.set_string(PERSONA_KEY, self.persona.key().into());
    }

    fn on_exit(&mut self) {
        self.layout.on_exit();
        self.vector.on_exit();
        self.pixel.on_exit();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn file_stems() {
        assert_eq!(file_stem("/a/b/logo.vectorcraft"), "logo");
        assert_eq!(file_stem("C:\\work\\photo.final.psd"), "photo.final");
        assert_eq!(file_stem("Untitled-1"), "Untitled-1");
        assert_eq!(file_stem(".svg"), "untitled");
    }

    #[test]
    fn persona_keys_round_trip() {
        for p in [Persona::Vector, Persona::Pixel, Persona::Layout] {
            assert_eq!(Persona::from_key(p.key()), Some(p));
        }
        assert_eq!(Persona::from_key("video"), None);
    }
}
