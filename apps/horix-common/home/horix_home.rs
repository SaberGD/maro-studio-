//! HORIX Home: the start screen of every HORIX app (HORIX, HORIX Vectors, HORIX Layout, HORIX
//! Light), after the HORIX Saber Group UI Kit: a sidebar with New and Open, Home, Workspace,
//! Courses and the HORIX family; then the page with the drop area, the recent files, the tools
//! the app starts with and Saber Group Academy's band. Workspace (or Esc) leaves the empty
//! workspace, as Photoshop's Home does.
//!
//! One file, copied into each app's UI crate by its rebrand.py with its assets
//! (apps/horix-common/home/), so the apps share it without a new crate: it needs egui only. The
//! app supplies its names, recent files and tools, and acts on the [`Action`] that comes back.
//! Its colours are HORIX's own dark theme, the same in every app.

use egui::epaint::text::{FontInsert, FontPriority, InsertFontFamily};
use egui::{Align2, Color32, CornerRadius, FontFamily, FontId, Pos2, Rect, Sense, Stroke, StrokeKind, Ui, UiBuilder, pos2, vec2};

pub const FACEBOOK: &str = "https://www.facebook.com/sabergroup.academy/";
pub const INSTAGRAM: &str = "https://www.instagram.com/sabergroup.academy";
pub const TELEGRAM: &str = "https://t.me/SABERGROUPEG";
/// WhatsApp, with a ready message ("Hello, I am coming from HORIX and want to know about the
/// courses and services").
pub const WHATSAPP: &str = "https://wa.me/201040784390?text=%D9%85%D8%B1%D8%AD%D8%A8%D9%8B%D8%A7%D8%8C%20%D8%AC%D8%A7%D9%8A%20%D9%85%D9%86%20HORIX%20%D9%88%D8%B9%D8%A7%D9%8A%D8%B2%20%D8%A3%D8%B9%D8%B1%D9%81%20%D8%B9%D9%86%20%D8%A7%D9%84%D9%83%D9%88%D8%B1%D8%B3%D8%A7%D8%AA%20%D9%88%D8%A7%D9%84%D8%AE%D8%AF%D9%85%D8%A7%D8%AA";
pub const DOWNLOADS: &str = "https://horix.si/";

/// The HORIX family, for the sidebar: (id, name, icon, web address).
pub const FAMILY: &[(&str, &str, Icon, &str)] = &[
    ("horix-one", "HORIX One", Icon::Layers, "https://one.horix.live/"),
    ("horix", "HORIX", Icon::Image, "https://horix.live/"),
    ("horix-vectors", "HORIX Vectors", Icon::Pen, "https://vectors.horix.live/"),
    ("horix-layout", "HORIX Layout", Icon::Book, "https://layout.horix.live/"),
    ("horix-light", "HORIX Light", Icon::Camera, "https://light.horix.live/"),
];

// HORIX's own dark theme (the same in every HORIX app): Horus Ink, its greys, Falcon Ivory for
// what is primary and Vision Amber for what is on. Saber Group's wordmark keeps its red.
const INK: Color32 = Color32::from_rgb(0x0e, 0x0e, 0x0f);
const SIDEBAR: Color32 = Color32::from_rgb(0x14, 0x14, 0x15);
const SURFACE: Color32 = Color32::from_rgb(0x1a, 0x1a, 0x1c);
const CARD: Color32 = Color32::from_rgb(0x1a, 0x1a, 0x1c);
const RAISED: Color32 = Color32::from_rgb(0x2c, 0x2c, 0x30);
const SECONDARY: Color32 = Color32::from_rgb(0x17, 0x17, 0x19);
const BORDER: Color32 = Color32::from_rgb(0x28, 0x28, 0x2c);
const BORDER_STRONG: Color32 = Color32::from_rgb(0x3a, 0x3a, 0x40);
const BORDER_HOVER: Color32 = Color32::from_rgb(0x5a, 0x5a, 0x63);
const TEXT: Color32 = Color32::from_rgb(0xf3, 0xef, 0xe8);
const TEXT_NAV: Color32 = Color32::from_rgb(0xc4, 0xc4, 0xcc);
const MUTED: Color32 = Color32::from_rgb(0x96, 0x96, 0x9e);
const FAINT: Color32 = Color32::from_rgb(0x8a, 0x8a, 0x92);
/// Falcon Ivory: primary buttons, with Horus Ink lettering.
const PRIMARY: Color32 = Color32::from_rgb(0xf3, 0xef, 0xe8);
const ON_PRIMARY: Color32 = Color32::from_rgb(0x14, 0x13, 0x14);
/// Vision Amber: what is on, and what the pointer is over.
const AMBER: Color32 = Color32::from_rgb(0xea, 0x99, 0x3f);
const RED_WORDMARK: Color32 = Color32::from_rgb(0xed, 0x4b, 0x3e);
const THUMB: Color32 = Color32::from_rgb(0x23, 0x23, 0x26);
const SIDEBAR_W: f32 = 232.0;
/// Sharp corners, as HORIX's.
const RADIUS: u8 = 4;

/// The kit's icons, in assets/icons.a8's order (make_assets.py's ICONS).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Icon {
    Plus,
    Folder,
    Home,
    Workspace,
    Courses,
    External,
    Layers,
    Image,
    Pen,
    Book,
    Camera,
    Globe,
    Arrow,
    File,
    More,
    Grid,
    List,
    Upload,
    Sparkles,
    Masks,
    Brush,
    Type,
    Files,
    Columns,
    Print,
    Sliders,
    WhatsApp,
    Facebook,
    Instagram,
    Telegram,
    X,
    Check,
}

const ICON_PX: usize = 48;
const ICON_COLUMNS: usize = 8;
const ICON_ROWS: usize = 4;

/// One of the things the app starts with, as a card under "Start with a tool".
pub struct Tool<'a> {
    pub icon: Icon,
    pub title: &'a str,
    pub text: &'a str,
}

