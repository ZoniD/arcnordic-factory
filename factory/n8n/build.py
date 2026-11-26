"""Genererer fabrikkens n8n-workflows som JSON.

Kør:  python factory/n8n/build.py
Prompten til AI-trinnet læses fra factory/prompts/refine-system-prompt.md, så filen i repoet
og prompten i n8n altid er den samme. Importér derefter JSON-filerne i n8n (se factory/n8n/README.md).
"""
import hashlib
import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent

REPO = "ZoniD/arcnordic-factory"
API = f"https://api.github.com/repos/{REPO}"
OLLAMA = "http://host.docker.internal:11434/api/chat"
MODEL = "gpt-oss:20b"
CRED = {"httpHeaderAuth": {"id": "ghFactoryCred001", "name": "GitHub arcnordic-factory"}}

# Markører i kommentarer, så fabrikken kan kende sine egne kommentarer fra dine
# (n8n skriver med din token, så afsenderen er den samme).
MARK_REFINE = "<!-- factory:refine -->"
MARK_FAIL = "<!-- factory:refine-fejl -->"
MARK_START = "<!-- factory:start -->"
MARK_PR = "<!-- factory:pr -->"

HEADINGS = ["Opgave", "Hvorfor", "Område", "Afhænger af", "Krav", "Data og regler",
            "Begrænsninger", "Acceptkriterier", "Uden for scope", "Størrelse"]

SYSTEM_PROMPT = (ROOT / "factory/prompts/refine-system-prompt.md").read_text(encoding="utf-8")

_pos = {"x": 0}


def node(name, ntype, version, params, **extra):
    _pos["x"] += 240
    n = {"parameters": params, "name": name, "type": ntype, "typeVersion": version,
         "position": [_pos["x"], 300], "id": str(uuid.UUID(hashlib.md5(name.encode()).hexdigest()))}
    n.update(extra)
    return n


def schedule(minutes):
    return node(f"Hvert {minutes}. minut", "n8n-nodes-base.scheduleTrigger", 1.2,
                {"rule": {"interval": [{"field": "minutes", "minutesInterval": minutes}]}})


def github(name, method, url, body_expr=None, execute_once=False):
    """HTTP-kald til GitHub med token fra n8n Credentials. Svar hentes som tekst, så en liste
    ikke splittes i mange items; Code-noderne parser den selv."""
    params = {
        "method": method, "url": url,
        "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
        "sendHeaders": True,
        "headerParameters": {"parameters": [
            {"name": "Accept", "value": "application/vnd.github+json"},
            {"name": "X-GitHub-Api-Version", "value": "2022-11-28"}]},
        "options": {"response": {"response": {"responseFormat": "text", "outputPropertyName": "data"}}},
    }
    if body_expr:
        params.update({"sendBody": True, "specifyBody": "json", "jsonBody": body_expr})
    extra = {"credentials": CRED, "retryOnFail": True, "maxTries": 3, "waitBetweenTries": 3000}
    if execute_once:
        extra["executeOnce"] = True
    return node(name, "n8n-nodes-base.httpRequest", 4.2, params, **extra)


def code(name, js, each=False):
    params = {"jsCode": js.strip()}
    if each:
        params["mode"] = "runOnceForEachItem"
    return node(name, "n8n-nodes-base.code", 2, params)


def workflow(wid, name, nodes):
    conns = {}
    for a, b in zip(nodes, nodes[1:]):
        conns[a["name"]] = {"main": [[{"node": b["name"], "type": "main", "index": 0}]]}
    _pos["x"] = 0
    return {"id": wid, "name": name, "active": False, "nodes": nodes, "connections": conns,
            "settings": {"executionOrder": "v1", "timezone": "Europe/Copenhagen"},
            "pinData": {}, "tags": []}


