//! HORIX Home: the start screen of every HORIX app (HORIX, Horix Vectors, Horix Light, Horix
//! Layout), in the spirit of Photoshop's: a sidebar with New and Open, Saber Group Academy's
//! banner, what the app does, and the recent files. Closing it (or opening anything) leaves the
//! empty workspace, as Photoshop does.
//!
//! One file, copied into each app's UI crate by its rebrand.py (apps/horix-common/home/), so the
//! apps share it without a new crate: it needs egui only. The app supplies its names, colours,
//! logo and recent files, and acts on the [`Action`] that comes back.

use egui::{Align, Align2, Color32, CornerRadius, FontId, Layout, Pos2, Rect, Sense, Stroke, Ui, UiBuilder, Vec2, pos2, vec2};

pub const FACEBOOK: &str = "https://www.facebook.com/sabergroup.academy/";
pub const INSTAGRAM: &str = "https://www.instagram.com/sabergroup.academy";
pub const TELEGRAM: &str = "https://t.me/SABERGROUPEG";
/// WhatsApp, with a ready message ("Hello, I am coming from HORIX and want to know about the
/// courses and services").
pub const WHATSAPP: &str = "https://wa.me/201040784390?text=%D9%85%D8%B1%D8%AD%D8%A8%D9%8B%D8%A7%D8%8C%20%D8%AC%D8%A7%D9%8A%20%D9%85%D9%86%20HORIX%20%D9%88%D8%B9%D8%A7%D9%8A%D8%B2%20%D8%A3%D8%B9%D8%B1%D9%81%20%D8%B9%D9%86%20%D8%A7%D9%84%D9%83%D9%88%D8%B1%D8%B3%D8%A7%D8%AA%20%D9%88%D8%A7%D9%84%D8%AE%D8%AF%D9%85%D8%A7%D8%AA";
pub const DOWNLOADS: &str = "https://horix.si/";

/// The HORIX family, for the sidebar: (id, name, web address).
pub const FAMILY: &[(&str, &str, &str)] = &[
    ("horix-one", "HORIX One", "https://one.horix.live/"),
    ("horix", "HORIX", "https://horix.live/"),
    ("horix-vectors", "Horix Vectors", "https://vectors.horix.live/"),
    ("horix-light", "Horix Light", "https://light.horix.live/"),
    ("horix-layout", "Horix Layout", "https://layout.horix.live/"),
];

const TELEGRAM_BLUE: Color32 = Color32::from_rgb(0x22, 0x9e, 0xd9);
const WHATSAPP_GREEN: Color32 = Color32::from_rgb(0x1f, 0xa8, 0x55);
const FACEBOOK_BLUE: Color32 = Color32::from_rgb(0x18, 0x77, 0xf2);
const INSTAGRAM_PINK: Color32 = Color32::from_rgb(0xd6, 0x29, 0x76);
const SIDEBAR_W: f32 = 232.0;
const TOP_H: f32 = 52.0;

/// The app's colours (its theme tokens).
#[derive(Clone, Copy, Debug)]
pub struct Palette {
    /// The page behind everything.
    pub background: Color32,
    /// The sidebar and the top bar.
    pub chrome: Color32,
    /// Cards.
    pub card: Color32,
    pub card_hover: Color32,
    pub border: Color32,
    pub text: Color32,
    pub text_strong: Color32,
    pub text_dim: Color32,
    /// What is on (Vision Amber).
    pub accent: Color32,
    /// Filled primary buttons (Horix Red).
    pub accent_strong: Color32,
}

impl Default for Palette {
    /// HORIX's own colours, for an app whose tokens differ.
    fn default() -> Self {
        Self {
            background: Color32::from_rgb(0x14, 0x13, 0x14),
            chrome: Color32::from_rgb(0x0e, 0x0d, 0x0e),
            card: Color32::from_rgb(0x22, 0x1f, 0x20),
            card_hover: Color32::from_rgb(0x2c, 0x28, 0x29),
            border: Color32::from_rgb(0x36, 0x31, 0x31),
            text: Color32::from_rgb(0xe6, 0xe1, 0xda),
            text_strong: Color32::from_rgb(0xf3, 0xef, 0xe8),
            text_dim: Color32::from_rgb(0x9e, 0x98, 0x91),
            accent: Color32::from_rgb(0xea, 0x99, 0x3f),
            accent_strong: Color32::from_rgb(0xd6, 0x3c, 0x32),
        }
    }
}

