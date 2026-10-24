# Ikony PPL – wektory SVG

| Plik | Opis |
|---|---|
| `ppl-logo.svg` | logo PPL, koło w kolorze #004B85, białe elementy są przezroczyste (wycięte) |
| `ppl-logo-biale.svg` | to samo w kolorze białym (na ciemne tło) |
| `fundacja-ppl-biale.svg` | Fundacja PPL, białe na przezroczystym (jak oryginał PNG) |
| `fundacja-ppl-czarne.svg` | Fundacja PPL, wersja czarna |
| `podglad.png` | podgląd wszystkich wersji |
| `ppl-porty-lotnicze.svg` | logo PPL Porty Lotnicze (znak + napis), #004B85 |
| `ppl-porty-lotnicze-biale.svg` | to samo w bieli, na ciemne tło |
| `podglad-porty-lotnicze.png` | podgląd |

Źródła: `ppl-zrodlo.jpg`, `fundacja-ppl-zrodlo.png`.

## Jak powstały (wersja 2 – wygładzona)
Pliki nie są surowym obrysem pikseli. Skrypt `wektoryzuj.py` czyści geometrię tak, jak rysuje się logo:
- **koło** jest matematycznie idealnym okręgiem (dopasowanym do oryginału), a kształty są do niego przycięte
- **proste krawędzie** to prawdziwe odcinki; poziome i pionowe są dokładnie pod 0°/90°,
  a pochylone krawędzie liter PPL mają jeden wspólny kąt kursywy (100,5°)
- **łuki** są wygładzone i opisane możliwie małą liczbą krzywych Béziera, bez falowania z kompresji JPG
- drobne „schodki” na styku łuku i prostej z oryginału zostały usunięte
- zgodność z oryginałem około 98,5% pikseli; różnice to wyłącznie wygładzone krawędzie

Uruchomienie: `python3 wektoryzuj.py <źródło> niebieski|alfa <kolor> <wynik.svg> <tytuł>`
Kolor #004B85 odczytano ze zdjęcia JPG, więc oficjalny kolor z księgi znaku może się minimalnie różnić.

## PPL Porty Lotnicze
- znak: ten sam wygładzony `ppl-logo.svg`, przeskalowany i ustawiony dokładnie na kole z `porty-lotnicze-zrodlo.png`
- napis: **złożony z konturów fontu Tahoma** (wersja otwarta z projektu Wine, licencja LGPL), a nie obrysowany.
  Skala, pozycje słów, rozstrzał i drobne korekty liter dopasowane do źródła (`napis-tahoma-dopasowanie.json`).
  W wersji Wine litera „y” ma zakrzywiony ogonek, więc poprawiono ją na prosty, jak w oryginalnej Tahomie.
- skrypty: `napis_z_fontu.py` (napis) → `zloz_porty_lotnicze.py` (znak + napis, jedna ścieżka)
