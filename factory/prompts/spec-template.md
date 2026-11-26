# Spec-skabelon

Alle opgaver bliver omskrevet til denne skabelon af AI-trinnet i n8n, før de kan godkendes.
Kodeagenten får altid de samme afsnit i samme rækkefølge.

```markdown
## Opgave
<Én sætning: hvad skal bygges.>

## Hvorfor
<Hvem i Fiktiv Rådgivning A/S har gavn af det, og hvad de kan bagefter.>

## Område
Mappe: app/ | factory/
Filer der sandsynligvis berøres: <liste eller "ukendt">

## Afhænger af
<#issue-numre der skal være Done først, eller "ingen">

## Krav
1. <Konkret, observerbart krav>
2. ...

## Data og regler
<Præcise fiktive værdier, grænser og formler opgaven bruger. Henvis til app/data/. "ingen" hvis ikke relevant.>

## Begrænsninger
- Ingen nye afhængigheder <medmindre andet står her>
- Ændr ikke eksisterende tests eller .github/
- <øvrige>

## Acceptkriterier
- [ ] Givet <situation>, når <handling>, så <forventet resultat>
- [ ] `npm test` i app/ består, og der er nye tests for <logik>
- [ ] <manuelt tjek, hvis noget ikke kan testes automatisk – markér det "(manuelt)">

## Uden for scope
- <Hvad opgaven ikke skal>

## Størrelse
S | M | L   (L skal deles op før godkendelse)
```

## Designvalg (til rapporten)
- **Fast rækkefølge og overskrifter:** agenten og runneren kan stole på strukturen, og forskelle mellem opgaver bliver kun indhold.
- **Hvorfor før hvordan:** som i spec-driven development (uge 10). Teknologivalg overlades til agenten inden for begrænsningerne.
- **Acceptkriterier som Givet/Når/Så:** de kan oversættes direkte til tests, så "færdig" betyder noget andet end "agenten stoppede".
- **Data og regler eksplicit:** alle tal er fiktive og skal stå i opgaven, så agenten ikke opfinder dem.
- **Afhænger af:** fabrikken bygger én opgave ad gangen; afhængigheder gør rækkefølgen synlig.
- **Uden for scope og Størrelse:** holder pull requests små nok til en ordentlig review.
- **Manuelle kriterier markeres:** gør det ærligt, hvor automatiske tests ikke rækker.