/// One of the things the app does, shown as a card that starts it.
pub struct Feature<'a> {
    /// A short mark in the card's tile ("AI", "Aa", …).
    pub mark: &'a str,
    pub title: &'a str,
    pub text: &'a str,
}

/// A recent file.
pub struct Recent {
    pub name: String,
    /// Its folder, or where it is kept.
    pub location: String,
    /// When it was last opened ("2 days ago"), if known.
    pub when: String,
    /// A preview, if the app has one.
    pub thumbnail: Option<egui::TextureId>,
    /// The thumbnail's width / height.
    pub aspect: f32,
}

impl Recent {
    pub fn new(name: impl Into<String>, location: impl Into<String>) -> Self {
        Self { name: name.into(), location: location.into(), when: String::new(), thumbnail: None, aspect: 1.0 }
    }
}

/// What the home screen asks the app to do.
#[derive(Clone, Debug, PartialEq)]
pub enum Action {
    New,
    Open,
    /// The recent file at this index.
    OpenRecent(usize),
    /// The feature card at this index.
    Feature(usize),
    /// Leave the home screen for the (empty) workspace.
    Workspace,
    /// Open this address in the browser.
    Url(String),
}

/// The app, as the home screen shows it.
pub struct Home<'a> {
    /// The app's family id (horix, horix-vectors, …), left out of the family list.
    pub id: &'a str,
    pub name: &'a str,
    /// What it is, in a few words ("The visionary AI editor").
    pub tagline: &'a str,
    pub version: &'a str,
    pub logo: Option<egui::Image<'static>>,
    /// Draws the logo into a square, for an app whose logo is no image.
    pub paint_logo: Option<&'a dyn Fn(&Ui, Rect)>,
    pub new_label: &'a str,
    pub open_label: &'a str,
    pub features: &'a [Feature<'a>],
    pub recent: &'a [Recent],
    pub palette: Palette,
    /// In the browser: the sidebar offers the desktop app.
    pub web: bool,
}

/// Draw the home screen over `ui`'s whole area. Returns what the person asked for.
pub fn show(ui: &mut Ui, home: &Home<'_>) -> Option<Action> {
    let mut action = None;
    let full = ui.max_rect();
    let p = home.palette;
    ui.painter().rect_filled(full, 0.0, p.background);
    let top = Rect::from_min_size(full.min, vec2(full.width(), TOP_H));
    let side = Rect::from_min_max(pos2(full.left(), top.bottom()), pos2(full.left() + SIDEBAR_W, full.bottom()));
    let main = Rect::from_min_max(pos2(side.right(), top.bottom()), full.max);
    ui.scope_builder(UiBuilder::new().max_rect(top), |ui| top_bar(ui, home, &mut action));
    ui.scope_builder(UiBuilder::new().max_rect(side), |ui| sidebar(ui, home, &mut action));
    ui.scope_builder(UiBuilder::new().max_rect(main), |ui| {
        egui::ScrollArea::vertical().id_salt("horix-home-main").auto_shrink([false, false]).show(ui, |ui| {
            egui::Frame::NONE.inner_margin(egui::Margin { left: 40, right: 40, top: 28, bottom: 40 }).show(ui, |ui| {
                ui.set_max_width(ui.available_width().min(1180.0));
                main_area(ui, home, &mut action);
            });
        });
    });
    // Esc goes to the workspace, as closing Photoshop's home does.
    if ui.input(|i| i.key_pressed(egui::Key::Escape)) && action.is_none() {
        action = Some(Action::Workspace);
    }
    action
}

