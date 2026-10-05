# Nano Banana 2 (Gemini 3.1 Flash Image): prompting research for the engraved-tray edit

Date: 2026-10-05. Scope: localized edits, iterative refinement, reference roles, photoreal materials, text/logo fidelity, system prompt and parameters, failure modes.
Note: the sandbox proxy blocked direct fetches of ai.google.dev, docs.cloud.google.com, developers.googleblog.com, blog.google and dev.to. The official findings below come from search-result extracts of those pages plus a full fetch of the Google Cloud blog guide.

---

## 0. Diagnosis of v3 (what the outputs show)

| Version | What the prompt change did | Remaining problem |
|---|---|---|
| v1 | Basic "engrave logo" | Too big, too dark/deep, "A" in VINTAGE got a crossbar, 1K |
| v2 | Physical description of a groove (highlight on one edge, shadow on the other) | Physics language made the model draw **outline + drop shadow** around every stroke, so the letters read as embossed or laser-cut |
| v3-nb2 | Image 3 close-up of the burin technique, "one line per stroke", cartouche | Much better tone (pale, frosted, sparkly). **But "A Certain Era" is still drawn as a double contour (hollow outlined letters with stippled fill)**. VINTAGE came out right as single lines. Text is about 1/2 of the inner-oval width, not 1/3. Baseline and spacing are perfectly regular, the strokes are uniformly crisp and the type looks like a font, not a hand-cut inscription. The cartouche wiped the scrolls too cleanly. |
| v3-pro | Same prompt on Pro | Even crisper, pure outline letters with no fill: a vector-stroke look |

Key takeaway: the model treats "letters" as filled glyph shapes and then "engraves" each glyph's outline. Larger letters ("A Certain Era") get outlined and smaller ones (VINTAGE) get single lines. The prompt has to say directly that each letter is a **single centreline cut, like a single-line (Hershey/CNC) engraving font or a pen-plotter line, with no inner and outer edge**, and it should describe the stroke as narrower than the existing ornament lines, not just the same.

---

## 1. Findings with sources

### (a) Localized edits that preserve the rest of the image
- Official inpainting template: *"Using the provided image, change only the [specific element] to [new element/description]. Keep everything else in the image exactly the same, preserving the original style, lighting, and composition."* Text works as a semantic mask. (Google Developers Blog, Gemini 2.5 Flash Image prompting; Gemini API image-generation docs)
- "Editing requires a different mindset... your prompt needs to focus on what is changing and what is staying the same. Be explicit about what to keep exactly the same." (Google Cloud blog, Ultimate prompting guide for Nano Banana; blog.google Nano Banana Pro tips)
- Practitioners: if you only describe the change, the model is free to redraw the rest, so list the parts that must stay. End with "Don't change anything else... keep camera angle, perspective and framing unchanged". Make **one change per edit**. (chasejarvis.com, morphed.app, artlist.io)
- Put the constraints in a separate "Must keep" block and repeat them in every follow-up. (morphic.com Nano Banana Pro guide)
- **Hard limit:** the model always re-encodes and re-renders the **whole** frame. Even unchanged regions drift (colour shift, texture "prior drift", softening). Research on Nano Banana (Banana100, FreqEdit, Why do DiT editors drift?) documents global colour shifts and cumulative degradation over editing rounds. **Practical counter:** after each accepted edit, composite only the inscription region back onto the source with a feathered mask (ComfyUI `ImageCompositeMasked` / `Image Blend by Mask`, or any editor). Then the rug, rim and reflections stay truly pixel-identical, whatever the model did elsewhere.

