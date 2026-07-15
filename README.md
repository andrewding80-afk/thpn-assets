# THPN Asset Pipeline

Generates The Handpulled Noodle lifecycle assets via the OpenAI Images API.

- `inputs/` — vector blueprints (geometry law) and style references
- `jobs/` — one JSON per generation job: prompt + inputs + variant count
- `pipeline/generate.py` — calls the images edits endpoint
- `outputs/` — generated variants, committed by the workflow

Run: Actions → Generate assets → Run workflow. Leave "jobs" blank for all,
or name specific jobs, e.g. `landscape_master`.

Requires repository secret `OPENAI_API_KEY`.
