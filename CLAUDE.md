# Instruktioner til kodeagenten

Du arbejder i ARCnordic-fabrikken. Du får én opgave (et GitHub-issue) ad gangen og arbejder kun på branchen `issue-N`.

## Regler
- Arbejd kun i den mappe opgaven nævner (`app/` eller `factory/`).
- Gæt ikke. Er specifikationen uklar, så stop og stil et spørgsmål.
- Alle data og regler er fiktive. Brug kun de værdier opgaven eller `app/data/` angiver, og opfind ikke andre.
- Ændr ikke eksisterende tests eller `.github/`, medmindre opgaven udtrykkeligt beder om det.
- Tilføj ingen nye afhængigheder uden at opgaven tillader det.
- Skriv tests til ny logik og kør `npm test` i `app/` før du stopper.
- Commit med en kort besked. Push ikke, og merge aldrig. Det gør fabrikken og mennesket.

## Afslut altid med præcis én af disse linjer som sidste linje
STATUS: DONE - <kort opsummering>
STATUS: QUESTION - <dit spørgsmål>
STATUS: STUCK - <hvad der gik galt>
