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

## Wynik B — lokalnie, tryb `patina` (0 zł, bez AI)
Polecenie: `python3 02-system-skladanki/make_composite.py patina [seed=4] [depth=0.46] [nazwa]`

- `B-lokalna-patyna-FINAL.png` (2076×2576) + `B-lokalna-patyna-zblizenie.png` (crop 800×380, powiększony 2×). Seed 4, `PAT_DEPTH=0.46`.
- Warianty: `B-lokalna-patyna-jasniejsza-*` (depth 0.34, bardziej wytarte, srebro-na-srebrze) i `B-lokalna-patyna-ciemniejsza-*` (depth 0.60, bliżej kontrastu referencji).
- Geometria: pełne kontury liter logo (nie szkielet), per-litera jitter i dryf linii bazowej z istniejącego kodu, ta sama homografia co tryby `cartouche`/`third` (pochylenie −7°, skrót 0.84, keystone 0.985). Środek (1062, 1302) jak w sesji 05 A-seed44. „A Certain Era” ma 590 px, czyli około 40% wewnętrznego owalu. Λ w VINTAGE bez poprzeczki, zgodnie z logo.
- Kanał: `multiply` ciemną patyną. Skład:
  - nisko-częstotliwościowe plamy (`PAT_MOTTLE` 0.32) plus drobny szum i speckle;
  - jaśniejsze wytarcia (`PAT_WORN` 25%);
  - profil przekroju: nalot zbiera się przy ściankach, dno jest jaśniejsze (`PAT_FLOOR` 0.55);
  - górna ścianka dodatkowo przyciemniona: maska przesunięta o 1.2 px (`PAT_WALL` 0.22);
  - na dolnej krawędzi cienki jasny brzeg (`PAT_HIGHLIGHT` 0.16).
- Zużycie: poszarpane krawędzie (`PAT_RAGGED`), płytkie „niedocięcia” z wolnego szumu (głębokość 0.55–1.0) i drobne wyszczerbienia (3.5% powierzchni, spłycone o 70%, nie przecięte, żeby litery zostały czytelne).
- Wokół i na literach: 35 plamek nalotu i 34 cienkie rysy powierzchni. Rysy zdzierają patynę tam, gdzie przecinają litery. Ornament kwiatowy pozostaje widoczny pod literami: część jego high-passu jest dodawana z powrotem (`PAT_FLORAL` 0.8).
- Wykończenie: blur 0.65 px i ziarno 1.1 poziomu w przyciemnionych miejscach.
- Poza elipsą o miękkiej krawędzi wokół napisu (+40/+34 px, feather 6 px) obraz jest bit-identyczny z `tacka.jpg`. Sprawdzone: 0 różnic poza obszarem napisu.

**Ocena realizmu.** Przy normalnym oglądaniu napis czyta się jak stary, zaśniedziały grawer i dobrze leży w perspektywie tacki, czyli lepiej niż referencja. Wady:
- wklęsłość wynika głównie z ciemnego wypełnienia. Ścianka i blik są subtelne, więc przy 2× litery wyglądają trochę jak „wtarty tusz”, a nie jak rowek z prawdziwym oświetleniem;
- krój bezszeryfowy o stałej grubości wygląda bardziej maszynowo niż ręcznie (to ma też referencja);
- tekstura patyny jest proceduralna i przy dużym powiększeniu widać jej powtarzalność.

## Ścieżka A — wyniki (NB2, prompt `prompt-A.txt`, wklejka na oryginał: elipsa 1062,1309 / 600×215, rozmycie 40 px)
- **seed54 → `A-patyna-seed54-FINAL.png` — NAJLEPSZY.** Ciemne, plamiste kanały z patyną, czytają się jako wklęsłe; perspektywa tacki poprawna; „Λ” poprawne; ślady nalotu i przetarcia. Wada: model wyczyścił ornament w samym środku (wygląda jak wypolerowane pole pod napis).
- seed51: podobny styl, mocniej brudny, ornament zostaje; „A” w VINTAGE z poprzeczką.
- seed52: bardzo czysty, ciemny, zbyt „nowy”.
- seed53: dużo rys i zużycia, napis jaśniejszy/przetarty.
- Porównanie: `A-porownanie-4-seedow-zblizenia.png` (kolejno 51, 52, 53, 54).
- Lokalna ścieżka B: wygląda bardziej jak stempel tuszem niż grawer — słabsza od A.