/// A recent file.
pub struct Recent {
    pub name: String,
    /// Its folder, or where it is kept.
    pub location: String,
    /// What it is ("PSD document", "Photo library").
    pub kind: String,
    /// The label on its picture ("PSD", "LIBRARY").
    pub badge: String,
    /// A preview, if the app has one.
    pub thumbnail: Option<egui::TextureId>,
    /// The thumbnail's width / height.
    pub aspect: f32,
    /// The thumbnail fills its card, cropped (photos); otherwise it shows whole (pages).
    pub fill: bool,
}

impl Recent {
    /// A recent file named `name` in `location`, its kind and badge from its extension.
    pub fn new(name: impl Into<String>, location: impl Into<String>) -> Self {
        let name = name.into();
        let ext = name.rsplit_once('.').map(|(_, e)| e.to_uppercase()).filter(|e| !e.is_empty() && e.len() <= 6).unwrap_or_default();
        let kind = if ext.is_empty() { "Document".to_owned() } else { format!("{ext} document") };
        Self { name, location: location.into(), kind, badge: ext, thumbnail: None, aspect: 1.0, fill: false }
    }
}

/// What the home screen asks the app to do.
#[derive(Clone, Debug, PartialEq)]
pub enum Action {
    New,
    Open,
    /// The recent file at this index.
    OpenRecent(usize),
    /// The tool card at this index.
    Tool(usize),
    /// Leave the home screen for the (empty) workspace.
    Workspace,
    /// Open this address in the browser.
    Url(String),
}

/// The app, as the home screen shows it.
pub struct Home<'a> {
    /// The app's family id (horix, horix-vectors, …): its place in the family list.
    pub id: &'a str,
    /// Its name ("HORIX Vectors").
    pub name: &'a str,
    pub version: &'a str,
    /// The page's title ("Make your next mark.").
    pub headline: &'a str,
    /// What it is, over the drop area ("THE VECTOR STUDIO").
    pub kicker: &'a str,
    /// The drop area's title ("Drop vector artwork to continue creating").
    pub drop_title: &'a str,
    pub drop_icon: Icon,
    /// What it opens ("AI / EPS / SVG / PDF").
    pub formats: &'a str,
    pub new_label: &'a str,
    pub open_label: &'a str,
    /// New's shortcut, as the menus show it ("Ctrl N").
    pub new_shortcut: &'a str,
    /// "Recent projects", "Recent libraries".
    pub recent_title: &'a str,
    pub recent: &'a [Recent],
    pub tools: &'a [Tool<'a>],
    /// In the browser: the family links open the web apps there.
    pub web: bool,
}

/// Draw the home screen over `ui`'s whole area. Returns what the person asked for.
pub fn show(ui: &mut Ui, home: &Home<'_>) -> Option<Action> {
    let mut action = None;
    let ctx = ui.ctx().clone();
    let k = Kit::get(&ctx);
    let full = ui.max_rect();
    ui.painter().rect_filled(full, 0.0, INK);
    let side = Rect::from_min_max(full.min, pos2(full.left() + SIDEBAR_W, full.bottom()));
    let main = Rect::from_min_max(pos2(side.right(), full.top()), full.max);
    grid_lines(ui.painter(), main);
    ui.scope_builder(UiBuilder::new().max_rect(side), |ui| sidebar(ui, &k, home, &mut action));
    ui.scope_builder(UiBuilder::new().max_rect(main), |ui| {
        egui::ScrollArea::vertical().id_salt("horix-home-main").auto_shrink([false, false]).show(ui, |ui| {
            egui::Frame::NONE.inner_margin(egui::Margin { left: 36, right: 36, top: 28, bottom: 0 }).show(ui, |ui| {
                ui.set_max_width(ui.available_width().min(1480.0));
                ui.spacing_mut().item_spacing = vec2(0.0, 0.0);
                page(ui, &k, home, &mut action);
            });
        });
    });
    // Esc goes to the workspace, as closing Photoshop's home does.
    if ui.input(|i| i.key_pressed(egui::Key::Escape)) && action.is_none() {
        action = Some(Action::Workspace);
    }
    action
}

/// The kit's icons and faces on this context.
struct Kit {
    icons: egui::TextureHandle,
    /// The faces are installed (the app's own font setup can replace them; they come back the
    /// next frame, and the app's face stands in meanwhile).
    fonts: bool,
}

const FACES: &[(&str, &[u8])] = &[
    ("horix-home-400", include_bytes!("horix_home_assets/inter-400.ttf")),
    ("horix-home-500", include_bytes!("horix_home_assets/inter-500.ttf")),
    ("horix-home-600", include_bytes!("horix_home_assets/inter-600.ttf")),
    ("horix-home-display", include_bytes!("horix_home_assets/barlow-condensed-700.ttf")),
];

impl Kit {
    fn get(ctx: &egui::Context) -> Self {
        let id = egui::Id::new("horix-home-icons");
        let icons = ctx.data_mut(|d| d.get_temp::<egui::TextureHandle>(id)).unwrap_or_else(|| {
            let alpha: &[u8] = include_bytes!("horix_home_assets/icons.a8");
            let rgba: Vec<u8> = alpha.iter().flat_map(|a| [255, 255, 255, *a]).collect();
            let image = egui::ColorImage::from_rgba_unmultiplied([ICON_COLUMNS * ICON_PX, ICON_ROWS * ICON_PX], &rgba);
            let tex = ctx.load_texture("horix-home-icons", image, egui::TextureOptions::LINEAR);
            ctx.data_mut(|d| d.insert_temp(id, tex.clone()));
            tex
        });
        let families = ctx.fonts(|f| f.families());
        let fonts = FACES.iter().all(|(name, _)| families.contains(&FontFamily::Name((*name).into())));
        if !fonts {
            for (name, bytes) in FACES {
                ctx.add_font(FontInsert::new(
                    name,
                    egui::FontData::from_static(bytes),
                    vec![InsertFontFamily { family: FontFamily::Name((*name).into()), priority: FontPriority::Highest }],
                ));
            }
            ctx.request_repaint();
        }
        Self { icons, fonts }
    }

    /// The kit's face at `weight` (400, 500, 600; 700 is the display face).
    fn font(&self, weight: u16, size: f32) -> FontId {
        if !self.fonts {
            return FontId::proportional(size);
        }
        let name = match weight {
            0..=449 => "horix-home-400",
            450..=549 => "horix-home-500",
            550..=649 => "horix-home-600",
            _ => "horix-home-display",
        };
        FontId::new(size, FontFamily::Name(name.into()))
    }