fn top_bar(ui: &mut Ui, home: &Home<'_>, action: &mut Option<Action>) {
    let p = home.palette;
    let r = ui.max_rect();
    ui.painter().rect_filled(r, 0.0, p.chrome);
    ui.painter().hline(r.x_range(), r.bottom() - 0.5, Stroke::new(1.0, p.border));
    let inner = r.shrink2(vec2(18.0, 0.0));
    ui.scope_builder(UiBuilder::new().max_rect(inner).layout(Layout::left_to_right(Align::Center)), |ui| {
        if let Some(logo) = &home.logo {
            ui.add(logo.clone().fit_to_exact_size(vec2(30.0, 30.0)));
            ui.add_space(6.0);
        } else if let Some(paint) = home.paint_logo {
            let (r, _) = ui.allocate_exact_size(vec2(30.0, 30.0), Sense::hover());
            paint(ui, r);
            ui.add_space(6.0);
        }
        ui.label(egui::RichText::new(home.name).size(17.0).color(p.text_strong).strong());
        ui.add_space(10.0);
        ui.label(egui::RichText::new(home.tagline).size(12.5).color(p.text_dim));
        ui.with_layout(Layout::right_to_left(Align::Center), |ui| {
            if close_button(ui, p).on_hover_text("Go to the workspace (Esc)").clicked() {
                *action = Some(Action::Workspace);
            }
            ui.add_space(12.0);
            if pill(ui, "Join us on Telegram", TELEGRAM_BLUE, Color32::WHITE, Some(Glyph::Telegram)).on_hover_text(TELEGRAM).clicked() {
                *action = Some(Action::Url(TELEGRAM.into()));
            }
        });
    });
}

fn sidebar(ui: &mut Ui, home: &Home<'_>, action: &mut Option<Action>) {
    let p = home.palette;
    let r = ui.max_rect();
    ui.painter().rect_filled(r, 0.0, p.chrome);
    ui.painter().vline(r.right() - 0.5, r.y_range(), Stroke::new(1.0, p.border));
    let inner = r.shrink2(vec2(18.0, 20.0));
    ui.scope_builder(UiBuilder::new().max_rect(inner).layout(Layout::top_down(Align::Min)), |ui| {
        ui.spacing_mut().item_spacing.y = 8.0;
        if wide_button(ui, home.new_label, p.accent_strong, Color32::WHITE, None, Glyph::Plus).clicked() {
            *action = Some(Action::New);
        }
        if wide_button(ui, home.open_label, Color32::TRANSPARENT, p.text_strong, Some(p.border), Glyph::Folder).clicked() {
            *action = Some(Action::Open);
        }
        ui.add_space(12.0);
        nav_item(ui, p, Glyph::Home, "Home", true);
        if nav_item(ui, p, Glyph::Play, "Workspace", false).clicked() {
            *action = Some(Action::Workspace);
        }
        if nav_item(ui, p, Glyph::Cap, "Courses", false).on_hover_text("Saber Group Academy on WhatsApp").clicked() {
            *action = Some(Action::Url(WHATSAPP.into()));
        }
        if home.web && nav_item(ui, p, Glyph::Download, "Desktop app", false).on_hover_text(DOWNLOADS).clicked() {
            *action = Some(Action::Url(DOWNLOADS.into()));
        }
        ui.add_space(14.0);
        section_label(ui, p, "THE HORIX FAMILY");
        for (id, name, url) in FAMILY.iter().filter(|(id, ..)| *id != home.id) {
            let _ = id;
            if nav_item(ui, p, Glyph::Dot, name, false).on_hover_text(*url).clicked() {
                *action = Some(Action::Url((*url).into()));
            }
        }
        // Saber Group's accounts at the foot of the sidebar.
        ui.with_layout(Layout::bottom_up(Align::Min), |ui| {
            ui.label(egui::RichText::new(format!("{} {} · by Saber Group", home.name, home.version)).size(11.0).color(p.text_dim));
            ui.add_space(4.0);
            ui.horizontal(|ui| {
                ui.spacing_mut().item_spacing.x = 8.0;
                for (glyph, color, url, tip) in [
                    (Glyph::Facebook, FACEBOOK_BLUE, FACEBOOK, "Facebook"),
                    (Glyph::Instagram, INSTAGRAM_PINK, INSTAGRAM, "Instagram"),
                    (Glyph::WhatsApp, WHATSAPP_GREEN, WHATSAPP, "WhatsApp"),
                    (Glyph::Telegram, TELEGRAM_BLUE, TELEGRAM, "Telegram"),
                ] {
                    if social(ui, glyph, color).on_hover_text(tip).clicked() {
                        *action = Some(Action::Url(url.into()));
                    }
                }
            });
            ui.add_space(2.0);
            section_label(ui, p, "SABER GROUP ACADEMY");
        });
    });
}

