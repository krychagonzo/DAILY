# Sesja 07 — czysta generacja, bez wklejania i obróbki

- Wejście: Image 1 = tacka.jpg, Image 2 = referencja-styl-graweru.jpg (cały obraz, tylko wygląd graweru), Image 3 = logo
- Prompt: `prompt.txt` — krótki, narracyjny; grawer płytki, jasnoszary nalot
- Modele: Nano Banana 2 (2K, thinking HIGH, bez system promptu) ×2 seedy, Nano Banana Pro (2K) ×2 seedy
- Wyniki zapisane 1:1 z modelu, bez żadnej obróbki

## Werdykt
- Wszystkie 4 (nb2-seed71, nb2-seed72, pro-seed71, pro-seed72) — **najbardziej realistyczny grawer dotąd**: płytki, z szarym nalotem w rowkach, w perspektywie tacki, ornament zachowany, wygląda na stary przedmiot. Czysta generacja, zero obróbki.
- Problem: wszystkie modele przejęły **szeryfowy krój z referencji (Image 2)** zamiast bezszeryfowego logo; „A” w VINTAGE z poprzeczką.
- Porównanie: `porownanie-zblizenia.png` (góra: NB2 71, 72; dół: Pro 71, 72), `porownanie-calosc.png`.
