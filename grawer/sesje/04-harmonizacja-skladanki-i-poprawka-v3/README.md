# Sesja 04 — harmonizacja składanki + poprawka v3

Model: vertexai/nano-banana-2, 2K, 4:5, thinking HIGH, temperature 1.0 (domyślna), system prompt z `01-research/nano-banana-prompting.md` §2.

## Ścieżka 1 — harmonizacja lokalnej składanki (2 seedy)
- Image 1 = `02-system-skladanki/composite-cartouche.png`, Image 2 = `00-materialy/input/wzor-grawerunku-zblizenie.png` (bez logo!)
- Prompt: `02-system-skladanki/README.md` → „Recommended AI step 1”
- Pliki: `1-harmonizacja-seed11.png`, `1-harmonizacja-seed22.png`

## Ścieżka 2 — PROMPT A: poprawka v3-nb2 (2 seedy)
- Image 1 = `sesje/03-.../wynik-nb2-NAJLEPSZY.png`, Image 2 = zbliżenie wzoru, Image 3 = logo
- Prompt: `01-research/nano-banana-prompting.md` §4
- Pliki: `2-poprawka-v3-seed11.png`, `2-poprawka-v3-seed22.png`

## Werdykt
- **1-harmonizacja seed11 / seed22:** napis ładnie siedzi w istniejącym owalu i pasuje do ornamentu, ale model z powrotem „wyczyścił” litery na idealny font (pełne, równe linie). Niedoskonałości ze składanki zniknęły; „A” w VINTAGE z poprzeczką. Seed22 dodał rysy na tacy.
- **2-poprawka seed11:** model przerysował całe zdjęcie (inny kadr, inne ornamenty) — odrzucony.
- **2-poprawka seed22:** litery nadal obrysowane podwójnym konturem z kropkowanym wypełnieniem — gorzej niż v3.
- Wniosek: każda pełna edycja AI „poprawia” litery do czystego fontu. Najbardziej realistyczny grawer daje lokalna składanka; AI tylko w masce (inpaint) albo wcale.
