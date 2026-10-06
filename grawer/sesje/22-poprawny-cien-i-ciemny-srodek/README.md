# Sesja 22 — poprawny kierunek cienia (wklęsłe) + wariant z ciemnym środkiem

Feedback: cień momentami po złej stronie → grawer wygląda na wypukły. Światło z góry ⇒ w rowku ciemna GÓRNA krawędź, jasna DOLNA.
Dodatkowo 2 warianty z ciemnym (oksydowanym) środkiem wg `00-materialy/input/referencja-ciemny-srodek.jpg`.

- Image 1 = referencja-postprodukcja-klienta.png
- normalny (seed 221, 222): Image 2 = ornament-zblizenie-3x.png, `prompt-normalny.txt`
- ciemny środek (seed 223, 224): Image 2 = ornament, Image 3 = referencja-ciemny-srodek.jpg, `prompt-ciemny-srodek.txt`
- Nano Banana Pro, 2K, zero obróbki

## Werdykt
- **Kierunek cienia poprawiony we wszystkich 4** (`detal-cien.png`): ciemna linia wzdłuż górnej krawędzi kresek, jasna wzdłuż dolnej → litery czytają się jako wklęsłe.
  - normalny-seed221: wyraźniejszy rowek, jasne litery z czystą fazą.
  - normalny-seed222: najsubtelniejszy, najbliżej tonu ornamentu.
  - ciemny-seed223 / 224: oksydowany, grafitowy środek z jasną krawędzią cięcia (styl z referencji); 224 bardziej matowy i nierówny, 223 ciemniejszy i ostrzejszy.
- **„Λ” w VINTAGE z poprzeczką we wszystkich 4** (`litera-lambda-porownanie.png`: 221, 222, 223, 224) — wymaga przeniesienia litery z bazy klienta w postprodukcji.
