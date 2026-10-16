# HORIX patches for PhotoCraft 0.9.0

Diffs here apply in name order after `rebrand.py`, against the rebranded 0.9.0 tree.

The 0.3.0 patches are kept in `../patches-0.3/` as the source for the port: about 60% of them
are now built into PhotoCraft 0.9.0 and are dropped (see `../UPGRADE-0.9.md`). The rest
returns here as new, smaller patches, one milestone at a time:

1. Branding, theme, web shell (rebrand.py): done.
2. `60-horix-ux`: P before/after, profile mismatch off by default, New Document colour profile,
   overset mark, Ungroup in the context menu, group-delete dialog, Color-panel eyedropper,
   Properties auto-raise, Select › Modify preview: done.
3. Blur Gallery handles (Iris, Spin, Tilt-Shift, Path on the canvas): done, part of `60-horix-ux`.
4. `30-refine`, `40-healing`: only where segeval measures a gain over upstream.
5. `50-horix-ai`: MobileSAM Quick / Object Selection, IS-Net Select Subject, preload, GPU status: done.
   The AI drives upstream's Object Finder hover and click when the model is ready; without a
   model every tool falls back to upstream's own algorithm.