fn main_area(ui: &mut Ui, home: &Home<'_>, action: &mut Option<Action>) {
    let p = home.palette;
    ui.label(egui::RichText::new(format!("Welcome to {}", home.name)).size(30.0).color(p.text_strong));
    ui.add_space(18.0);
    banner(ui, home, action);
    ui.add_space(34.0);
    if !home.features.is_empty() {
        ui.label(egui::RichText::new("What you can do").size(18.0).color(p.text_strong));
        ui.add_space(10.0);
        let cols = home.features.len().clamp(1, 3);
        let gap = 14.0;
        let w = ((ui.available_width() - gap * (cols as f32 - 1.0)) / cols as f32).max(220.0);
        ui.horizontal_wrapped(|ui| {
            ui.spacing_mut().item_spacing = vec2(gap, gap);
            for (i, f) in home.features.iter().enumerate() {
                if feature_card(ui, p, f, w).clicked() {
                    *action = Some(Action::Feature(i));
                }
            }
        });
        ui.add_space(26.0);
    }
    ui.horizontal(|ui| {
        ui.label(egui::RichText::new("Recent").size(18.0).color(p.text_strong));
    });
    ui.add_space(10.0);
    if home.recent.is_empty() {
        egui::Frame::NONE.fill(p.card).corner_radius(10.0).inner_margin(egui::Margin::symmetric(20, 22)).show(ui, |ui| {
            ui.set_width(ui.available_width());
            ui.label(egui::RichText::new("Nothing here yet").size(14.0).color(p.text));
            ui.label(egui::RichText::new(format!("Files you open or save in {} show up here.", home.name)).size(12.5).color(p.text_dim));
        });
    } else {
        ui.horizontal_wrapped(|ui| {
            ui.spacing_mut().item_spacing = vec2(14.0, 14.0);
            for (i, r) in home.recent.iter().enumerate() {
                if recent_tile(ui, p, r).on_hover_text(format!("{}\n{}", r.name, r.location)).clicked() {
                    *action = Some(Action::OpenRecent(i));
                }
            }
        });
    }
}