    fn icon(&self, painter: &egui::Painter, center: Pos2, size: f32, icon: Icon, color: Color32) {
        let i = icon as usize;
        let (col, row) = ((i % ICON_COLUMNS) as f32, (i / ICON_COLUMNS) as f32);
        let (w, h) = (ICON_COLUMNS as f32, ICON_ROWS as f32);
        let uv = Rect::from_min_max(pos2(col / w, row / h), pos2((col + 1.0) / w, (row + 1.0) / h));
        painter.image(self.icons.id(), Rect::from_center_size(center, vec2(size, size)), uv, color);
    }
}

/// The page's fine 64-point grid, fading out downwards.
fn grid_lines(painter: &egui::Painter, r: Rect) {
    let painter = painter.with_clip_rect(r);
    let fade = |y: f32| (1.0 - ((y - r.top()) / r.height().max(1.0)) / 0.95).clamp(0.0, 1.0);
    let line = |a: f32| Stroke::new(1.0, Color32::from_white_alpha((5.4 * a) as u8));
    let mut x = r.left();
    while x < r.right() {
        // Vertical lines fade in steps, as the kit's mask does.
        for step in 0..8 {
            let y0 = r.top() + r.height() * step as f32 / 8.0;
            let y1 = r.top() + r.height() * (step + 1) as f32 / 8.0;
            painter.vline(x, y0..=y1, line(fade((y0 + y1) / 2.0)));
        }
        x += 64.0;
    }
    let mut y = r.top();
    while y < r.bottom() {
        painter.hline(r.x_range(), y, line(fade(y)));
        y += 64.0;
    }
}

fn hand(resp: egui::Response) -> egui::Response {
    resp.on_hover_cursor(egui::CursorIcon::PointingHand)
}

fn sidebar(ui: &mut Ui, k: &Kit, home: &Home<'_>, action: &mut Option<Action>) {
    let r = ui.max_rect();
    let p = ui.painter().clone();
    p.rect_filled(r, 0.0, SIDEBAR);
    p.vline(r.right() - 0.5, r.y_range(), Stroke::new(1.0, BORDER));
    let inner = Rect::from_min_max(r.min + vec2(17.0, 26.0), r.max - vec2(17.0, 18.0));
    let w = inner.width();
    let mut y = inner.top();
    // New and Open.
    let new = Rect::from_min_size(pos2(inner.left(), y), vec2(w, 42.0));
    if hand(ui.interact(new, ui.id().with("new"), Sense::click())).clicked() {
        *action = Some(Action::New);
    }
    let hovered = ui.rect_contains_pointer(new);
    p.rect_filled(new, RADIUS, if hovered { AMBER } else { PRIMARY });
    k.icon(&p, pos2(new.left() + 20.0, new.center().y), 17.0, Icon::Plus, ON_PRIMARY);
    p.text(pos2(new.left() + 37.0, new.center().y), Align2::LEFT_CENTER, home.new_label, k.font(600, 12.5), ON_PRIMARY);
    p.text(pos2(new.right() - 14.0, new.center().y), Align2::RIGHT_CENTER, home.new_shortcut, k.font(400, 10.0), ON_PRIMARY.gamma_multiply(0.7));
    y = new.bottom() + 10.0;
    let open = Rect::from_min_size(pos2(inner.left(), y), vec2(w, 42.0));
    if hand(ui.interact(open, ui.id().with("open"), Sense::click())).clicked() {
        *action = Some(Action::Open);
    }
    secondary_button(ui, k, open, Icon::Folder, home.open_label, 12.5);
    y = open.bottom() + 22.0;
    // Home, Workspace, Courses.
    let items = [(Icon::Home, "Home", None), (Icon::Workspace, "Workspace", Some(Action::Workspace)), (Icon::Courses, "Courses", Some(Action::Url(WHATSAPP.into())))];
    for (i, (icon, label, go)) in items.into_iter().enumerate() {
        let item = Rect::from_min_size(pos2(inner.left(), y), vec2(w, 42.0));
        let resp = hand(ui.interact(item, ui.id().with(("nav", i)), Sense::click()));
        let selected = go.is_none();
        if selected {
            p.rect_filled(item, 3.0, Color32::from_rgba_unmultiplied(0xea, 0x99, 0x3f, 0x16));
            p.rect_filled(Rect::from_min_size(pos2(r.left(), item.center().y - 12.0), vec2(3.0, 24.0)), CornerRadius { ne: 1, se: 1, ..Default::default() }, AMBER);
        } else if resp.hovered() {
            p.rect_filled(item, 3.0, RAISED);
        }
        let color = if selected { AMBER } else { TEXT_NAV.gamma_multiply(0.9) };
        k.icon(&p, pos2(item.left() + 22.0, item.center().y), 20.0, icon, color);
        let text = if selected || resp.hovered() { TEXT } else { TEXT_NAV };
        p.text(pos2(item.left() + 44.0, item.center().y), Align2::LEFT_CENTER, label, k.font(400, 13.0), text);
        if icon == Icon::Courses {
            k.icon(&p, pos2(item.right() - 18.0, item.center().y), 13.0, Icon::External, MUTED.gamma_multiply(0.7));
        }
        if resp.clicked()
            && let Some(go) = go
        {
            *action = Some(go);
        }
        let resp = if icon == Icon::Courses { resp.on_hover_text("Saber Group Academy on WhatsApp") } else { resp };
        let _ = resp;
        y = item.bottom() + 6.0;
    }
    y += 18.0;
    p.hline(inner.x_range(), y, Stroke::new(1.0, BORDER));
    // The HORIX family.
    y += 24.0;
    p.text(pos2(inner.left() + 12.0, y), Align2::LEFT_TOP, "HORIX FAMILY", k.font(400, 10.0), Color32::from_rgb(0x99, 0x99, 0xa3));
    y += 26.0;
    for (id, name, icon, url) in FAMILY {
        let item = Rect::from_min_size(pos2(inner.left(), y), vec2(w, 42.0));
        let current = *id == home.id;
        let resp = ui.interact(item, ui.id().with(("family", *id)), if current { Sense::hover() } else { Sense::click() });
        if current {
            p.rect_filled(item, 3.0, Color32::from_white_alpha(4));
            p.circle_filled(pos2(item.right() - 14.0, item.center().y), 2.5, AMBER);
        } else if resp.hovered() {
            p.rect_filled(item, 3.0, RAISED);
        }
        k.icon(&p, pos2(item.left() + 21.0, item.center().y), 18.0, *icon, TEXT_NAV.gamma_multiply(0.7));
        let text = if current || resp.hovered() { TEXT } else { TEXT_NAV };
        p.text(pos2(item.left() + 42.0, item.center().y), Align2::LEFT_CENTER, *name, k.font(400, 12.5), text);
        if *id == "horix-one" && !current {
            k.icon(&p, pos2(item.right() - 18.0, item.center().y), 13.0, Icon::External, MUTED.gamma_multiply(0.7));
        }
        if !current && hand(resp).on_hover_text(if home.web { *url } else { "Open it in the browser, or get it at horix.si" }).clicked() {
            *action = Some(Action::Url((*url).into()));
        }
        y = item.bottom() + 3.0;
    }
    // The community link and the product line at the foot, when there is room.
    let caption_top = inner.bottom() - 34.0;
    let community = Rect::from_min_max(pos2(inner.left(), caption_top - 62.0), pos2(inner.right(), caption_top - 12.0));
    if community.top() > y + 20.0 {
        p.hline(inner.x_range(), community.top(), Stroke::new(1.0, BORDER));
        let resp = hand(ui.interact(community, ui.id().with("community"), Sense::click())).on_hover_text("Join us on Telegram");
        let c = if resp.hovered() { TEXT } else { TEXT_NAV };
        k.icon(&p, pos2(community.left() + 16.0, community.center().y), 16.0, Icon::Globe, c.gamma_multiply(0.8));
        p.text(pos2(community.left() + 32.0, community.center().y), Align2::LEFT_CENTER, "Our community", k.font(400, 12.5), c);
        k.icon(&p, pos2(community.right() - 14.0, community.center().y), 16.0, Icon::Arrow, c.gamma_multiply(0.8));
        if resp.clicked() {
            *action = Some(Action::Url(TELEGRAM.into()));
        }
        p.text(pos2(inner.left() + 8.0, caption_top), Align2::LEFT_TOP, "A SABER GROUP PRODUCT", k.font(400, 9.5), Color32::from_rgb(0xa1, 0xa1, 0xaa));
        p.text(pos2(inner.left() + 8.0, caption_top + 18.0), Align2::LEFT_TOP, format!("{} {} / Home", home.name, home.version), k.font(400, 10.0), Color32::from_rgb(0x91, 0x91, 0x9c));
    }
}

