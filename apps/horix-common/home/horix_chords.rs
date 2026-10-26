//! HORIX Colour Chords, the same in every HORIX app (apps/horix-common/home/horix_chords.rs, copied
//! into each app's UI crate by horix_rebrand.install_home): colours that go with a base colour by
//! colour theory, as Affinity Designer's colour chords make them. Ten chords:
//!
//! - Complementary: the base and the hue opposite it.
//! - Split Complementary: the base and the two hues either side of its opposite.
//! - Analogous: the base and its neighbours either side.
//! - Accented Analogic: the base, its opposite and the opposite's neighbours.
//! - Triadic: three hues a third of the wheel apart.
//! - Tetradic: two complementary pairs, a twelfth of the wheel apart (a rectangle).
//! - Square: four hues a quarter of the wheel apart.
//! - Tints, Shades, Tones: the base toward white, black and grey, in seven steps.
//!
//! The hue chords turn the base around the HSL wheel and keep its saturation and lightness. The
//! panel section [`section`] shows the chosen chord as a strip: a click on a colour makes it the
//! app's colour, and Add to Swatches saves the chord as a swatch group of its own. The app does
//! both (`ChordAction`); this file only draws and does the colour theory.

use egui::{Color32, CornerRadius, Rect, Sense, Stroke, StrokeKind, Ui, vec2};

/// The colour chords, in Affinity's order.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Chord {
    Complementary,
    SplitComplementary,
    Analogous,
    AccentedAnalogic,
    Triadic,
    Tetradic,
    Square,
    Tints,
    Shades,
    Tones,
}

impl Chord {
    pub const ALL: [Chord; 10] = [
        Chord::Complementary,
        Chord::SplitComplementary,
        Chord::Analogous,
        Chord::AccentedAnalogic,
        Chord::Triadic,
        Chord::Tetradic,
        Chord::Square,
        Chord::Tints,
        Chord::Shades,
        Chord::Tones,
    ];

    pub fn name(self) -> &'static str {
        match self {
            Chord::Complementary => "Complementary",
            Chord::SplitComplementary => "Split Complementary",
            Chord::Analogous => "Analogous",
            Chord::AccentedAnalogic => "Accented Analogic",
            Chord::Triadic => "Triadic",
            Chord::Tetradic => "Tetradic",
            Chord::Square => "Square",
            Chord::Tints => "Tints",
            Chord::Shades => "Shades",
            Chord::Tones => "Tones",
        }
    }

    /// The hue turns (degrees) of a hue chord, the base's own (0) first.
    fn turns(self) -> &'static [f32] {
        match self {
            Chord::Complementary => &[0.0, 180.0],
            Chord::SplitComplementary => &[0.0, 150.0, 210.0],
            Chord::Analogous => &[-30.0, 0.0, 30.0],
            Chord::AccentedAnalogic => &[0.0, 150.0, 180.0, 210.0],
            Chord::Triadic => &[0.0, 120.0, 240.0],
            Chord::Tetradic => &[0.0, 30.0, 180.0, 210.0],
            Chord::Square => &[0.0, 90.0, 180.0, 270.0],
            Chord::Tints | Chord::Shades | Chord::Tones => &[],
        }
    }

    /// The chord's colours (sRGB, 0–1), the base first except for Analogous, whose base is in the
    /// middle as on the wheel.
    pub fn colors(self, base: [f32; 3]) -> Vec<[f32; 3]> {
        let base = base.map(|v| if v.is_finite() { v.clamp(0.0, 1.0) } else { 0.0 });
        let toward = |to: [f32; 3]| -> Vec<[f32; 3]> {
            (0..STEPS).map(|i| {
                let t = i as f32 / (STEPS - 1) as f32;
                [0, 1, 2].map(|k| base[k] + (to[k] - base[k]) * t)
            }).collect()
        };
        match self {
            Chord::Tints => toward([1.0; 3]),
            Chord::Shades => toward([0.0; 3]),
            Chord::Tones => toward([0.5; 3]),
            _ => {
                let (h, s, l) = rgb_to_hsl(base);
                self.turns().iter().map(|t| if *t == 0.0 { base } else { hsl_to_rgb(h + t, s, l) }).collect()
            }
        }
    }
}

/// Steps of Tints, Shades and Tones: the base, five between, and white, black or grey.
const STEPS: usize = 7;