JS_CONST = f"""
const MARK_REFINE = {json.dumps(MARK_REFINE)};
const MARK_FAIL = {json.dumps(MARK_FAIL)};
const MARK_START = {json.dumps(MARK_START)};
const MARK_PR = {json.dumps(MARK_PR)};
const labelsOf = (i) => i.labels.map((l) => l.name);
const issueNo = (c) => Number(c.issue_url.split('/').pop());
"""

# ---------------------------------------------------------------- 1. Refine
find_refine = JS_CONST + """
// Finder opgaver til AI-trinnet:
//  - nye opgaver med labelen Ideas
//  - opgaver i Ready for approval, hvor din seneste kommentar er nyere end AI'ens
const issues = JSON.parse($('Hent åbne issues').first().json.data).filter((i) => !i.pull_request);
const comments = JSON.parse($('Hent kommentarer').first().json.data);
const byIssue = {};
for (const c of comments) (byIssue[issueNo(c)] ??= []).push(c);

const out = [];
for (const i of issues) {
  const labels = labelsOf(i);
  const cs = (byIssue[i.number] || []).sort((a, b) => a.created_at.localeCompare(b.created_at));
  const last = cs[cs.length - 1];
  const fejl = cs.filter((c) => c.body.includes(MARK_FAIL)).length;
  const ny = labels.includes('Ideas') && fejl < 3;   // højst 3 forsøg ved ugyldigt AI-svar
  const svar = labels.includes('Ready for approval') && last && !last.body.includes(MARK_REFINE);
  if (!ny && !svar) continue;
  out.push({ json: {
    number: i.number, title: i.title, body: i.body || '', reason: ny ? 'ny opgave' : 'svar fra dig',
    comments: cs.filter((c) => !c.body.includes(MARK_FAIL)).map((c) => ({
      ai: c.body.includes(MARK_REFINE) || c.body.includes('<!-- factory:'),
      body: c.body.replace(/<!-- factory:[a-z-]+ -->/g, '').trim(),
    })),
  } });
}
return out;
"""

build_prompt = f"""
// Bygger beskeden til modellen: systemprompt fra factory/prompts/refine-system-prompt.md
// og opgaven med hele kommentarhistorikken.
const SYSTEM = {json.dumps(SYSTEM_PROMPT, ensure_ascii=False)};
const t = $('Find opgaver').item.json;
const historik = t.comments.map((c) => (c.ai ? 'AI-trinnet' : 'Mennesket') + ':\\n' + c.body).join('\\n\\n---\\n\\n') || 'ingen';
const user = `Titel: ${{t.title}}\\n\\nBeskrivelse:\\n${{t.body || '(tom)'}}\\n\\nTidligere kommentarer:\\n${{historik}}`;
return {{ json: {{ number: t.number, ollama: {{
  model: {json.dumps(MODEL)}, stream: false, format: 'json',
  options: {{ temperature: 0.2, num_ctx: 16384 }},
  messages: [{{ role: 'system', content: SYSTEM }}, {{ role: 'user', content: user }}],
}} }} }};
"""

