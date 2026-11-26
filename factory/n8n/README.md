# n8n-workflows

| Fil | Workflow | Tilstande |
|---|---|---|
| `1-refine.json` | Hver 2. min: finder opgaver i **Ideas** og svar fra dig i **Ready for approval**, kører AI-trinnet (gpt-oss:20b via Ollama), tjekker svaret og skriver specifikationen som kommentar | Ideas → Refining → Ready for approval |
| `2-start.json` | Hvert minut: tager den ældste **Approved**, hvis intet andet bygges, og skriver kommandoen til kodeagenten (basic A) | Approved → Building |
| `3-track-prs.json` | Hver 2. min: kobler pull requests til opgaver via branchen `issue-N` | Building → Your QA → Done |

JSON-filerne genereres af `build.py`, som indsætter prompten fra `factory/prompts/refine-system-prompt.md`.
Ret derfor prompten eller `build.py`, ikke JSON'en, og kør `python factory/n8n/build.py`.

## Designvalg
- **Labels er tilstanden.** n8n læser og sætter dem. Kun mennesket sætter `Approved`.
- **Polling, ikke webhooks.** GitHub kan ikke kalde n8n på en laptop.
- **Markører i kommentarer** (`<!-- factory:... -->`): n8n skriver med samme token som dig, så markøren skiller fabrikkens kommentarer fra dine.
- **AI-svaret valideres** (gyldig JSON og alle 10 afsnit). Ellers tilbage til Ideas med højst 3 forsøg.
- **Ingen dobbeltkørsel:** en opgave flyttes til `Refining` eller `Building`, før det langsomme arbejde starter, så næste kørsel ikke tager den igen.
- **Én opgave ad gangen:** Start-workflowet venter, så længe noget er i `Building` eller `Waiting for you`.

## Opsætning
1. Opret en **fine-grained token** på GitHub: Settings → Developer settings → Fine-grained tokens → Generate.
   Kun repoet `arcnordic-factory`. Rettigheder: **Issues: Read and write**, **Pull requests: Read**, **Contents: Read** (Metadata: Read sættes automatisk).
2. I n8n: Credentials → **GitHub arcnordic-factory** → Value: `Bearer <din token>` → Save.
3. Importér workflows (Workflows → Import from file) eller med `n8n import:workflow`, og slå dem til (Active).
4. Ollama skal køre på værten med `gpt-oss:20b`. n8n i Docker når den på `host.docker.internal:11434`.
