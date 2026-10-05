# Engraved logo composite: deterministic pipeline + AI harmonization

The goal is to stop asking the model to *invent* the engraving. We draw it ourselves, as single
hand-made burin lines in the photo's own perspective and tone. The model then only harmonizes the
pixels.

## Files

| file | what |
|---|---|
| `make_composite.py` | the whole pipeline; parameters at the top. `python3 make_composite.py [cartouche|third] [seed]` |
| `composite-cartouche.png` / `-zoom.png` | **variant A (recommended)**: inscription placed inside the tray's existing empty dotted cartouche (~290 px, about 20% of the inner oval). No existing engraving is removed. |
| `composite-third.png` / `-zoom.png` | **variant B**: "A Certain Era" is about 1/3 of the inner oval (420 px, ~29%). The old dotted cartouche and nearby leaves are removed inside a NEW engraved double-line oval frame. |
| `engraving-lines-<v>.png` | flat (un-warped) single-line engraving, grey intensity |
| `engraving-layer-<v>.png` | RGBA layer in photo coordinates (white, alpha = cut strength) |
| `mask-inpaint-<v>.png` | inpaint mask (white = may change), see below |

Requirements: `pip install numpy opencv-python-headless`. Each run takes about 5 s. The output is deterministic for a given seed.

## Pipeline (make_composite.py)

1. **Per-letter irregularity on the logo.** Connected components are grouped into letters (the
   i-dot stays with its stem). Each letter gets a small random dx/dy/rotation (σ 0.7 px, 0.6 px,
   1.3°). A slow two-frequency baseline drift is added, so the baseline wanders and the spacing
   varies slightly. VINTAGE is enlarged 12% and moved a little further down for legibility.
2. **Centreline.** A Zhang-Suen skeleton turns every stroke into one burin cut. It is drawn at 4x
   supersampling as a 1.7 px line in final pixels. Stroke ends get 1–3 short "slip" overshoots, and 4
   short doubled "re-cut" segments are offset by 1–2 px.
3. **Hand wobble.** A smooth displacement field (0.4 px over ~16 px) plus a tiny tremor (0.07 px)
   is applied. Larger values look like pencil sketching, not a burin.
4. **Wear and pressure.** Smooth noise varies the line strength between 0.5 and 1.0 along the
   strokes. About 4% of the stroke length is skipped as gaps. Pixel sparkle and rare glints give the
   frosted look. The result is downsampled with an area filter.
5. **Perspective.** A homography sets the apparent tilt to −7° (measured from the inner oval's long
   axis), adds 0.84 vertical foreshortening and a slight keystone. It is centred at (1106, 1300),
   which is the centre of the existing dotted cartouche.
6. **Tone.** Measured on the photo, the existing cuts are about +15–25 grey levels over a ~138
   background, 2–3 px wide, with a slight dark dip on one side. The cut is blended as
   `base + 0.30·L·(248−base)` and a 7-level dark edge is added on the lower side.
7. **(Variant B only) Clearing.** Old lines inside the new frame are found with a morphological
   top-hat and removed with an inpaint plus median/Gaussian smoothing. Grain is re-synthesized from
   the noise statistics of the original metal.
8. **Softness.** A Gaussian blur of 0.4 px is applied, then the edited area only goes through one
   JPEG q92 round-trip. Every pixel outside the edit is bit-identical to `input/tacka.jpg`.

## Honest assessment

- **Strengths.** The letter strokes have the same width, tone and crisp frosted look as the floral
  cuts. They are single lines with no double outline and no fake depth, and the perspective
  matches the tray. Variant A looks believable at normal viewing size, because a monogram inside an
  empty cartouche is what real trays have.
- **Weaknesses.**
  - The letter shapes are still the geometric logo font. A real engraver would add slight
    script-like stroke-weight swelling (burin cuts get wider where pressed harder). Ours vary only in
    brightness.
  - At small sizes (VINTAGE in variant A, ~11 px tall) the gaps can read as missing letters
    ("VIN TAGE"). Re-roll the seed or set `GAP_FRACTION=0.02`.
  - Skeleton forks at sharp apexes (the top of "A") leave a tiny tick. It reads as an overshoot, but
    it is visible at 2x zoom.
  - In variant B the cleared interior is a little too smooth and uniform compared with the
    smudged original metal. The new frame also cuts the leaf scrolls abruptly.
  - The 3D look of the cut is very subtle. Some light-dependent sparkle variation is missing.

## Recommended AI step 1: Nano Banana 2 harmonize pass (cheap, keeps shape)

Inputs: **Image 1 = `composite-cartouche.png`** (or `composite-third.png`). Optionally,
**Image 2 = `input/wzor-grawerunku-zblizenie.png`** as the line-finish reference. Do NOT pass the
logo PNG: it pulls the model back to clean font outlines. Use low creativity if the API exposes it,
same aspect ratio, 2K.

Prompt draft:

> Retouch Image 1 very lightly so it looks like an unedited phone photo. Image 1 already shows an
> old silver-plated tray with a hand-engraved inscription "A Certain Era" / "VINTAGE" in the
> centre. Keep the inscription exactly where it is, with exactly the same letter shapes, size,
> spacing, perspective and thin single-line strokes. Do not redraw, retype, thicken, outline or
> straighten it. Only make the inscription's engraved lines share the same finish as the
> surrounding floral engraving (shown up close in Image 2): fine pale frosted burin cuts with tiny
> glints, slightly uneven pressure, a little worn by decades of polishing, with the tray's faint
> smudges and fine scratches passing over them. Everything else in Image 1 stays pixel-identical:
> tray, rim, reflections, stains, floral engraving, rug, framing, colour, softness and grain.

If it still "re-fonts" the letters, drop the word "inscription" and describe the change as "unify
the finish of all engraved lines in the centre". Some generations will regress. Compare each one
against the composite and keep the composite if the model makes it worse.

## Recommended AI step 2 (alternative): masked inpaint on Comfy Cloud (bfl/flux-pro-fill)

A mask keeps everything outside the inscription untouched. Flux Fill is strong at texture
continuation. Use `mask-inpaint-<v>.png`: white = regenerate, black = keep. It is a soft-edged
ellipse in photo coordinates, tilted −7°, covering the text block plus a ~25–30 px margin. For
variant B, regenerate a mask that covers the whole new frame (set the ellipse in step 7 of the
script to the frame size) if you also want the cleared patch re-textured.

- Image: `composite-<v>.png` (full res 2076x2576). Mask: `mask-inpaint-<v>.png`.
- **Feed the composite, not the original.** With the inscription already present, Fill continues
  it instead of inventing letters.
- Prompt for Fill (describe the final state of the masked area):
  `close-up of worn silver-plated metal tray surface with a hand-engraved inscription "A Certain Era" above small spaced capitals "VINTAGE", single fine pale frosted burin lines, slightly uneven, low contrast, soft diffuse daylight, phone photo`
- Use low guidance and steps to stay close (e.g. guidance ~15–20 on flux-pro-fill, steps 30). If
  Fill garbles the letters, shrink the mask to a ~6 px dilation of the line layer. To make it,
  the script saves it as `mask-inpaint-tight-<v>.png` (layer alpha > 10, dilated 6 px, blurred 2 px). Fill then only
  re-textures the cuts and their immediate surroundings and cannot redraw the glyphs.