/// A bordered button (Open), its icon and label centred.
fn secondary_button(ui: &Ui, k: &Kit, rect: Rect, icon: Icon, label: &str, size: f32) {
    let p = ui.painter();
    let hovered = ui.rect_contains_pointer(rect);
    p.rect_filled(rect, RADIUS, if hovered { Color32::from_rgb(0x23, 0x23, 0x26) } else { SECONDARY });
    p.rect_stroke(rect, RADIUS, Stroke::new(1.0, if hovered { Color32::from_rgb(0x68, 0x68, 0x6f) } else { BORDER_STRONG }), StrokeKind::Inside);
    centered_label(ui, k, rect, Some(icon), label, size, TEXT);
}

/// An icon and a label, centred together in `rect`.
fn centered_label(ui: &Ui, k: &Kit, rect: Rect, icon: Option<Icon>, label: &str, size: f32, color: Color32) {
    let p = ui.painter();
    let galley = p.layout_no_wrap(label.to_owned(), k.font(500, size), color);
    let icon_w = if icon.is_some() { 17.0 + 9.0 } else { 0.0 };
    let x = rect.center().x - (icon_w + galley.size().x) / 2.0;
    if let Some(icon) = icon {
        k.icon(p, pos2(x + 8.5, rect.center().y), 17.0, icon, color);
    }
    p.galley(pos2(x + icon_w, rect.center().y - galley.size().y / 2.0), galley, color);
}

fn page(ui: &mut Ui, k: &Kit, home: &Home<'_>, action: &mut Option<Action>) {
    heading(ui, k, home, action);
    ui.add_space(24.0);
    drop_area(ui, k, home, action);
    ui.add_space(23.0);
    recent(ui, k, home, action);
    ui.add_space(22.0);
    tools(ui, k, home, action);
    ui.add_space(22.0);
    academy(ui, k, action);
    // The credit line.
    let (r, _) = ui.allocate_exact_size(vec2(ui.available_width(), 46.0), Sense::hover());
    ui.painter().text(
        r.center(),
        Align2::CENTER_CENTER,
        "Developed by Eng. Mohamed Saber  ·  SABER GROUP",
        k.font(400, 9.5),
        Color32::from_rgb(0x9c, 0x9c, 0xa6),
    );
}

fn heading(ui: &mut Ui, k: &Kit, home: &Home<'_>, action: &mut Option<Action>) {
    let w = ui.available_width();
    let (r, _) = ui.allocate_exact_size(vec2(w, 62.0), Sense::hover());
    let p = ui.painter();
    // HOME / HORIX VECTORS
    let crumb = p.layout_no_wrap("HOME".into(), k.font(600, 10.0), AMBER);
    let cw = crumb.size().x;
    p.galley(r.min, crumb, AMBER);
    p.text(pos2(r.left() + cw + 7.0, r.top()), Align2::LEFT_TOP, "/", k.font(400, 10.0), Color32::from_rgb(0x68, 0x68, 0x72));
    p.text(pos2(r.left() + cw + 19.0, r.top()), Align2::LEFT_TOP, home.name.to_uppercase(), k.font(600, 10.0), AMBER);
    p.text(pos2(r.left(), r.top() + 20.0), Align2::LEFT_TOP, home.headline, k.font(600, 30.0), TEXT);
    // Open workspace →, and Telegram before it.
    let row_y = r.top() + 34.0;
    let open = text_action(ui, k, pos2(r.right(), row_y), "Open workspace", Icon::Arrow, "open-workspace");
    if open.on_hover_text("The workspace, without a document (Esc)").clicked() {
        *action = Some(Action::Workspace);
    }
    let left = r.right() - text_action_width(ui, k, "Open workspace") - 22.0;
    if telegram_pill(ui, k, pos2(left, row_y)).on_hover_text(TELEGRAM).clicked() {
        *action = Some(Action::Url(TELEGRAM.into()));
    }
}

