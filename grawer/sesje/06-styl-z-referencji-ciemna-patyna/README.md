# Sesja 06 — styl graweru z referencji użytkownika (ciemna patyna w rowkach)

Referencja: `00-materialy/input/referencja-styl-graweru.jpg` (+ `-zblizenie.png`).

## Analiza referencji (co sprawia, że wygląda fotorealistycznie)
- Rowki są **ciemne, grafitowo-szare** — w wycięciach zebrała się patyna/czernienie srebra (typowe dla vintage). To od razu czyta się jako WKLĘSŁE.
- Kreska ma **pełną szerokość litery** (wycięty kanał, nie włosowa rysa), na jednej krawędzi ciemniejsza, w środku plamista, jaśniejsze przetarcia.
- Krawędzie lekko poszarpane i miękkie, litery miejscami przetarte/niedocięte, drobne ubytki, kropki i plamki nalotu.
- Kontrast umiarkowany, wszystko trochę „brudne”, z rysami na powierzchni przechodzącymi przez litery.
- Wada: napis jest płasko „frontalnie”, nie leży w perspektywie tacki. Krój szeryfowy (nasze logo jest bezszeryfowe).

## Plan
- Ścieżka A (AI): NB2, Image 1 = tacka.jpg, Image 2 = referencja-styl-graweru-zblizenie.png (TYLKO technika/patyna), Image 3 = logo (kształty liter), perspektywa tacki → wklejka na oryginał jak w sesji 05. 4 seedy.
- Ścieżka B (lokalnie, 0 zł): `02-system-skladanki` w trybie „ciemna patyna”: pełne litery logo w perspektywie, ciemny, plamisty kanał, przetarcia.