/// sRGB (0–1) to hue (degrees), saturation and lightness (0–1).
pub fn rgb_to_hsl(c: [f32; 3]) -> (f32, f32, f32) {
    let [r, g, b] = c;
    let max = r.max(g).max(b);
    let min = r.min(g).min(b);
    let l = (max + min) / 2.0;
    let d = max - min;
    if d <= f32::EPSILON {
        return (0.0, 0.0, l);
    }
    let s = if l > 0.5 { d / (2.0 - max - min) } else { d / (max + min) };
    let h = if max == r {
        (g - b) / d + if g < b { 6.0 } else { 0.0 }
    } else if max == g {
        (b - r) / d + 2.0
    } else {
        (r - g) / d + 4.0
    };
    (h * 60.0, s, l)
}

/// Hue (degrees, any turn), saturation and lightness (0–1) to sRGB (0–1).
pub fn hsl_to_rgb(h: f32, s: f32, l: f32) -> [f32; 3] {
    let h = h.rem_euclid(360.0) / 360.0;
    if s <= 0.0 {
        return [l; 3];
    }
    let q = if l < 0.5 { l * (1.0 + s) } else { l + s - l * s };
    let p = 2.0 * l - q;
    let f = |t: f32| {
        let t = t.rem_euclid(1.0);
        if t < 1.0 / 6.0 {
            p + (q - p) * 6.0 * t
        } else if t < 0.5 {
            q
        } else if t < 2.0 / 3.0 {
            p + (q - p) * (2.0 / 3.0 - t) * 6.0
        } else {
            p
        }
    };
    [f(h + 1.0 / 3.0), f(h), f(h - 1.0 / 3.0)].map(|v| v.clamp(0.0, 1.0))
}

/// `#RRGGBB` of an sRGB colour.
pub fn hex(c: [f32; 3]) -> String {
    let [r, g, b] = c.map(|v| (v.clamp(0.0, 1.0) * 255.0).round() as u8);
    format!("#{r:02X}{g:02X}{b:02X}")
}

fn c32(c: [f32; 3]) -> Color32 {
    let [r, g, b] = c.map(|v| (v.clamp(0.0, 1.0) * 255.0).round() as u8);
    Color32::from_rgb(r, g, b)
}

/// What the person did in the section.
#[derive(Clone, Debug, PartialEq)]
pub enum ChordAction {
    /// Make this colour the app's colour.
    Use([f32; 3]),
    /// Save these colours as a swatch group named `group`.
    AddToSwatches { group: String, colors: Vec<[f32; 3]> },
}

