# Sesja 05 — grawer na ORYGINALNYM zdjęciu (ta sama tacka, ten sam dywan)

Zasada: poza obszarem napisu każdy piksel = `00-materialy/input/tacka.jpg`.

## Ścieżka A — Nano Banana 2 + PROMPT B + wklejka (seed 33, 44)
- Image 1 = tacka.jpg, Image 2 = zbliżenie wzoru, Image 3 = logo; 2K, thinking HIGH, system prompt (`01-research/nano-banana-prompting.md` §2, §5)
- Wynik AI (`A-nb2-seedNN-surowy.png`) skalowany do 2076×2576 i wklejony na oryginał tylko w eliptycznej masce środka tacy z miękką krawędzią → `A-nb2-seedNN-FINAL.png`

## Ścieżka B — Flux Pro Fill z maską (seed 33, 44)
- image = `02-system-skladanki/composite-cartouche.png`, mask = `mask-inpaint-tight-cartouche.png` (tylko linie liter)
- Prompt: opis faktury graweru (bez tekstu liter)
- Wyniki: `B-flux-fill-seedNN.png`

## Werdykt
- **A seed44 → `A-nb2-seed44-FINAL.png` — NAJLEPSZY DOTĄD.** Oryginalne zdjęcie (dywan, tacka, kadr identyczne co do piksela poza elipsą napisu — sprawdzone: 0 różnic poza maską). Napis cienki, srebro-na-srebrze, „Λ” poprawne, ornament wokół zachowany. Wady: litery wciąż dość równe/fontowe, miejscami lekki podwójny kontur w „A Certain Era”.
- A seed33: litery z kropkowanym konturem, większe — słabszy.
- B Flux Fill (oba seedy): zamiast liter bazgroły + niska rozdzielczość (1135×1408) — odrzucone.
- Wklejka: wynik NB2 przeskalowany do 2076×2576, nałożony na oryginał przez elipsę (środek 1062,1303; promienie 420×165; rozmycie 30 px).
