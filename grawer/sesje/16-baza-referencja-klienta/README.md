# Sesja 16 — baza: referencja klienta (dokładny logotyp + perspektywa)

Feedback po s15: tylko 2 warianty; s15 seed154 za bardzo się wybija; „A” w VINTAGE musi być Λ; logotyp 100% jak w logo. Klient dostarczył referencję z logo w perspektywie (kontury).

- Image 1 = 00-materialy/input/referencja-perspektywa-logo.png, Image 2 = logo, Image 3 = ornament-zblizenie-3x.png
- Nano Banana Pro, 2K, seedy 161, 162, zero obróbki. Prompt: `prompt.txt`

## Werdykt
- pro-seed161: model wygenerował zupełnie inne zdjęcie (inna taca, czerwony dywan, krój szeryfowy) — odrzucone.
- pro-seed162: krój i perspektywa z referencji zachowane, ale litery wyglądają na WYPUKŁE (jasna faza na dole), a „A” w VINTAGE znów z poprzeczką — odrzucone.
- Wniosek: same kontury liter mylą model (czyta je jako relief). Propozycja: lokalnie wypełnić kontury z referencji płaskim szarym (dokładny kształt), a modelowi zlecić tylko zmianę powierzchni.