/// The Colour Chords section of a colour panel, for `base` (the app's current colour). `swatches`
/// is whether the app can save swatches (Add to Swatches shows only then). The chord chosen and
/// whether the section is open are remembered per `id`.
pub fn section(ui: &mut Ui, id: &str, base: [f32; 3], swatches: bool) -> Option<ChordAction> {
    let key = egui::Id::new(("horix-chords", id));
    // (the chord chosen, whether the section is folded away)
    let (mut chord_i, mut folded) = ui.ctx().data_mut(|d| *d.get_persisted_mut_or_default::<(usize, bool)>(key));
    let mut action = None;
    let v = ui.visuals().clone();
    let faint = v.weak_text_color();

    // Header: the disclosure and the title, as the apps' collapsible sections.
    let head = ui.horizontal(|ui| {
        let arrow = if !folded { "⏷" } else { "⏵" };
        let r = ui.add(egui::Label::new(egui::RichText::new(format!("{arrow}  Colour Chords")).strong()).sense(Sense::click()));
        r.on_hover_text("Colours that go with the current colour, by colour theory")
    });
    if head.inner.clicked() {
        folded = !folded;
    }
    if !folded {
        ui.add_space(4.0);
        let chord = Chord::ALL[chord_i.min(Chord::ALL.len() - 1)];
        ui.horizontal(|ui| {
            egui::ComboBox::from_id_salt(key.with("chord")).width(ui.available_width().min(170.0)).selected_text(chord.name()).show_ui(ui, |ui| {
                for (i, c) in Chord::ALL.iter().enumerate() {
                    ui.selectable_value(&mut chord_i, i, c.name());
                }
            });
        });
        let chord = Chord::ALL[chord_i.min(Chord::ALL.len() - 1)];
        let colors = chord.colors(base);
        ui.add_space(4.0);
        // The strip: touching cells across the panel, the base marked with a dot.
        let w = ui.available_width().max(60.0);
        let (strip, _) = ui.allocate_exact_size(vec2(w, 26.0), Sense::hover());
        let n = colors.len().max(1) as f32;
        let cell = strip.width() / n;
        let base_at = if chord == Chord::Analogous { 1 } else { 0 };
        for (i, c) in colors.iter().enumerate() {
            let r = Rect::from_min_size(strip.min + vec2(cell * i as f32, 0.0), vec2(cell, strip.height()));
            let resp = ui.interact(r, key.with(("cell", i)), Sense::click());
            ui.painter().rect_filled(r, CornerRadius::ZERO, c32(*c));
            if i == base_at {
                let dot = if rgb_to_hsl(*c).2 > 0.6 { Color32::from_black_alpha(160) } else { Color32::from_white_alpha(200) };
                ui.painter().circle_filled(r.center_bottom() - vec2(0.0, 6.0), 2.2, dot);
            }
            if resp.hovered() {
                ui.painter().rect_stroke(r.shrink(0.5), CornerRadius::ZERO, Stroke::new(1.5, v.strong_text_color()), StrokeKind::Inside);
            }
            let tip = if i == base_at { format!("{}  (base)", hex(*c)) } else { hex(*c) };
            if resp.on_hover_text(tip).clicked() {
                action = Some(ChordAction::Use(*c));
            }
        }
        ui.painter().rect_stroke(strip, CornerRadius::ZERO, Stroke::new(1.0, v.widgets.noninteractive.bg_stroke.color), StrokeKind::Outside);
        ui.add_space(6.0);
        ui.horizontal(|ui| {
            ui.label(egui::RichText::new(format!("{} colours · click one to use it", colors.len())).small().color(faint));
            if swatches {
                ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                    if ui.button("Add to Swatches").on_hover_text("Save this chord as a swatch group").clicked() {
                        action = Some(ChordAction::AddToSwatches { group: format!("{} {}", chord.name(), hex(base)), colors: colors.clone() });
                    }
                });
            }
        });
    }
    ui.ctx().data_mut(|d| d.insert_persisted(key, (chord_i, folded)));
    action
}

/// The hue chords (Tints, Shades and Tones keep the hue), for colour grading.
pub const HUE_CHORDS: [Chord; 7] =
    [Chord::Complementary, Chord::SplitComplementary, Chord::Analogous, Chord::AccentedAnalogic, Chord::Triadic, Chord::Tetradic, Chord::Square];

/// Which grading wheel (0 shadows, 1 midtones, 2 highlights) each of a hue chord's colours goes to:
/// the base to the highlights, the next to the midtones (a pair skips them) and the next to the
/// shadows. Returns (wheel, hue in degrees).
pub fn grading_hues(chord: Chord, base_hue: f32) -> Vec<(usize, f32)> {
    let hues: Vec<f32> = chord.turns().iter().map(|t| (base_hue + t).rem_euclid(360.0)).collect();
    match hues.as_slice() {
        [a, b] => vec![(2, *a), (0, *b)],
        [a, b, c, ..] => vec![(2, *a), (1, *b), (0, *c)],
        _ => Vec::new(),
    }
}