/// Saber Group Academy's banner: a Horix Red to ink card with the contact buttons.
fn banner(ui: &mut Ui, home: &Home<'_>, action: &mut Option<Action>) {
    let p = home.palette;
    let w = ui.available_width();
    let (rect, _) = ui.allocate_exact_size(vec2(w, 170.0), Sense::hover());
    let left = Color32::from_rgb(0x8f, 0x22, 0x1c);
    let right = Color32::from_rgb(0x1e, 0x14, 0x14);
    let mut mesh = egui::Mesh::default();
    mesh.colored_vertex(rect.left_top(), left);
    mesh.colored_vertex(rect.right_top(), right);
    mesh.colored_vertex(rect.right_bottom(), right);
    mesh.colored_vertex(rect.left_bottom(), left);
    mesh.add_triangle(0, 1, 2);
    mesh.add_triangle(0, 2, 3);
    let painter = ui.painter().with_clip_rect(rect);
    painter.add(egui::Shape::mesh(mesh));
    // A soft amber glow at the right.
    painter.circle_filled(pos2(rect.right() - 90.0, rect.top() + 30.0), 120.0, Color32::from_rgba_unmultiplied(0xea, 0x99, 0x3f, 26));
    painter.rect_stroke(rect, CornerRadius::same(12), Stroke::new(1.0, p.border), egui::StrokeKind::Inside);
    let inner = rect.shrink2(vec2(28.0, 22.0));
    ui.scope_builder(UiBuilder::new().max_rect(inner).layout(Layout::top_down(Align::Min)), |ui| {
        ui.label(egui::RichText::new("SABER GROUP ACADEMY").size(11.5).color(p.accent));
        ui.add_space(2.0);
        ui.label(egui::RichText::new(format!("Learn {} with the people who make it", home.name)).size(22.0).color(Color32::WHITE));
        ui.label(
            egui::RichText::new("Courses, workshops and answers in Arabic, from the team behind the HORIX family.")
                .size(13.0)
                .color(Color32::from_rgb(0xe8, 0xd8, 0xd0)),
        );
        ui.add_space(14.0);
        ui.horizontal(|ui| {
            ui.spacing_mut().item_spacing.x = 10.0;
            if pill(ui, "Ask on WhatsApp", WHATSAPP_GREEN, Color32::WHITE, Some(Glyph::WhatsApp)).clicked() {
                *action = Some(Action::Url(WHATSAPP.into()));
            }
            if pill(ui, "Facebook", FACEBOOK_BLUE, Color32::WHITE, Some(Glyph::Facebook)).clicked() {
                *action = Some(Action::Url(FACEBOOK.into()));
            }
            if pill(ui, "Instagram", INSTAGRAM_PINK, Color32::WHITE, Some(Glyph::Instagram)).clicked() {
                *action = Some(Action::Url(INSTAGRAM.into()));
            }
            if pill(ui, "Telegram", TELEGRAM_BLUE, Color32::WHITE, Some(Glyph::Telegram)).clicked() {
                *action = Some(Action::Url(TELEGRAM.into()));
            }
        });
    });
}

fn feature_card(ui: &mut Ui, p: Palette, f: &Feature<'_>, w: f32) -> egui::Response {
    let (rect, resp) = ui.allocate_exact_size(vec2(w, 112.0), Sense::click());
    let fill = if resp.hovered() { p.card_hover } else { p.card };
    ui.painter().rect_filled(rect, 10.0, fill);
    let tile = Rect::from_min_size(rect.min + vec2(16.0, 16.0), vec2(44.0, 44.0));
    ui.painter().rect_filled(tile, 9.0, p.accent.gamma_multiply(0.18));
    ui.painter().text(tile.center(), Align2::CENTER_CENTER, f.mark, FontId::proportional(16.0), p.accent);
    let x = tile.right() + 14.0;
    let text_w = rect.right() - x - 14.0;
    ui.painter().text(pos2(x, rect.top() + 18.0), Align2::LEFT_TOP, f.title, FontId::proportional(15.0), p.text_strong);
    let galley = ui.painter().layout(f.text.to_owned(), FontId::proportional(12.5), p.text_dim, text_w.max(80.0));
    ui.painter().galley(pos2(x, rect.top() + 40.0), galley, p.text_dim);
    ui.painter().text(pos2(x, rect.bottom() - 16.0), Align2::LEFT_BOTTOM, "Try it  →", FontId::proportional(12.5), p.accent);
    resp.on_hover_cursor(egui::CursorIcon::PointingHand)
}

