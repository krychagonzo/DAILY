# Grawer logo „A Certain Era” na tacce

| folder | co jest w środku |
|---|---|
| `00-materialy/input/` | zdjęcie tacki, logo, zbliżenie istniejącego grawerunku |
| `01-research/` | research realizmu graweru, poradnik promptowania Nano Banana, historia promptów |
| `02-system-skladanki/` | lokalny skrypt rysujący grawer (bez AI) + składanki i maski |
| `sesje/NN-nazwa/` | każda sesja generacji osobno: `README.md` (model, prompt, werdykt) + wyniki |

## Sesje
| # | co | wynik |
|---|---|---|
| 01 | NB2 1K, pierwsza próba | za duże, ciemne, „A” z poprzeczką |
| 02 | NB2 2K, płytki wklęsły | podwójny kontur, wygląda na wypukłe |
| 03 | NB2 vs Pro + zbliżenie wzoru | **NB2 najlepszy dotąd**; Pro odpada |
| 04 | harmonizacja składanki + poprawka v3 | AI wraca do czystego fontu; składanka lokalna bardziej realistyczna |
| 05 | NB2 prompt B na oryginale + wklejka; Flux Fill | jasny włosowy grawer, oryginalny dywan i tacka |
| 06 | styl z referencji: ciemna patyna w rowkach | za sztuczne wg klienta |
| 07 | czysta generacja, krótki prompt, referencja stylu | realistyczny grawer, ale krój szeryfowy z referencji |
| 08 | czysta generacja, krój z logo | **`sesje/08-…/pro-seed81.png` — najlepszy z krojem z logo** (za czysty) |
| 09 | referencje = wyniki sesji 07 | świetne postarzenie, ale znów krój szeryfowy |
| 10 | postarzenie wyniku 08 (krój z logo) + referencje 07/09 | dobre, ale za mocno postarzone |
| 11 | przygaszenie + spójność ze stanem tacy | dobre, ale grawer za głęboki, logotyp niezgodny |
| 12 | płytki grawer + wierny logotyp | płytki, ale kreska grubsza niż w logo |
| 13 | technika i światło jak istniejący ornament | **`sesje/13-…/pro-seed133.png` — najlepszy dotąd (ton/światło zgodne z ornamentem)** |
