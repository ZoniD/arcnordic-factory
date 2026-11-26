#!/usr/bin/env sh
# Opretter/opdaterer fabrikkens labels i det aktuelle GitHub-repo. Kræver: gh auth login
set -e
cd "$(dirname "$0")"
python -I -c "import json;[print(l['name']+'\t'+l['color']+'\t'+l['description']) for l in json.load(open('labels.json',encoding='utf-8'))]" |
while IFS="$(printf '\t')" read -r name color desc; do
  gh label create "$name" --color "$color" --description "$desc" --force
done