fn recent_tile(ui: &mut Ui, p: Palette, r: &Recent) -> egui::Response {
    let size = vec2(184.0, 172.0);
    let (rect, resp) = ui.allocate_exact_size(size, Sense::click());
    let fill = if resp.hovered() { p.card_hover } else { p.card };
    ui.painter().rect_filled(rect, 10.0, fill);
    let thumb = Rect::from_min_size(rect.min + vec2(10.0, 10.0), vec2(size.x - 20.0, 112.0));
    ui.painter().rect_filled(thumb, 6.0, p.background);
    match r.thumbnail {
        Some(tex) => {
            let a = r.aspect.max(0.05);
            let fit = if thumb.width() / thumb.height() > a { vec2(thumb.height() * a, thumb.height()) } else { vec2(thumb.width(), thumb.width() / a) };
            let img = Rect::from_center_size(thumb.center(), fit);
            ui.painter().image(tex, img, Rect::from_min_max(Pos2::ZERO, pos2(1.0, 1.0)), Color32::WHITE);
        }
        None => {
            // A page with the file's type on it.
            let page = Rect::from_center_size(thumb.center(), vec2(58.0, 74.0));
            ui.painter().rect_filled(page, 4.0, p.card_hover);
            ui.painter().rect_stroke(page, 4.0, Stroke::new(1.0, p.border), egui::StrokeKind::Inside);
            let ext = r.name.rsplit_once('.').map(|(_, e)| e.to_uppercase()).filter(|e| e.len() <= 5).unwrap_or_default();
            ui.painter().text(page.center(), Align2::CENTER_CENTER, ext, FontId::proportional(13.0), p.accent);
        }
    }
    let name = elide(ui, &r.name, FontId::proportional(13.0), size.x - 20.0);
    ui.painter().text(pos2(rect.left() + 10.0, thumb.bottom() + 10.0), Align2::LEFT_TOP, name, FontId::proportional(13.0), p.text_strong);
    let sub = if r.when.is_empty() { r.location.clone() } else { r.when.clone() };
    let sub = elide(ui, &sub, FontId::proportional(11.5), size.x - 20.0);
    ui.painter().text(pos2(rect.left() + 10.0, thumb.bottom() + 29.0), Align2::LEFT_TOP, sub, FontId::proportional(11.5), p.text_dim);
    resp.on_hover_cursor(egui::CursorIcon::PointingHand)
}

/// `text` shortened with an ellipsis to fit `width`.
fn elide(ui: &Ui, text: &str, font: FontId, width: f32) -> String {
    let fits = |s: &str| ui.fonts_mut(|f| f.layout_no_wrap(s.to_owned(), font.clone(), Color32::WHITE).size().x) <= width;
    if fits(text) {
        return text.to_owned();
    }
    let chars: Vec<char> = text.chars().collect();
    let (mut lo, mut hi) = (0, chars.len());
    while lo < hi {
        let mid = (lo + hi).div_ceil(2);
        let s: String = chars[..mid].iter().collect::<String>() + "…";
        if fits(&s) { lo = mid } else { hi = mid - 1 }
    }
    chars[..lo].iter().collect::<String>() + "…"
}

fn section_label(ui: &mut Ui, p: Palette, text: &str) {
    ui.label(egui::RichText::new(text).size(10.5).color(p.text_dim));
}

fn nav_item(ui: &mut Ui, p: Palette, glyph: Glyph, text: &str, selected: bool) -> egui::Response {
    let w = ui.available_width();
    let (rect, resp) = ui.allocate_exact_size(vec2(w, 32.0), Sense::click());
    if selected || resp.hovered() {
        ui.painter().rect_filled(rect, 7.0, if selected { p.card_hover } else { p.card });
    }
    if selected {
        ui.painter().rect_filled(Rect::from_min_size(rect.min + vec2(0.0, 7.0), vec2(3.0, 18.0)), 2.0, p.accent);
    }
    let c = if selected { p.text_strong } else { p.text };
    glyph.paint(ui.painter(), pos2(rect.left() + 18.0, rect.center().y), 14.0, if selected { p.accent } else { p.text_dim });
    ui.painter().text(pos2(rect.left() + 34.0, rect.center().y), Align2::LEFT_CENTER, text, FontId::proportional(13.5), c);
    resp.on_hover_cursor(egui::CursorIcon::PointingHand)
}