### (b) Iterative refinement of a previous output
- Google: "Don't expect a perfect image on the first attempt. Use follow-up prompts to make small changes." Chat or multi-turn is the recommended way to iterate. (Gemini API docs, Cloud blog)
- If an image is about 80% right, refine it instead of regenerating. (morphic.com / chasejarvis.com)
- In true multi-turn API use, pass thought signatures back to keep the reasoning context. (Gemini API docs, Gemini 3 developer guide) The Comfy node is single-shot, so we simulate multi-turn by feeding v3-nb2 as Image 1 and naming the exact defects to fix. Phrase it as a **correction to an existing image** ("the inscription in Image 1 is currently drawn as..., redraw only it as...") rather than describing the whole scene again.
- Each edit pass degrades quality slightly. Limit the edit chain to 1 or 2 passes, then either composite (see a) or regenerate from the original with the lessons learned (Prompt B).

### (c) Reference image role assignment
- Official formula: `[Reference images] + [Relationship instruction] + [New scenario]`, e.g. "Using the attached napkin sketch as the structure and the attached fabric sample as the texture...". (Cloud blog)
- Put the image that must survive **first**. Say per image what to take from it and what to ignore ("use the second image only as the lighting reference"). Start with 2 to 4 references, not 14. Each one needs a distinct role. (practitioner guides on Nano Banana Pro reference slots, morphic.com)
- Limits: Gemini 3 image models accept up to 14 inputs. About 5 to 6 object references keep high fidelity. Gemini 2.5 Flash Image worked best with 3 or fewer. (Vertex AI "Gemini image generation limitations")
- For us: Image 1 = base to edit, Image 2 = technique/tone (engraving close-up), Image 3 = letter shapes only (logo). Tell the model to take **only the letter skeletons** from the logo, never its black colour, white background or stroke thickness.

### (d) Photoreal material and texture, avoiding the CG-clean look
- Define materiality physically ("navy blue tweed", "etched with silver leaf patterns"). Specify the surface, lighting and camera/film character. (Cloud blog)
- The model defaults to the "statistical average" of retouched commercial imagery. Realism comes from **naming the imperfections** (wear, asymmetry, signs of use, grain) and from one real light source. (cookedbanana.com, lunostudio.ai, sider.ai)
- Use positive framing: describe what you want ("bare pale metal lines") instead of "no X". (blog.google Nano Banana Pro tips, Cloud blog) Exception: practitioners report that short, concrete negative clauses help against specific recurring artifacts, as long as they come after the positive description. Our v2 lesson also shows that **over-describing groove physics (highlight edge plus shadow edge) causes outline/bevel artifacts**. Describe the *visual result in the photo* (a thin pale scratch-line) rather than the 3D profile.

### (e) Text and logo fidelity
- Put the exact text in quotes and describe the typeface style. For unusual glyphs, describe them verbally. The model may also ignore exact character instructions, so it helps to state the character sequence explicitly. (Cloud blog, morphic.com)
- Specify placement and size explicitly (relative to a reference object). (morphic.com, Cloud blog)
- Single-line vs outline: in the engraving world, an "outline font" engraves the boundary of each glyph, while a "single-line / single-stroke font" (Hershey, CNC engraving fonts) cuts one line per stroke. (Autodesk FeatureCam KB, Rhino single-line fonts, snijlab.nl) Using this vocabulary in the prompt gives the model a concrete, well-known visual concept.
- Recommended extra lever (optional, outside the model): give the model a **skeletonized/centreline version of the logo** as the letter reference (e.g. Inkscape "Hershey Text" tracing, or skeletonize the PNG). A 1-px line reference makes it much harder for the model to draw double contours.