/// The Colour Chords section of a colour grading panel: the hue chords on the wheel's base hue
/// (`base_hue`, degrees), shown as a strip; Apply gives the hues for the wheels ([`grading_hues`]).
pub fn grading_section(ui: &mut Ui, id: &str, base_hue: f32) -> Option<Vec<(usize, f32)>> {
    let key = egui::Id::new(("horix-chords-grading", id));
    let (mut chord_i, mut folded) = ui.ctx().data_mut(|d| *d.get_persisted_mut_or_default::<(usize, bool)>(key));
    let mut out = None;
    let v = ui.visuals().clone();
    let head = ui.horizontal(|ui| {
        let arrow = if !folded { "⏷" } else { "⏵" };
        ui.add(egui::Label::new(egui::RichText::new(format!("{arrow}  Colour Chords")).strong()).sense(Sense::click()))
            .on_hover_text("Hues that go together by colour theory, for the Shadows, Midtones and Highlights wheels")
    });
    if head.inner.clicked() {
        folded = !folded;
    }
    if !folded {
        ui.add_space(4.0);
        let chord = HUE_CHORDS[chord_i.min(HUE_CHORDS.len() - 1)];
        egui::ComboBox::from_id_salt(key.with("chord")).width(ui.available_width().min(170.0)).selected_text(chord.name()).show_ui(ui, |ui| {
            for (i, c) in HUE_CHORDS.iter().enumerate() {
                ui.selectable_value(&mut chord_i, i, c.name());
            }
        });
        let chord = HUE_CHORDS[chord_i.min(HUE_CHORDS.len() - 1)];
        let hues = grading_hues(chord, base_hue);
        ui.add_space(4.0);
        // Shadows, midtones, highlights, left to right; a wheel the chord leaves alone is empty.
        let w = ui.available_width().max(60.0);
        let (strip, _) = ui.allocate_exact_size(vec2(w, 22.0), Sense::hover());
        let cell = strip.width() / 3.0;
        for (i, name) in ["Shadows", "Midtones", "Highlights"].iter().enumerate() {
            let r = Rect::from_min_size(strip.min + vec2(cell * i as f32, 0.0), vec2(cell, strip.height()));
            match hues.iter().find(|(k, _)| *k == i) {
                Some((_, h)) => {
                    ui.painter().rect_filled(r, CornerRadius::ZERO, c32(hsl_to_rgb(*h, 0.75, 0.55)));
                    ui.interact(r, key.with(("cell", i)), Sense::hover()).on_hover_text(format!("{name}: {}°", h.round()));
                }
                None => {
                    ui.painter().rect_stroke(r.shrink(0.5), CornerRadius::ZERO, Stroke::new(1.0, v.widgets.noninteractive.bg_stroke.color), StrokeKind::Inside);
                    ui.interact(r, key.with(("cell", i)), Sense::hover()).on_hover_text(format!("{name}: kept"));
                }
            }
        }
        ui.add_space(6.0);
        ui.horizontal(|ui| {
            ui.label(egui::RichText::new(format!("From the base hue {}°", base_hue.round())).small().color(v.weak_text_color()));
            ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                if ui.button("Apply to Wheels").on_hover_text("Set the wheels' hues to this chord").clicked() {
                    out = Some(hues.clone());
                }
            });
        });
    }
    ui.ctx().data_mut(|d| d.insert_persisted(key, (chord_i, folded)));
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    fn hue(c: [f32; 3]) -> f32 {
        rgb_to_hsl(c).0
    }

    #[test]
    fn hue_chords_turn_the_base_and_keep_it() {
        let base = [0.282, 0.757, 0.918]; // Affinity's sky blue, about 195°
        let h = hue(base);
        let split = Chord::SplitComplementary.colors(base);
        assert_eq!(split[0], base);
        assert!((hue(split[1]) - (h + 150.0).rem_euclid(360.0)).abs() < 1.0);
        assert!((hue(split[2]) - (h + 210.0).rem_euclid(360.0)).abs() < 1.0);
        assert_eq!(Chord::Square.colors(base).len(), 4);
        assert_eq!(Chord::Analogous.colors(base)[1], base);
    }

    #[test]
    fn tints_shades_and_tones_end_at_white_black_and_grey() {
        let base = [0.2, 0.4, 0.8];
        assert_eq!(*Chord::Tints.colors(base).last().unwrap(), [1.0; 3]);
        assert_eq!(*Chord::Shades.colors(base).last().unwrap(), [0.0; 3]);
        assert_eq!(*Chord::Tones.colors(base).last().unwrap(), [0.5; 3]);
        assert_eq!(Chord::Tints.colors(base).len(), STEPS);
    }

    #[test]
    fn grading_puts_the_base_on_the_highlights() {
        assert_eq!(grading_hues(Chord::Complementary, 30.0), vec![(2, 30.0), (0, 210.0)]);
        assert_eq!(grading_hues(Chord::Triadic, 0.0), vec![(2, 0.0), (1, 120.0), (0, 240.0)]);
        assert!(grading_hues(Chord::Tints, 0.0).is_empty());
    }

    #[test]
    fn hsl_round_trips() {
        for c in [[0.9, 0.1, 0.3], [0.1, 0.8, 0.2], [0.5, 0.5, 0.5], [0.0, 0.0, 0.0]] {
            let (h, s, l) = rgb_to_hsl(c);
            let back = hsl_to_rgb(h, s, l);
            for k in 0..3 {
                assert!((back[k] - c[k]).abs() < 1e-4, "{c:?} -> {back:?}");
            }
        }
    }
}