fn wide_button(ui: &mut Ui, text: &str, fill: Color32, color: Color32, stroke: Option<Color32>, glyph: Glyph) -> egui::Response {
    let w = ui.available_width();
    let (rect, resp) = ui.allocate_exact_size(vec2(w, 38.0), Sense::click());
    let fill = if resp.hovered() && fill != Color32::TRANSPARENT { fill.gamma_multiply(0.88) } else { fill };
    ui.painter().rect_filled(rect, 19.0, fill);
    if let Some(s) = stroke {
        let s = if resp.hovered() { color } else { s };
        ui.painter().rect_stroke(rect, 19.0, Stroke::new(1.0, s), egui::StrokeKind::Inside);
    }
    let galley = ui.painter().layout_no_wrap(text.to_owned(), FontId::proportional(14.0), color);
    let total = 14.0 + 8.0 + galley.size().x;
    let x0 = rect.center().x - total / 2.0;
    glyph.paint(ui.painter(), pos2(x0 + 7.0, rect.center().y), 14.0, color);
    ui.painter().galley(pos2(x0 + 22.0, rect.center().y - galley.size().y / 2.0), galley, color);
    resp.on_hover_cursor(egui::CursorIcon::PointingHand)
}

fn pill(ui: &mut Ui, text: &str, fill: Color32, color: Color32, glyph: Option<Glyph>) -> egui::Response {
    let galley = ui.painter().layout_no_wrap(text.to_owned(), FontId::proportional(13.0), color);
    let icon = if glyph.is_some() { 20.0 } else { 0.0 };
    let size = vec2(galley.size().x + icon + 28.0, 32.0);
    let (rect, resp) = ui.allocate_exact_size(size, Sense::click());
    let fill = if resp.hovered() { fill.gamma_multiply(0.85) } else { fill };
    ui.painter().rect_filled(rect, 16.0, fill);
    if let Some(g) = glyph {
        g.paint(ui.painter(), pos2(rect.left() + 21.0, rect.center().y), 14.0, color);
    }
    ui.painter().galley(pos2(rect.left() + 14.0 + icon, rect.center().y - galley.size().y / 2.0), galley, color);
    resp.on_hover_cursor(egui::CursorIcon::PointingHand)
}

fn social(ui: &mut Ui, glyph: Glyph, color: Color32) -> egui::Response {
    let (rect, resp) = ui.allocate_exact_size(vec2(30.0, 30.0), Sense::click());
    let fill = if resp.hovered() { color } else { color.gamma_multiply(0.85) };
    ui.painter().circle_filled(rect.center(), 15.0, fill);
    glyph.paint(ui.painter(), rect.center(), 15.0, Color32::WHITE);
    resp.on_hover_cursor(egui::CursorIcon::PointingHand)
}

fn close_button(ui: &mut Ui, p: Palette) -> egui::Response {
    let (rect, resp) = ui.allocate_exact_size(vec2(30.0, 30.0), Sense::click());
    if resp.hovered() {
        ui.painter().circle_filled(rect.center(), 15.0, p.card_hover);
    }
    let c = rect.center();
    let s = Stroke::new(1.6, if resp.hovered() { p.text_strong } else { p.text_dim });
    ui.painter().line_segment([c + vec2(-5.5, -5.5), c + vec2(5.5, 5.5)], s);
    ui.painter().line_segment([c + vec2(5.5, -5.5), c + vec2(-5.5, 5.5)], s);
    resp.on_hover_cursor(egui::CursorIcon::PointingHand)
}

/// Small icons drawn with shapes (no icon font), so every app draws them the same.
#[derive(Clone, Copy)]
enum Glyph {
    Plus,
    Folder,
    Home,
    Play,
    Cap,
    Download,
    Dot,
    Facebook,
    Instagram,
    WhatsApp,
    Telegram,
}