### (f) System prompt, temperature, seed and thinking
- Google strongly recommends keeping **temperature at the default 1.0 for all Gemini 3 models**. Lowering it can cause looping or degraded behaviour. Some image endpoints cap at 1.0. (Gemini 3 developer guide, Vertex AI parameter docs) Do not go above 1.0 for edits, because it increases drift. Leave top_p at 0.95.
- Variation comes from **seeds**, not temperature: run 3 to 4 seeds per prompt and pick the best.
- thinking_level: HIGH maximizes reasoning depth. MINIMAL is for latency and does not guarantee that thinking is off. (Gemini thinking docs) For a constraint-heavy edit (exact glyphs, placement, preservation), HIGH is worth the extra cost.
- A system instruction can carry the persistent rules (role, preservation contract, realism standard), so the user prompt only states the change. Google's image guides don't publish a canonical one. The draft below is our own, built on the official principles.
- Resolution: 2K (4:5) matches v3-nb2 (1856x2304) and the original's aspect ratio (2076x2576 is about 4:5). For an edit, keep the **same resolution as the input** so the model doesn't rescale and re-synthesize textures. Use 4K only for a final regeneration (Prompt B), and expect more invented micro-detail.

### (g) Known failure modes and counters
| Failure | Counter |
|---|---|
| Whole image re-rendered or colour-shifted on edit | Explicit keep-list. Same resolution and aspect ratio. Composite the edited region back with a mask. Keep the chain to 1 or 2 passes. |
| Letters drawn as outlines / double contour / hollow | Say "single-line engraving font, one centreline cut per stroke, like a pen-plotter line". Give an explicit width comparison (thinner than the ornament lines). Use a centreline logo reference. Name the current defect in refinement edits. |
| Bevel, drop shadow, embossed look | Avoid describing highlight/shadow edges. Describe a flat pale scratch-line in the photo. |
| Too clean / font-perfect | List concrete hand-made irregularities with numbers ("baseline wanders by about a letter-stroke width", "a few strokes partly worn away"). |
| Glyph substitution (A with crossbar) | Spell the glyph out ("open Λ, two strokes meeting at the top, no horizontal bar"). |
| Size creep | Give size relative to features visible in the image ("from the point below X to Y", "about one third of the flat oval's width"). |
| Model "improves" the composition (erases ornament, invents a cartouche) | Say exactly how much ornament may give way ("only where a letter would cross it"). |

### Sources
- https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana
- https://blog.google/products-and-platforms/products/gemini/prompting-tips-nano-banana-pro/
- https://blog.google/innovation-and-ai/technology/ai/nano-banana-2/
- https://developers.googleblog.com/how-to-prompt-gemini-2-5-flash-image-generation-for-the-best-results/
- https://ai.google.dev/gemini-api/docs/image-generation
- https://ai.google.dev/gemini-api/docs/gemini-3 (temperature 1.0 recommendation)
- https://ai.google.dev/gemini-api/docs/thinking
- https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/gemini-image-generation-best-practices
- https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/gemini-image-generation-limitations
- https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/3-1-flash-image
- https://dev.to/googleai/nano-banana-pro-prompting-guide-strategies-1h9n
- https://morphic.com/resources/how-to/nano-banana-pro-guide
- https://chasejarvis.com/blog/how-to-edit-images-in-nano-banana-pro-for-creative-professionals/
- https://morphed.app/blog/nano-banana-prompts-for-editing-images
- https://www.cookedbanana.com/blog/fix-plastic-skin-ai-images-nano-banana
- https://www.lunostudio.ai/academy/nano-banana-photorealism
- https://arxiv.org/html/2604.03400v1 (Banana100: iterative degradation with Nano Banana Pro)
- https://arxiv.org/pdf/2512.01755 (FreqEdit: multi-turn editing drift)
- https://www.rhino3d.com/features/text/single-line-fonts/
- https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Which-font-style-to-choose-for-a-single-line-engraving-in-FeatureCam.html

---

## 2. Recommended system_prompt (use for both A and B)

