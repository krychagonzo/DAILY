# Sesja 19 — 4 generacje finalne

Wnioski z analizy sesji 18 wprowadzone do promptu: kontrast jak ornament (+10…15), rowek zamiast płaskiego wypełnienia, miękkie krawędzie, gradient światła, rysy przez litery, Λ jako odwrócone V.

- Image 1 = referencja-wypelniony-napis.png, Image 2 = ornament-zblizenie-3x.png
- Nano Banana Pro, 2K, seedy 191–194, zero obróbki. Prompt: `prompt.txt`

## Werdykt
Pomiary (metal ~146; ornament ~+12…15):
| seed | litery | różnica | „Λ” w VINTAGE |
|---|---|---|---|
| 191 | 144 | −2 | ✗ poprzeczka |
| 192 | 152 | +5 | ✗ poprzeczka |
| 193 | 137 | −10 (ciemniejsze) | ✓ |
| **194** | **161** | **+15 (jak ornament)** | **✓** |

- **pro-seed194 — FINAŁ.** Logotyp 1:1 z „Λ”, kontrast jak ornament, miękkie krawędzie, rowek zamiast płaskiego wypełnienia, rysy tacy przechodzą przez litery, ornament/taca/dywan bez zmian.
- pro-seed193 — alternatywa: „Λ” poprawne, wyraźniej wycięty rowek z ciemniejszą ścianką (bardziej „głęboki”, ostrzejszy).
- 191 i 192 odrzucone (poprzeczka w „A”). Zbliżenie litery: `litera-lambda-porownanie.png` (191, 192, 193, 194).
