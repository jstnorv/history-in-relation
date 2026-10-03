# History in Relation

History in Relation is a small, independent educational web app for exploring connections between historical topics related to the lands of contemporary Ukraine and wider world history. It is not affiliated with Ukrainian History Global Initiative (UHGI).

## First milestone

- Browse and search a curated set of topics.
- Open a topic to see related topics, the type of relationship, and a short explanation.
- Follow the source link attached to each connection.

The starter graph is deliberately small. Its summaries and connections are paraphrased from UHGI's [project overview](https://uhgi.org/), which is cited in the app. This is an exploration of UHGI's framing, not independent verification or a substitute for scholarly sources. Expanding the graph should include source research and attribution for every new claim.

## Run locally

From this directory:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run --debug
```

Open the local address printed by Flask. On Windows, activate the environment with `.venv\Scripts\activate`.

The SQLite database is created and seeded on first run. Set `UHGI_DATABASE` to use a different database path.

## AI assistance

GitHub Copilot was used to help draft and refine the app's code. The project idea, research decisions, and final review should remain the student's responsibility; review and personalize this disclosure to reflect the actual work before submission.
