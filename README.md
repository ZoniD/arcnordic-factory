# ARCnordic-fabrikken

Afsluttende projekt i AI-Agenter E2026: en lille softwarefabrik, hvor en specifikation bliver til en pull request,
bygget af en kodeagent, og hvor et menneske bestemmer, hvad der bliver accepteret.

| Mappe | Indhold |
|---|---|
| `factory/n8n/` | n8n-workflows som JSON (importeres i n8n efter review) |
| `factory/prompts/` | Spec-skabelon og prompt til AI-trinnet |
| `factory/runner/` | Runneren, der starter kodeagenten (basic B) |
| `app/` | Det fabrikken bygger: små byggeværktøjer på **fiktive data** (React + TypeScript). Intet er rigtige ARCnordic-data eller -værktøjer |
| `docs/` | Arkitektur, evaluering og rapport |

## Opgavens tilstande
Hver opgave er et issue, og dets label er dets tilstand:
Ideas → Refining → Ready for approval → Approved → Building → (Waiting for you | Stuck) → Your QA → Done.
Kun et menneske sætter **Approved**, og intet merges til `main` uden review.

## Opsætning
1. `gh auth login`
2. `sh factory/setup-labels.sh`
3. Start n8n (Docker) og importér workflows fra `factory/n8n/`.