impl Glyph {
    fn paint(self, painter: &egui::Painter, c: Pos2, size: f32, color: Color32) {
        let s = size / 2.0;
        let stroke = Stroke::new((size / 9.0).max(1.4), color);
        match self {
            Glyph::Plus => {
                painter.line_segment([c - vec2(s * 0.8, 0.0), c + vec2(s * 0.8, 0.0)], stroke);
                painter.line_segment([c - vec2(0.0, s * 0.8), c + vec2(0.0, s * 0.8)], stroke);
            }
            Glyph::Folder => {
                let body = Rect::from_center_size(c + vec2(0.0, s * 0.12), vec2(size * 0.95, size * 0.68));
                painter.rect_stroke(body, 2.0, stroke, egui::StrokeKind::Middle);
                painter.line_segment([body.left_top() + vec2(0.0, -s * 0.25), body.left_top() + vec2(s * 0.7, -s * 0.25)], stroke);
            }
            Glyph::Home => {
                let roof = [c + vec2(-s * 0.95, -s * 0.05), c + vec2(0.0, -s * 0.95), c + vec2(s * 0.95, -s * 0.05)];
                painter.add(egui::Shape::line(roof.to_vec(), stroke));
                painter.rect_stroke(Rect::from_min_max(c + vec2(-s * 0.65, -s * 0.15), c + vec2(s * 0.65, s * 0.9)), 1.0, stroke, egui::StrokeKind::Middle);
            }
            Glyph::Play => {
                painter.rect_stroke(Rect::from_center_size(c, vec2(size * 0.95, size * 0.75)), 2.0, stroke, egui::StrokeKind::Middle);
                painter.line_segment([c + vec2(-s * 0.95, -s * 0.3), c + vec2(s * 0.95, -s * 0.3)], stroke);
            }
            Glyph::Cap => {
                let top = vec![c + vec2(-s, -s * 0.2), c + vec2(0.0, -s * 0.75), c + vec2(s, -s * 0.2), c + vec2(0.0, s * 0.35)];
                painter.add(egui::Shape::convex_polygon(top, color, Stroke::NONE));
                painter.line_segment([c + vec2(-s * 0.55, s * 0.1), c + vec2(-s * 0.55, s * 0.7)], stroke);
                painter.line_segment([c + vec2(s * 0.55, s * 0.1), c + vec2(s * 0.55, s * 0.7)], stroke);
            }
            Glyph::Download => {
                painter.line_segment([c - vec2(0.0, s * 0.9), c + vec2(0.0, s * 0.35)], stroke);
                painter.add(egui::Shape::line(vec![c + vec2(-s * 0.5, -s * 0.1), c + vec2(0.0, s * 0.4), c + vec2(s * 0.5, -s * 0.1)], stroke));
                painter.line_segment([c + vec2(-s * 0.9, s * 0.85), c + vec2(s * 0.9, s * 0.85)], stroke);
            }
            Glyph::Dot => {
                painter.circle_filled(c, s * 0.35, color);
            }
            Glyph::Facebook => {
                let f = FontId::proportional(size * 1.05);
                painter.text(c + vec2(0.5, 0.5), Align2::CENTER_CENTER, "f", f, color);
            }
            Glyph::Instagram => {
                painter.rect_stroke(Rect::from_center_size(c, Vec2::splat(size * 0.8)), size * 0.22, stroke, egui::StrokeKind::Middle);
                painter.circle_stroke(c, s * 0.38, stroke);
                painter.circle_filled(c + vec2(s * 0.48, -s * 0.48), s * 0.1, color);
            }
            Glyph::WhatsApp => {
                painter.circle_stroke(c, s * 0.82, stroke);
                painter.add(egui::Shape::convex_polygon(vec![c + vec2(-s * 0.75, s * 0.45), c + vec2(-s * 0.95, s * 0.98), c + vec2(-s * 0.35, s * 0.8)], color, Stroke::NONE));
            }
            Glyph::Telegram => {
                // A paper plane.
                let pts = vec![c + vec2(-s * 0.95, -s * 0.05), c + vec2(s * 0.95, -s * 0.8), c + vec2(s * 0.45, s * 0.85)];
                painter.add(egui::Shape::convex_polygon(pts, color, Stroke::NONE));
                painter.line_segment([c + vec2(-s * 0.1, s * 0.2), c + vec2(s * 0.95, -s * 0.8)], Stroke::new(stroke.width * 0.8, Color32::from_black_alpha(90)));
            }
        }
    }
}
