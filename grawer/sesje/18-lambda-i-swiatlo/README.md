# Sesja 18 — wymuszenie Λ + światło jak ornament (jaśniejsze, nie ciemniejsze)

- Image 1 = referencja-wypelniony-napis.png, Image 2 = ornament-zblizenie-3x.png
- „A” w VINTAGE opisane jako odwrócone V (nie nazywane literą A); grawer jaśniejszy od metalu jak ornament
- Nano Banana Pro, 2K, seedy 181–184, zero obróbki. Prompt: `prompt.txt`

## Werdykt
- **„Λ” poprawne w pro-seed182 i pro-seed183** (opis litery jako „odwrócone V” zamiast „A” zadziałał w 2/4). W 181 i 184 nadal poprzeczka.
- Światło: litery teraz jaśniejsze od metalu (jak ornament), perłowo-srebrne, niski kontrast — zgodnie z analizą światła.
- **pro-seed182 — najlepszy:** gładkie, spokojne, jasne litery, logotyp 1:1, „Λ” poprawne.
- pro-seed183: logotyp 1:1, „Λ” poprawne; wnętrze bardziej szronione/iskrzące.

## Analiza (po feedbacku) — co poprawić
Zbliżenie `analiza-zblizenie.png`: baza klienta (ciemny napis) / seed182 / seed183 / ornament tacy, ta sama skala 3x.

Pomiary jasności (0–255): metal ~145; linie ornamentu ~158 (+12…15); litery seed182 ~178 (+33), seed183 ~166 (+21).
1. **Za duży kontrast** — litery 182 ok. 2× jaśniejsze względem metalu niż ornament; 183 bliżej, ale wciąż za jasne. Cel: +10…15, jak ornament.
2. **Płaskie wypełnienie jak folia/naklejka** — cała litera jednolicie jasna z ostrym, jasnym obrzeżem (182 ma jasną fazę na dolnej krawędzi → lekko „wypukłe”, jak hot-stamping). Prawdziwy rowek: jedna ścianka (zwrócona do światła z góry) jaśniejsza, środek/druga ścianka ciemniejsza, wnętrze nie jest równe.
3. **Faktura 183** — drobny brokat/szum w środku liter, sztuczny.
4. **Za ostre krawędzie** — litery ostrzejsze niż reszta zdjęcia z telefonu (ornament jest miękki, lekko rozmyty, z przerwami).
5. **Brak zmienności** — wszystkie litery tak samo jasne; brak gradientu (jaśniej na dole tacy, ciemniej u góry) i różnic zależnych od kierunku kreski.
6. **Brak śladów wieku** — rysy tacy nie przechodzą przez litery, brak miejsc przetartych.
7. **Λ** — poprawne tylko w 2/4 (opis „odwrócone V” działa częściowo) → generować kilka i wybierać.
8. Model przerysowuje całe zdjęcie (różnica ~3% na dywanie/tacy) — drobne przesunięcia kolorów/szczegółów poza napisem.
