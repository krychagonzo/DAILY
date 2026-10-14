# Logo „A Certain Era / VINTAGE” — wektor SVG
- `logo-a-certain-era.svg` — zwektoryzowane (potrace) z `logo-zrodlo.png`, jedna ścieżka, czarne wypełnienie, przezroczyste tło; „Λ” w VINTAGE bez poprzeczki jak w oryginale.
- Uwaga: źródło to bitmapa ~70 px wysokości liter, więc krawędzie są minimalnie nierówne w dużym powiększeniu. Jeśli istnieje oryginalny plik logo (AI/PDF/SVG) albo nazwa fontu — warto użyć go do druku.
- `wektoryzuj_logo.py` — skrypt.

## Logo „A CERTAIN ERA / VINTAGE” (wersja bold) – `logo-a-certain-era-vintage.svg`

Źródło: `logo2-zrodlo.jpg` (słaba jakość). Wektory **nie są obrysem** zdjęcia, tylko oryginalnymi
konturami fontu Montserrat (darmowy odpowiednik Gothama), które zostały **przerysowane tak, by
pokrywały się z oryginałem**. Krawędzie są proste i gładkie, a kształty zgodne z logo.

Wersja 2 (dopasowana do oryginału):
- grubość „A CERTAIN ERA”: 760, „VINTAGE”: 450
- każda litera ma pozycję, wysokość i szerokość dokładnie z oryginału
- poprawki kształtów, dobrane automatycznie przez porównanie piksel po pikselu:
  - **E**: grubsze belki górna i dolna, poprzeczka wyżej, w VINTAGE tak samo
  - **R**: krótszy i wyższy brzuszek, węższy łuk, płynnie (bez załamań)
  - **A**: poprzeczka w miejscu z oryginału (bold: niżej, VINTAGE: wyżej)
  - **G**: długa, prosta pozioma poprzeczka jak w Gothamie, na właściwej wysokości
- zgodność z oryginałem: **96,5 %** pikseli (różnice to rozmycie JPEG na krawędziach, poniżej 1 px)
- jedna ścieżka, kolor #000, bez nakładających się konturów, same krzywe
- `porownanie-logo-vintage.png`: czarne = zgodne, czerwone = tylko oryginał, niebieskie = tylko SVG

Odtworzenie: `skrypt-vintage/` (`opt.py` dobiera poprawki → `params.json`, `final.py` zapisuje SVG):
`python3 skrypt-vintage/final.py Montserrat[wght].ttf logo2-zrodlo.jpg skrypt-vintage/params.json wynik.svg`