fn text_action_width(ui: &Ui, k: &Kit, label: &str) -> f32 {
    ui.painter().layout_no_wrap(label.to_owned(), k.font(400, 12.5), TEXT).size().x + 12.0 + 17.0
}

/// A label with an icon after it, right-aligned at `right_center`.
fn text_action(ui: &Ui, k: &Kit, right_center: Pos2, label: &str, icon: Icon, id: &str) -> egui::Response {
    let w = text_action_width(ui, k, label);
    let rect = Rect::from_min_size(pos2(right_center.x - w, right_center.y - 14.0), vec2(w, 28.0));
    let resp = hand(ui.interact(rect, ui.id().with(id), Sense::click()));
    let c = if resp.hovered() { TEXT } else { Color32::from_rgb(0xd4, 0xd4, 0xda) };
    let p = ui.painter();
    p.text(pos2(rect.left(), rect.center().y), Align2::LEFT_CENTER, label, k.font(400, 12.5), c);
    k.icon(p, pos2(rect.right() - 8.5, rect.center().y), 17.0, icon, c.gamma_multiply(if resp.hovered() { 1.0 } else { 0.65 }));
    resp
}

/// "Join us on Telegram", ending at `right_center`.
fn telegram_pill(ui: &Ui, k: &Kit, right_center: Pos2) -> egui::Response {
    let label = "Join us on Telegram";
    let galley = ui.painter().layout_no_wrap(label.into(), k.font(500, 11.5), TEXT);
    let w = galley.size().x + 15.0 + 8.0 + 24.0;
    let rect = Rect::from_min_size(pos2(right_center.x - w, right_center.y - 15.0), vec2(w, 30.0));
    let resp = hand(ui.interact(rect, ui.id().with("telegram"), Sense::click()));
    let p = ui.painter();
    p.rect_filled(rect, 4.0, if resp.hovered() { Color32::from_rgba_unmultiplied(0xea, 0x99, 0x3f, 0x14) } else { Color32::TRANSPARENT });
    p.rect_stroke(rect, 4.0, Stroke::new(1.0, if resp.hovered() { AMBER } else { Color32::from_rgb(0x4c, 0x4c, 0x55) }), StrokeKind::Inside);
    k.icon(p, pos2(rect.left() + 12.0 + 7.5, rect.center().y), 15.0, Icon::Telegram, TEXT);
    p.galley(pos2(rect.left() + 12.0 + 15.0 + 8.0, rect.center().y - galley.size().y / 2.0), galley, TEXT);
    resp
}

fn drop_area(ui: &mut Ui, k: &Kit, home: &Home<'_>, action: &mut Option<Action>) {
    let w = ui.available_width();
    let (r, _) = ui.allocate_exact_size(vec2(w, 212.0), Sense::hover());
    let dragging = ui.ctx().input(|i| !i.raw.hovered_files.is_empty());
    let p = ui.painter().clone();
    p.rect_filled(r, 3.0, if dragging { Color32::from_rgba_unmultiplied(0xea, 0x99, 0x3f, 0x12) } else { Color32::from_rgba_unmultiplied(0x17, 0x17, 0x19, 0x4d) });
    dashed_rect(&p, r, if dragging { AMBER } else { Color32::from_rgb(0x4b, 0x4b, 0x53) });
    // Registration marks at the corners.
    for c in [r.left_top(), r.right_top(), r.left_bottom(), r.right_bottom()] {
        let s = Stroke::new(1.0, Color32::from_rgba_unmultiplied(0x67, 0x67, 0x70, 128));
        p.hline((c.x - 5.5)..=(c.x + 5.5), c.y, s);
        p.vline(c.x, (c.y - 5.5)..=(c.y + 5.5), s);
    }
    let cx = r.center().x;
    let mut y = r.top() + 30.0;
    // The app's icon with a red plus.
    let icon_c = pos2(cx, y + 17.0);
    k.icon(&p, icon_c, 34.0, home.drop_icon, TEXT.gamma_multiply(0.78));
    let badge = icon_c + vec2(13.0, 12.0);
    p.circle_filled(badge, 10.0, Color32::from_rgb(0x19, 0x19, 0x1c));
    p.circle_filled(badge, 8.0, AMBER);
    k.icon(&p, badge, 11.0, Icon::Plus, ON_PRIMARY);
    y += 34.0 + 12.0;
    p.text(pos2(cx, y), Align2::CENTER_TOP, home.kicker, k.font(400, 9.5), FAINT);
    y += 18.0;
    let title = if dragging { "Drop to open" } else { home.drop_title };
    p.text(pos2(cx, y), Align2::CENTER_TOP, title, k.font(500, 17.0), TEXT);
    y += 24.0 + 15.0;
    let bw = 160.0;
    let new = Rect::from_min_size(pos2(cx - 5.0 - bw, y), vec2(bw, 37.0));
    let open = Rect::from_min_size(pos2(cx + 5.0, y), vec2(bw, 37.0));
    let new_resp = hand(ui.interact(new, ui.id().with("drop-new"), Sense::click()));
    p.rect_filled(new, RADIUS, if new_resp.hovered() { AMBER } else { PRIMARY });
    centered_label(ui, k, new, Some(Icon::Plus), home.new_label, 12.5, ON_PRIMARY);
    if new_resp.clicked() {
        *action = Some(Action::New);
    }
    if hand(ui.interact(open, ui.id().with("drop-open"), Sense::click())).clicked() {
        *action = Some(Action::Open);
    }
    secondary_button(ui, k, open, Icon::Folder, home.open_label, 12.5);
    y += 37.0 + 13.0;
    p.text(pos2(cx, y), Align2::CENTER_TOP, home.formats, k.font(400, 9.5), Color32::from_rgb(0x9f, 0x9f, 0xa9));
    // Drag & drop, at the bottom right.
    let corner = pos2(r.right() - 15.0, r.bottom() - 14.0);
    let label = p.layout_no_wrap("Drag & drop".into(), k.font(400, 9.5), Color32::from_rgb(0xa3, 0xa3, 0xac));
    let lw = label.size().x;
    p.galley(pos2(corner.x - lw, corner.y - label.size().y / 2.0), label, Color32::from_rgb(0xa3, 0xa3, 0xac));
    k.icon(&p, pos2(corner.x - lw - 12.0, corner.y), 12.0, Icon::Upload, MUTED.gamma_multiply(0.6));
}

