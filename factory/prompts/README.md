# Prompts
- `spec-template.md` – skabelonen alle opgaver omskrives til, og begrundelser for designet.
- `refine-system-prompt.md` – systemprompten til AI-trinnet i n8n (Refining → Ready for approval).

AI-trinnet får som brugerbesked: issue-titel, issue-tekst og tidligere kommentarer. Det svarer med JSON, som n8n
laver om til en kommentar på issuet: specifikation, spørgsmål og råd. Mennesket svarer i en kommentar
(tilbage til Refining) eller sætter labelen Approved.