check_answer = JS_CONST + f"""
// Stoler ikke blindt på modellen: svaret skal være gyldig JSON med alle afsnit fra skabelonen.
const HEADINGS = {json.dumps(HEADINGS, ensure_ascii=False)};
const n = $('Byg prompt').item.json.number;
let j = null, fejl = null;
try {{ j = JSON.parse($json.message.content); }} catch (e) {{ fejl = 'ugyldig JSON'; }}
if (!fejl && typeof j.spec !== 'string') fejl = 'mangler spec';
if (!fejl) {{
  const mangler = HEADINGS.filter((h) => !j.spec.includes('## ' + h));
  if (mangler.length) fejl = 'mangler afsnit: ' + mangler.join(', ');
}}
if (fejl) return {{ json: {{ number: n, label: 'Ideas',
  comment: `${{MARK_REFINE}}\\n${{MARK_FAIL}}\\n⚠️ AI-trinnet gav et ugyldigt svar (${{fejl}}). Fabrikken prøver igen (højst 3 gange).` }} }};

const q = Array.isArray(j.questions) ? j.questions.filter(Boolean) : [];
const ready = j.ready === true && !j.spec.includes('[AFKLARES') && q.length === 0;
const comment = [
  MARK_REFINE,
  '## 🤖 Forslag til specifikation',
  `**Klar til godkendelse:** ${{ready ? '✅ ja' : '❌ ikke endnu'}}`,
  `**Råd:** ${{j.advice || '-'}}`,
  q.length ? '### Spørgsmål til dig\\n' + q.map((x, k) => `${{k + 1}}. ${{x}}`).join('\\n') : '',
  '---',
  j.spec,
  '---',
  '_Svar i en kommentar for at få en ny version, eller sæt labelen **Approved**, når du er tilfreds. AI-trinnet godkender aldrig selv._',
].filter(Boolean).join('\\n\\n');
return {{ json: {{ number: n, label: 'Ready for approval', comment }} }};
"""

refine = workflow("factoryRefine001", "Fabrik 1 – Refine (Ideas → Ready for approval)", [
    schedule(2),
    github("Hent åbne issues", "GET", f"{API}/issues?state=open&per_page=100"),
    github("Hent kommentarer", "GET", f"{API}/issues/comments?sort=created&direction=desc&per_page=100", execute_once=True),
    code("Find opgaver", find_refine),
    github("Sæt Refining", "PATCH", f"={API}/issues/{{{{ $json.number }}}}",
           "={{ JSON.stringify({ labels: ['Refining'] }) }}"),
    code("Byg prompt", build_prompt, each=True),
    node(f"AI-trin ({MODEL})", "n8n-nodes-base.httpRequest", 4.2, {
        "method": "POST", "url": OLLAMA, "sendBody": True, "specifyBody": "json",
        "jsonBody": "={{ JSON.stringify($json.ollama) }}", "options": {"timeout": 900000}},
        retryOnFail=True, maxTries=2, waitBetweenTries=5000),
    code("Tjek svar", check_answer, each=True),
    github("Skriv kommentar", "POST", f"={API}/issues/{{{{ $json.number }}}}/comments",
           "={{ JSON.stringify({ body: $json.comment }) }}"),
    github("Sæt label", "PATCH", f"={API}/issues/{{{{ $('Tjek svar').item.json.number }}}}",
           "={{ JSON.stringify({ labels: [$('Tjek svar').item.json.label] }) }}"),
])

# ---------------------------------------------------------------- 2. Start
find_start = JS_CONST + """
// Én opgave ad gangen: kun hvis intet er i Building eller Waiting for you.
const issues = JSON.parse($('Hent åbne issues').first().json.data).filter((i) => !i.pull_request);
const busy = issues.some((i) => labelsOf(i).includes('Building') || labelsOf(i).includes('Waiting for you'));
if (busy) return [];
const next = issues.filter((i) => labelsOf(i).includes('Approved')).sort((a, b) => a.number - b.number)[0];
if (!next) return [];
const n = next.number;
const comment = [
  MARK_START,
  `## 🏭 Klar til at bygge (issue #${n})`,
  'Basic A: start kodeagenten selv i repoet:',
  '```sh',
  'git checkout main && git pull',
  `git checkout -b issue-${n}`,
  `claude "Byg GitHub-issue #${n}. Læs det med: gh issue view ${n} --comments. Brug den seneste specifikation fra AI-trinnet og mine svar. Følg CLAUDE.md, og spørg mig, hvis noget er uklart."`,
  '```',
  'Når agenten er færdig:',
  '```sh',
  `git push -u origin issue-${n}`,
  `gh pr create --fill --body "Closes #${n}"`,
  '```',
  'Fabrikken ser pull requesten og flytter opgaven til **Your QA**.',
].join('\\n');
return [{ json: { number: n, comment } }];
"""