fn dashed_rect(p: &egui::Painter, r: Rect, color: Color32) {
    let stroke = Stroke::new(1.0, color);
    let r = r.shrink(0.5);
    let pts = [r.left_top(), r.right_top(), r.right_bottom(), r.left_bottom(), r.left_top()];
    p.extend(egui::Shape::dashed_line(&pts, stroke, 4.0, 3.0));
}

/// Grid or list, for the recent files (kept for the session).
fn list_view(ctx: &egui::Context) -> bool {
    ctx.data(|d| d.get_temp::<bool>(egui::Id::new("horix-home-list"))).unwrap_or(false)
}

fn columns(w: f32) -> usize {
    if w >= 860.0 {
        3
    } else if w >= 540.0 {
        2
    } else {
        1
    }
}

fn recent(ui: &mut Ui, k: &Kit, home: &Home<'_>, action: &mut Option<Action>) {
    let w = ui.available_width();
    let ctx = ui.ctx().clone();
    let list = list_view(&ctx);
    // The heading: the title, how many, and the grid / list switch.
    let (h, _) = ui.allocate_exact_size(vec2(w, 30.0), Sense::hover());
    let p = ui.painter().clone();
    p.text(pos2(h.left(), h.center().y), Align2::LEFT_CENTER, home.recent_title, k.font(500, 16.0), TEXT);
    let mut x = h.right();
    for (icon, is_list) in [(Icon::List, true), (Icon::Grid, false)] {
        let b = Rect::from_min_size(pos2(x - 28.0, h.center().y - 14.0), vec2(28.0, 28.0));
        let resp = hand(ui.interact(b, ui.id().with(("view", is_list)), Sense::click()));
        if resp.hovered() {
            p.rect_filled(b, 3.0, RAISED);
        }
        let on = list == is_list;
        k.icon(&p, b.center(), 16.0, icon, if on { TEXT } else { TEXT.gamma_multiply(0.6) });
        if on {
            p.hline((b.left() + 7.0)..=(b.right() - 7.0), b.bottom() - 1.0, Stroke::new(2.0, AMBER));
        }
        if resp.on_hover_text(if is_list { "List" } else { "Grid" }).clicked() {
            ctx.data_mut(|d| d.insert_temp(egui::Id::new("horix-home-list"), is_list));
        }
        x -= 32.0;
    }
    if !home.recent.is_empty() {
        let n = home.recent.len();
        let count = format!("{n} RECENT {}", if n == 1 { "FILE" } else { "FILES" });
        p.text(pos2(x - 8.0, h.center().y), Align2::RIGHT_CENTER, count, k.font(400, 8.5), Color32::from_rgb(0xa0, 0xa0, 0xaa));
    }
    ui.add_space(12.0);
    if home.recent.is_empty() {
        let (r, _) = ui.allocate_exact_size(vec2(w, 96.0), Sense::hover());
        p.rect_filled(r, RADIUS, SURFACE);
        p.rect_stroke(r, RADIUS, Stroke::new(1.0, BORDER), StrokeKind::Inside);
        k.icon(&p, pos2(r.left() + 34.0, r.center().y), 24.0, Icon::Files, MUTED.gamma_multiply(0.8));
        p.text(pos2(r.left() + 62.0, r.center().y - 10.0), Align2::LEFT_CENTER, "No recent files yet", k.font(500, 13.0), TEXT);
        p.text(
            pos2(r.left() + 62.0, r.center().y + 10.0),
            Align2::LEFT_CENTER,
            format!("Files you open or save in {} show up here.", home.name),
            k.font(400, 11.0),
            MUTED,
        );
        return;
    }
    let shown = &home.recent[..home.recent.len().min(if list { 8 } else { 6 })];
    let cols = if list { 1 } else { columns(w) };
    let gap = 14.0;
    let cw = (w - gap * (cols as f32 - 1.0)) / cols as f32;
    let ch = if list { 62.0 } else { 162.0 + 56.0 };
    for (row, chunk) in shown.chunks(cols).enumerate() {
        if row > 0 {
            ui.add_space(if list { 8.0 } else { gap });
        }
        let (rr, _) = ui.allocate_exact_size(vec2(w, ch), Sense::hover());
        for (c, item) in chunk.iter().enumerate() {
            let i = row * cols + c;
            let card = Rect::from_min_size(pos2(rr.left() + c as f32 * (cw + gap), rr.top()), vec2(cw, ch));
            if recent_card(ui, k, card, item, i, list, action) {
                *action = Some(Action::OpenRecent(i));
            }
        }
    }
}