```
You are a meticulous high-end photo retoucher and master hand engraver working on real product photographs. Your edits must be undetectable: the result has to look like an unretouched phone snapshot of a real object, never like a render, a mockup or a digital overlay.
Rules:
1. Change only what the instruction asks to change. Every other part of the input photo (composition, crop, perspective, colours, white balance, reflections, stains, scratches, background, grain, sharpness) stays exactly as it is, with no global re-colouring, sharpening, denoising or "enhancement".
2. Each input image has the role stated in the instruction. Take from a reference image only what the instruction says to take from it.
3. Physical marks such as engraving follow the photo's real light and perspective and match the existing marks on the same object in tone, width and wear. They are made of the object's own material, never added outlines, strokes, glows, bevels or drop shadows.
4. Lettering must reproduce the exact characters and glyph shapes given, including unusual glyphs, at the requested size and position.
5. Prefer subtle, imperfect, aged realism over clean perfection.
```

## 3. Parameters

| Setting | PROMPT A (refinement of v3-nb2) | PROMPT B (regeneration from original) | Why |
|---|---|---|---|
| Images | 1 = v3-nb2, 2 = engraving close-up, 3 = logo (ideally a centreline/skeleton version) | 1 = tacka.jpg, 2 = engraving close-up, 3 = logo | Base first. One role per image. 3 refs is the reliable range. |
| aspect_ratio | 4:5 | 4:5 | Matches input. Prevents recrop/re-synthesis. |
| resolution | 2K | 2K for the seed search, then 4K for the chosen seed only if needed | Same scale as input for edits. 4K invents micro-detail and costs more. |
| thinking_level | HIGH | HIGH | Exact glyphs, placement and preservation constraints benefit from reasoning. |
| temperature | 1.0 (default) | 1.0 | Google: keep Gemini 3 at 1.0. Lower can degrade, higher adds drift. |
| top_p | 0.95 (default) | 0.95 | Leave default. |
| seeds | 4 variants (e.g. 11, 22, 33, 44) | 4 variants | Variety comes from seeds. Pick the best, then composite. |
| response_modalities | IMAGE (or IMAGE+TEXT) | same | |
| Post-step | Composite the inscription zone from the best output onto v3-nb2 (or the original) with a feathered mask | same, onto tacka.jpg | Guarantees the rest is pixel-identical and stops drift. |

---

## 4. PROMPT A: refinement edit on v3-nb2

Inputs: Image 1 = `sesje/03-nb2-vs-pro-wzorzec-grawerunku/wynik-nb2-NAJLEPSZY.png`, Image 2 = `00-materialy/input/wzor-grawerunku-zblizenie.png`, Image 3 = `00-materialy/input/logo-a-certain-era.png` (or a single-line/skeleton version of it).

```
Using Image 1, redraw only the engraved inscription "A Certain Era" / "VINTAGE" in the centre of the tray. Everything else in Image 1 stays exactly as it is.

Image 1 is the photo to edit: a worn silver-plated oval tray on a grey rug, phone snapshot, soft daylight. Image 2 shows the tray's existing hand engraving up close; use it only as the reference for line quality, tone and wear. Image 3 shows the logo; use it only for the letter shapes and spacing, not for its black colour, white background or stroke weight.

What is wrong now: in Image 1 the large words "A Certain Era" are engraved as hollow outlined letters, with two parallel contour lines around every stroke and a sparkly fill between them. That makes them look like a laser-marked font outline, and the inscription is too large, too crisp and too perfect compared with the old floral engraving.

Redraw the inscription like this:
- Every letter stroke is one single hair-thin cut line running along the centre of the stroke, like a single-line engraving font or a pen-plotter line. Each stroke has exactly one line, never an inner and an outer edge. Draw "A Certain Era" the same way the word "VINTAGE" is already drawn in Image 1.
- The line is the same pale, frosted, slightly glinting silver as the floral cuts in Image 2 and no wider than the thinnest of them. It lies flat in the metal, with no shadow, bevel, outline or glow, so from a normal viewing distance the words are about as faint as the surrounding ornament.
- Make it look cut by hand decades ago and worn by polishing: the baseline wanders slightly, letters lean and space a little unevenly, curves such as the C, e and a are not perfectly round, some strokes are brighter and others fade out or break for a few millimetres, a couple of stroke ends show a tiny slip or overshoot, and fine surface scratches and the tray's smudges run across the letters.
- Keep the exact text "A Certain Era" on the first line and "VINTAGE" in widely spaced small capitals below. The A in VINTAGE is an open Λ: two strokes meeting at the top with no horizontal bar.
- Make the inscription about 25% smaller than now, still centred on the tray's long axis and in the same perspective as the tray surface. "A Certain Era" spans roughly one third of the flat inner oval's width. Let the floral scrolls come back closer around the words, interrupted only where a letter would cross them.

Keep exactly the same as Image 1: the tray's shape, rim and shell ornaments, all reflections, spots and scratches, the floral engraving outside the lettering, the rug, framing, colours, white balance, softness and grain. The result is the same unretouched phone photo, with only the inscription changed.
```