start = workflow("factoryStart0001", "Fabrik 2 – Start opgave (Approved → Building)", [
    schedule(1),
    github("Hent åbne issues", "GET", f"{API}/issues?state=open&per_page=100"),
    code("Vælg næste opgave", find_start),
    github("Sæt Building", "PATCH", f"={API}/issues/{{{{ $json.number }}}}",
           "={{ JSON.stringify({ labels: ['Building'] }) }}"),
    github("Skriv instruktion", "POST", f"={API}/issues/{{{{ $('Vælg næste opgave').item.json.number }}}}/comments",
           "={{ JSON.stringify({ body: $('Vælg næste opgave').item.json.comment }) }}"),
])

# ---------------------------------------------------------------- 3. Følg pull requests
find_pr = JS_CONST + """
// Kobler pull requests til opgaver via branchnavnet issue-N.
//  Building + åben PR (opdateret efter start)  -> Your QA
//  Your QA + PR merget eller lukket             -> Done (issuet lukkes)
//  issue lukket uden Done                       -> Done
const prs = JSON.parse($('Hent pull requests').first().json.data);
const issues = JSON.parse($('Hent alle issues').first().json.data).filter((i) => !i.pull_request);
const comments = JSON.parse($('Hent kommentarer').first().json.data);
const out = [];
for (const i of issues) {
  const labels = labelsOf(i);
  if (labels.includes('Done')) continue;
  const pr = prs.find((p) => p.head.ref === `issue-${i.number}`);
  const starts = comments.filter((c) => issueNo(c) === i.number && c.body.includes(MARK_START))
    .map((c) => c.created_at).sort();
  const startTid = starts[starts.length - 1] || '';
  if (i.state === 'closed') {
    const note = pr && pr.merged_at ? `✅ PR #${pr.number} er merget. Opgaven er færdig.` : '🗑️ Issuet er lukket uden merge.';
    out.push({ json: { number: i.number, patch: { labels: ['Done'] }, note } });
  } else if (pr && pr.state === 'open' && labels.includes('Building') && pr.updated_at > startTid) {
    out.push({ json: { number: i.number, patch: { labels: ['Your QA'] },
      note: `🔍 PR #${pr.number} er klar til din review: ${pr.html_url}\\n\\nMerge den, luk den, eller send opgaven tilbage med en kommentar og labelen **Approved**.` } });
  } else if (pr && pr.state === 'closed' && labels.includes('Your QA')) {
    const note = pr.merged_at ? `✅ PR #${pr.number} er merget. Opgaven er færdig.` : `🗑️ PR #${pr.number} blev lukket uden merge.`;
    out.push({ json: { number: i.number, patch: { labels: ['Done'], state: 'closed' }, note } });
  }
}
return out;
"""

track = workflow("factoryTrackPR01", "Fabrik 3 – Følg pull requests (Your QA → Done)", [
    schedule(2),
    github("Hent pull requests", "GET", f"{API}/pulls?state=all&sort=updated&direction=desc&per_page=50"),
    github("Hent alle issues", "GET", f"{API}/issues?state=all&per_page=100", execute_once=True),
    github("Hent kommentarer", "GET", f"{API}/issues/comments?sort=created&direction=desc&per_page=100", execute_once=True),
    code("Find ændringer", find_pr),
    github("Opdatér issue", "PATCH", f"={API}/issues/{{{{ $json.number }}}}",
           "={{ JSON.stringify($json.patch) }}"),
    github("Skriv status", "POST", f"={API}/issues/{{{{ $('Find ændringer').item.json.number }}}}/comments",
           "={{ JSON.stringify({ body: '" + MARK_PR + "\\n' + $('Find ændringer').item.json.note }) }}"),
])

for fname, wf in [("1-refine.json", refine), ("2-start.json", start), ("3-track-prs.json", track)]:
    (OUT / fname).write_text(json.dumps(wf, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("skrev", fname, len(wf["nodes"]), "noder")
