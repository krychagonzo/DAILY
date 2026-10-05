# Grawer logo „A Certain Era” na tacce — prompty

## Wnioski z researchu (Nano Banana / Gemini Image)
- Edycja: opisz **co się zmienia i co zostaje identyczne**; zacznij od mocnego czasownika.
- Przy kilku obrazach nadaj każdemu rolę („Image 1 = …, Image 2 = …”).
- Pisz narracyjnie, pełnymi zdaniami, nie listą słów kluczowych.
- Opisz **materiał i fizykę** (głębokość, ścianki rowka, jak łapie światło), a nie tylko „engraved”.
- Myśl jak fotograf: obiektyw, przysłona, kierunek i charakter światła.
- Tekst w cudzysłowach + opis kroju; opisz nietypowe glify słownie.
- Pozytywne sformułowania zamiast „no X” (np. „bare metal, unpainted grooves” zamiast „no ink”).
- Ustaw rozdzielczość (2K/4K) i thinking_level HIGH dla dokładności.

Źródła:
- https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana
- https://blog.google/products-and-platforms/products/gemini/prompting-tips-nano-banana-pro/
- https://developers.googleblog.com/en/how-to-prompt-gemini-2-5-flash-image-generation-for-the-best-results/
- https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/gemini-image-generation-best-practices

## v1 (Nano Banana 2, 1K) — uwagi
Logo za duże (~55%), za ciemne i głębokie, „A” w VINTAGE z poprzeczką, niska rozdzielczość.

## v2 — prompt
Engrave the logo from Image 2 into the flat center of the silver tray in Image 1, editing Image 1 only in that area.

Image 1 is the base photograph: an old, slightly worn silver-plated oval serving tray lying on a grey-brown abstract rug, shot from above at an angle with a phone camera in soft, diffuse daylight. Image 2 is only the artwork reference for the logo: the words "A Certain Era" in a thin, geometric, rounded sans-serif (single-weight hairline strokes, a single-storey "a"), and beneath it the word "VINTAGE" in small, widely letter-spaced capitals, where the letter "A" in "VINTAGE" is drawn as an open inverted V ("Λ") with no crossbar.

Place the logo in the middle of the inner oval, centered on the tray's long axis, modest in size: the line "A Certain Era" spans about one third of the inner oval's width, so plenty of the existing floral scroll etching stays visible around it. Lay the lettering flat on the metal and foreshorten it with exactly the same perspective as the tray surface.

Make it read as a real, slightly imperfect hand-guided engraving pressed shallowly into the metal: thin, gently concave grooves roughly a fraction of a millimetre deep, the same hairline width as the existing ornamental etching. Inside each groove the bare metal is a slightly duller, satin grey; one edge of every stroke catches a thin bright highlight from the daylight and the opposite edge holds a soft, faint shadow, so the letters look recessed rather than printed. Add natural imperfections: stroke depth varies a little, a few curves are very slightly uneven, tiny burr and micro-scratches along the edges, the grooves carry the same light tarnish, fingerprints and wear as the rest of the tray, and some fine surface scratches pass across the letters. The engraving is subtle and tone-on-tone, silver on silver, about as visible as the existing floral engraving, unpainted bare metal.

Keep everything else exactly as in Image 1: the tray shape, the gadrooned rim with its shell ornaments, the reflections, stains and spots, the existing floral etching, the rug, the framing, colour and the natural phone-photo grain and slight softness. The result should look like an untouched, candid product photo of a genuinely engraved vintage tray.

## v2 — uwagi (feedback)
Za sztucznie: litery grube, obrysowane podwójnym konturem, ciemny cień pod spodem → czytają się jak WYPUKŁE / wycięte laserem. Światło na literach niezgodne ze zdjęciem. Napis zbyt „czysty”, nie gra z istniejącym wzorem.

Analiza zbliżenia oryginału: istniejący grawer to pojedyncze, włosowate rysy rylca, JAŚNIEJSZE od tła (matowo-białawe, lekko iskrzące), cienkie, miejscami przerywane, lekko drżące, różnej intensywności, z drobnymi poślizgami. Brak cieni, brak obrysów. → Logo trzeba zrobić tą samą techniką: jedna rysa na każdą kreskę liter (linia środkowa), ten sam ton co ornament.

## v3 — prompt (+ Image 3 = zbliżenie istniejącego grawerunku)
Add a hand-engraved inscription of the logo from Image 2 to the centre of the tray in Image 1, cut with exactly the same tool, line and finish as the tray's existing floral engraving shown up close in Image 3. Edit only the inscription area; the rest of Image 1 stays pixel-identical.

Image 1 is the base photo to edit: a worn, mass-produced vintage silver-plated oval tray on a grey rug, phone photo, soft diffuse daylight, slightly soft focus and mild JPEG grain. Image 2 is only the lettering reference: "A Certain Era" in a thin geometric sans-serif and below it "VINTAGE" in small, widely spaced capitals, whose "A" is an open "Λ" without a crossbar. Image 3 is a close-up of the engraving technique to copy: single hairline cuts made by an engraving burin, each cut a fine pale line, a little lighter and more frosted than the surrounding grey metal, with tiny sparkling glints along its length, slightly shaky, varying in strength, sometimes fading out or broken, with small slips and overshoots at the ends of curves.

How the inscription must look:
- Each letter stroke is ONE single fine engraved line following the centre of the stroke, the same width and the same pale frosted silver tone as the floral lines in Image 3. The letters are drawn only by these thin cut lines, so they look as delicate and low-contrast as the existing ornament and sit in it as if engraved in the same workshop decades ago.
- The cuts sit slightly below the surface: a fine incised scratch-line that catches the soft daylight the same way the existing pattern does, flush with the tray, flat in silhouette, with the tray's own reflections and smudges continuing over the letters.
- Hand-made irregularity: the baseline wanders a little, letter spacing is slightly uneven, a few strokes are a touch lighter or doubled where the burin was re-cut, round letters are not perfectly round, the line occasionally skips, and some letters are partly worn and faded by decades of polishing, exactly like the older parts of the floral pattern.
- Size and placement: centred in the middle of the inner oval, along the tray's long axis, following the same perspective as the tray surface; "A Certain Era" spans roughly one third of the inner oval's width, "VINTAGE" about half of that. The floral scrolls stop a few millimetres around the lettering as if the engraver left a small clear cartouche for it, and the surrounding scrolls frame the inscription, so it reads as part of the original decoration.

Keep exactly as in Image 1: tray shape, gadrooned rim and shell ornaments, all reflections, dark spots, stains, scratches, the remaining floral engraving, the rug, crop, colours, softness and grain. The final image is an unretouched phone snapshot of a genuinely old engraved tray.