/// A recent file's card; true when it was clicked.
fn recent_card(ui: &Ui, k: &Kit, card: Rect, item: &Recent, i: usize, list: bool, action: &mut Option<Action>) -> bool {
    let resp = hand(ui.interact(card, ui.id().with(("recent", i)), Sense::click()));
    let p = ui.painter().with_clip_rect(card.intersect(ui.clip_rect()));
    let hovered = resp.hovered();
    p.rect_filled(card, RADIUS, SURFACE);
    let image = if list { Rect::from_min_size(card.min, vec2(90.0, card.height())) } else { Rect::from_min_size(card.min, vec2(card.width(), 162.0)) };
    let rounding = if list { CornerRadius { nw: RADIUS, sw: RADIUS, ..Default::default() } } else { CornerRadius { nw: RADIUS, ne: RADIUS, ..Default::default() } };
    p.rect_filled(image, rounding, THUMB);
    match item.thumbnail {
        Some(tex) if item.fill => {
            // Cropped to the card, from the middle.
            let a = item.aspect.max(0.05);
            let r = image.width() / image.height();
            let (u, v) = if a > r { ((1.0 - r / a) / 2.0, 0.0) } else { (0.0, (1.0 - a / r) / 2.0) };
            let zoom = if hovered { 0.01 } else { 0.0 };
            let uv = Rect::from_min_max(pos2(u + zoom, v + zoom), pos2(1.0 - u - zoom, 1.0 - v - zoom));
            let shape = egui::epaint::RectShape::filled(image, rounding, Color32::WHITE).with_texture(tex, uv);
            p.add(shape);
        }
        Some(tex) => {
            // The page, whole, on the grey (as the kit shows publications).
            let a = item.aspect.max(0.05);
            let room = image.shrink(if list { 4.0 } else { 10.0 });
            let fit = if room.width() / room.height() > a { vec2(room.height() * a, room.height()) } else { vec2(room.width(), room.width() / a) };
            let fit = if hovered { fit * 1.02 } else { fit };
            p.image(tex, Rect::from_center_size(room.center(), fit), Rect::from_min_max(Pos2::ZERO, pos2(1.0, 1.0)), Color32::WHITE);
        }
        None => {
            let size = if list { 22.0 } else { 44.0 };
            k.icon(&p, image.center() - vec2(0.0, if list { 0.0 } else { 8.0 }), size, Icon::File, Color32::from_rgb(0x5c, 0x5c, 0x66));
            if !list && !item.badge.is_empty() {
                p.text(image.center() + vec2(0.0, 26.0), Align2::CENTER_CENTER, &item.badge, k.font(600, 11.0), Color32::from_rgb(0x7a, 0x7a, 0x84));
            }
        }
    }
    if !list && !item.badge.is_empty() {
        let g = p.layout_no_wrap(item.badge.clone(), k.font(400, 8.5), TEXT);
        let b = Rect::from_min_size(pos2(image.left() + 10.0, image.bottom() - 10.0 - g.size().y - 8.0), g.size() + vec2(12.0, 8.0));
        p.rect_filled(b, 3.0, Color32::from_rgba_unmultiplied(0x12, 0x12, 0x13, 0xc9));
        p.rect_stroke(b, 3.0, Stroke::new(1.0, Color32::from_white_alpha(0x26)), StrokeKind::Inside);
        p.galley(b.min + vec2(6.0, 4.0), g, TEXT);
    }
    let info = if list { Rect::from_min_max(pos2(image.right(), card.top()), card.max) } else { Rect::from_min_max(pos2(card.left(), image.bottom()), card.max) };
    k.icon(&p, pos2(info.left() + 20.5, info.center().y), 17.0, Icon::File, TEXT.gamma_multiply(0.75));
    let text_w = info.width() - 40.0 - 40.0;
    // Names and folders in the app's own face, which has the person's scripts.
    let name = elide(ui, &item.name, FontId::proportional(12.5), text_w);
    p.text(pos2(info.left() + 40.0, info.center().y - 8.5), Align2::LEFT_CENTER, name, FontId::proportional(12.5), TEXT);
    let sub = if list && !item.location.is_empty() { format!("{}  ·  {}", item.kind, item.location) } else { item.kind.clone() };
    let sub = elide(ui, &sub, FontId::proportional(10.5), text_w);
    p.text(pos2(info.left() + 40.0, info.center().y + 9.0), Align2::LEFT_CENTER, sub, FontId::proportional(10.5), MUTED);
    p.rect_stroke(card, RADIUS, Stroke::new(1.0, if hovered { BORDER_HOVER } else { BORDER }), StrokeKind::Inside);
    // "…": open, or copy where it is.
    let more = Rect::from_center_size(pos2(info.right() - 21.0, info.center().y), vec2(28.0, 28.0));
    let more_resp = hand(ui.interact(more, ui.id().with(("more", i)), Sense::click()));
    if more_resp.hovered() {
        p.rect_filled(more, 3.0, RAISED);
    }
    k.icon(&p, more.center(), 17.0, Icon::More, TEXT.gamma_multiply(0.8));
    egui::Popup::menu(&more_resp).show(|ui| {
        if ui.button("Open").clicked() {
            *action = Some(Action::OpenRecent(i));
        }
        if !item.location.is_empty() && ui.button("Copy location").clicked() {
            ui.ctx().copy_text(item.location.clone());
        }
    });
    let resp = resp.on_hover_text(if item.location.is_empty() { item.name.clone() } else { format!("{}\n{}", item.name, item.location) });
    resp.clicked() && !more_resp.clicked() && !more_resp.hovered()
}