## 5. PROMPT B: full regeneration from the original photo

Inputs: Image 1 = `00-materialy/input/tacka.jpg`, Image 2 = `00-materialy/input/wzor-grawerunku-zblizenie.png`, Image 3 = `00-materialy/input/logo-a-certain-era.png` (or its single-line/skeleton version).

```
Using Image 1, add a small hand-engraved inscription to the centre of the silver tray, cut in exactly the same technique as the tray's existing floral engraving. Change nothing else in the photo.

Image 1 is the photo to edit: an old, worn, silver-plated oval tray with a gadrooned rim and shell ornaments on a grey-brown rug, taken from above at an angle with a phone in soft diffuse daylight, slightly soft with mild grain. Image 2 is a close-up of the tray's existing engraving; use it only as the reference for line quality, tone and wear. Its lines are single hairline burin cuts, pale and frosted, a little lighter than the grey metal, with tiny glints, slightly shaky, and in places faded or broken. Image 3 is the logo; use it only for the letter shapes and spacing, not for its black colour, white background or stroke weight.

The inscription reads "A Certain Era" on one line and, below it, "VINTAGE" in small, widely spaced capitals. The lettering is a thin geometric sans-serif with a single-storey a. The A in VINTAGE is an open Λ: two strokes meeting at the top with no horizontal bar.

How it is engraved:
- Each letter stroke is one single hair-thin cut line along the centre of the stroke, like a single-line engraving font or a pen-plotter line. Each stroke has exactly one line, never an inner and an outer edge, so no letter is hollow or outlined.
- The line has the same pale frosted silver tone as the cuts in Image 2 and is no wider than the thinnest of them. It lies flat in the metal and is visible only as a fine bright scratch-line, with no shadow, bevel, outline, glow or dark fill. From a normal viewing distance the words are about as faint as the floral ornament.
- It looks cut by hand decades ago and softened by polishing: the baseline wanders slightly, letters lean and space a little unevenly, curves are not perfectly round, some strokes are brighter and others fade out or break for a few millimetres, a couple of stroke ends show a small slip or overshoot, and the tray's fine scratches, smudges and tarnish continue across the letters.

Size and placement: centred in the flat inner oval on the tray's long axis and in the same perspective as the tray surface. "A Certain Era" spans about one third of the inner oval's width and "VINTAGE" about half of that. The existing floral scrolls stay in place and are interrupted only where a letter would cross them, as if the engraver had left a small space for the name.

Keep exactly as in Image 1: tray shape, rim, shell ornaments, every reflection, dark spot, stain and scratch, all of the floral engraving, the rug, crop, colours, white balance, softness and grain. The result is an unretouched phone snapshot of a genuinely old, engraved tray.
```

### Workflow suggestion
1. Run Prompt A with 4 seeds at 2K, HIGH, temp 1.0.
2. If the outline problem persists in all 4 seeds, swap Image 3 for a skeleton (1-px centreline) version of the logo and rerun.
3. Composite the best inscription onto v3-nb2 or tacka.jpg with a feathered mask covering only the lettering zone.
4. If A can't fix it (or the photo has drifted), run Prompt B from the original with 4 seeds, then composite in the same way.
