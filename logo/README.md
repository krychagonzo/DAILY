# Logo „A Certain Era / VINTAGE” — wektor SVG
- `logo-a-certain-era.svg` — zwektoryzowane (potrace) z `logo-zrodlo.png`, jedna ścieżka, czarne wypełnienie, przezroczyste tło; „Λ” w VINTAGE bez poprzeczki jak w oryginale.
- Uwaga: źródło to bitmapa ~70 px wysokości liter, więc krawędzie są minimalnie nierówne w dużym powiększeniu. Jeśli istnieje oryginalny plik logo (AI/PDF/SVG) albo nazwa fontu — warto użyć go do druku.
- `wektoryzuj_logo.py` — skrypt.

## Logo „A CERTAIN ERA / VINTAGE” (wersja bold) – `logo-a-certain-era-vintage.svg`

Źródło: `logo2-zrodlo.jpg` (słaba jakość). Wektory **nie są obrysem** zdjęcia: każda litera
to oryginalny kontur z fontu Montserrat (darmowy odpowiednik Gothama), dopasowany do
pozycji i wielkości liter z oryginału. Dzięki temu krawędzie są idealnie proste i gładkie.

- „A CERTAIN ERA”: Montserrat, grubość 720 (≈ Bold)
- „VINTAGE”: Montserrat, grubość 450 (≈ Book/Regular), szeroki rozstrzał liter jak w oryginale
- Jedna ścieżka, kolor #000, same krzywe (bez fontów)
- `porownanie-logo-vintage.png`: czarne = zgodne, czerwone = tylko oryginał, niebieskie = tylko SVG
- Skrypt: `python3 odbuduj_logo_vintage.py Montserrat.ttf logo2-zrodlo.jpg wynik.svg`

Oryginał najpewniej jest złożony Gothamem (Bold + Book). Poprzeczki w E/R/A są w nim
odrobinę niżej, a G ma inną końcówkę. Jeśli masz licencję na Gotham, można podmienić font w skrypcie.