fn tools(ui: &mut Ui, k: &Kit, home: &Home<'_>, action: &mut Option<Action>) {
    if home.tools.is_empty() {
        return;
    }
    let w = ui.available_width();
    let (h, _) = ui.allocate_exact_size(vec2(w, 44.0), Sense::hover());
    let p = ui.painter().clone();
    p.hline(h.x_range(), h.top(), Stroke::new(1.0, BORDER));
    p.text(pos2(h.left(), h.top() + 29.0), Align2::LEFT_CENTER, "Start with a tool", k.font(500, 16.0), TEXT);
    p.text(pos2(h.right(), h.top() + 29.0), Align2::RIGHT_CENTER, "Built for your next idea.", k.font(400, 10.5), MUTED);
    ui.add_space(10.0);
    let cols = columns(w).min(home.tools.len());
    let gap = 14.0;
    let cw = (w - gap * (cols as f32 - 1.0)) / cols as f32;
    for (row, chunk) in home.tools.chunks(cols).enumerate() {
        if row > 0 {
            ui.add_space(gap);
        }
        let (rr, _) = ui.allocate_exact_size(vec2(w, 74.0), Sense::hover());
        for (c, tool) in chunk.iter().enumerate() {
            let i = row * cols + c;
            let card = Rect::from_min_size(pos2(rr.left() + c as f32 * (cw + gap), rr.top()), vec2(cw, 74.0));
            let resp = hand(ui.interact(card, ui.id().with(("tool", i)), Sense::click()));
            let hovered = resp.hovered();
            p.rect_filled(card, RADIUS, if hovered { RAISED } else { CARD });
            p.rect_stroke(card, RADIUS, Stroke::new(1.0, if hovered { BORDER_HOVER } else { BORDER }), StrokeKind::Inside);
            k.icon(&p, pos2(card.left() + 14.0 + 13.5, card.center().y), 27.0, tool.icon, TEXT.gamma_multiply(0.85));
            let x = card.left() + 14.0 + 27.0 + 13.0;
            let text_w = card.right() - x - 40.0;
            p.text(pos2(x, card.center().y - 9.0), Align2::LEFT_CENTER, elide(ui, tool.title, k.font(500, 12.5), text_w), k.font(500, 12.5), TEXT);
            p.text(pos2(x, card.center().y + 10.0), Align2::LEFT_CENTER, elide(ui, tool.text, k.font(400, 10.5), text_w), k.font(400, 10.5), MUTED);
            k.icon(&p, pos2(card.right() - 24.0, card.center().y), 15.0, Icon::Arrow, TEXT.gamma_multiply(if hovered { 1.0 } else { 0.6 }));
            if resp.clicked() {
                *action = Some(Action::Tool(i));
            }
        }
    }
}

fn academy(ui: &mut Ui, k: &Kit, action: &mut Option<Action>) {
    let w = ui.available_width();
    let narrow = w < 760.0;
    let (r, _) = ui.allocate_exact_size(vec2(w, if narrow { 170.0 } else { 120.0 }), Sense::hover());
    let p = ui.painter().clone();
    p.rect_filled(r, RADIUS, CARD);
    p.rect_stroke(r, RADIUS, Stroke::new(1.0, BORDER), StrokeKind::Inside);
    p.rect_filled(Rect::from_min_max(pos2(r.left(), r.top() + 14.0), pos2(r.left() + 3.0, r.bottom() - 14.0)), CornerRadius { ne: 1, se: 1, ..Default::default() }, AMBER);
    // SABER GROUP  ACADEMY
    let x = r.left() + 24.0;
    let top = r.top() + 18.0;
    let mark = p.layout_no_wrap("SABER GROUP".into(), k.font(700, 21.0), RED_WORDMARK);
    let mw = mark.size().x;
    let mh = mark.size().y;
    p.galley(pos2(x, top), mark, RED_WORDMARK);
    p.text(pos2(x + mw + 9.0, top + mh - 3.0), Align2::LEFT_BOTTOM, "ACADEMY", k.font(400, 8.5), Color32::from_rgb(0xad, 0xad, 0xb5));
    p.text(pos2(x, top + mh + 6.0), Align2::LEFT_TOP, "Learn with the team behind HORIX.", k.font(500, 17.0), TEXT);
    p.text(pos2(x, top + mh + 32.0), Align2::LEFT_TOP, "Courses, workshops and creative support in Arabic.", k.font(400, 10.5), Color32::from_rgb(0xa8, 0xa8, 0xb2));
    // Explore courses →, and the accounts under it.
    let socials = [(Icon::WhatsApp, "WhatsApp", WHATSAPP), (Icon::Facebook, "Facebook", FACEBOOK), (Icon::Instagram, "Instagram", INSTAGRAM), (Icon::Telegram, "Telegram", TELEGRAM)];
    let social_w: Vec<f32> = socials.iter().map(|(_, l, _)| p.layout_no_wrap((*l).into(), k.font(400, 10.5), TEXT).size().x + 13.0 + 7.0).collect();
    let total: f32 = social_w.iter().sum::<f32>() + 18.0 * (socials.len() as f32 - 1.0);
    let (row_y, mut sx) = if narrow { (r.bottom() - 22.0, x) } else { (r.bottom() - 30.0, r.right() - 22.0 - total) };
    for ((icon, label, url), sw) in socials.iter().zip(&social_w) {
        let rect = Rect::from_min_size(pos2(sx, row_y - 10.0), vec2(*sw, 20.0));
        let resp = hand(ui.interact(rect, ui.id().with(("social", *label)), Sense::click()));
        let c = if resp.hovered() { TEXT } else { Color32::from_rgb(0xbc, 0xbc, 0xc5) };
        k.icon(&p, pos2(sx + 6.5, row_y), 13.0, *icon, c.gamma_multiply(if resp.hovered() { 1.0 } else { 0.85 }));
        p.text(pos2(sx + 20.0, row_y), Align2::LEFT_CENTER, *label, k.font(400, 10.5), c);
        if resp.on_hover_text(*url).clicked() {
            *action = Some(Action::Url((*url).into()));
        }
        sx += sw + 18.0;
    }
    let label = "Explore courses";
    let g = p.layout_no_wrap(label.into(), k.font(400, 11.5), TEXT);
    let bw = g.size().x + 18.0 + 15.0 + 24.0;
    let b = if narrow {
        Rect::from_min_size(pos2(x, row_y - 52.0), vec2(bw, 32.0))
    } else {
        Rect::from_min_size(pos2(r.right() - 22.0 - bw, r.top() + 22.0), vec2(bw, 32.0))
    };
    let resp = hand(ui.interact(b, ui.id().with("courses"), Sense::click()));
    p.rect_filled(b, 4.0, if resp.hovered() { Color32::from_rgba_unmultiplied(0xea, 0x99, 0x3f, 0x14) } else { Color32::TRANSPARENT });
    p.rect_stroke(b, 4.0, Stroke::new(1.0, if resp.hovered() { AMBER } else { Color32::from_rgb(0x4c, 0x4c, 0x55) }), StrokeKind::Inside);
    p.galley(pos2(b.left() + 12.0, b.center().y - g.size().y / 2.0), g, TEXT);
    k.icon(&p, pos2(b.right() - 12.0 - 7.5, b.center().y), 15.0, Icon::Arrow, TEXT);
    if resp.on_hover_text("Saber Group Academy on WhatsApp").clicked() {
        *action = Some(Action::Url(WHATSAPP.into()));
    }
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
