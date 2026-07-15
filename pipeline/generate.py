"""THPN asset generation pipeline.
Runs image-edit jobs against the OpenAI Images API (gpt-image-1).
Each job is a JSON file in jobs/ specifying prompt, input images, size, and variant count.
Results are written to outputs/{job_name}/ and committed by the workflow.
"""
import base64
import json
import os
import pathlib
import sys

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
API_KEY = os.environ["OPENAI_API_KEY"]
ENDPOINT = "https://api.openai.com/v1/images/edits"


def run_job(job_path: pathlib.Path) -> None:
    spec = json.loads(job_path.read_text())
    name = job_path.stem
    out_dir = ROOT / "outputs" / name
    out_dir.mkdir(parents=True, exist_ok=True)

    files = []
    for img in spec["input_images"]:
        p = ROOT / img
        files.append(("image[]", (p.name, p.read_bytes(), "image/png")))

    data = {
        "model": spec.get("model", "gpt-image-1"),
        "prompt": spec["prompt"],
        "size": spec.get("size", "1536x1024"),
        "quality": spec.get("quality", "high"),
        "n": str(spec.get("n", 2)),
        "input_fidelity": spec.get("input_fidelity", "high"),
    }

    print(f"[{name}] requesting {data['n']} variant(s) at {data['size']} ...")
    r = requests.post(
        ENDPOINT,
        headers={"Authorization": f"Bearer {API_KEY}"},
        data=data,
        files=files,
        timeout=600,
    )
    if r.status_code != 200:
        print(f"[{name}] API error {r.status_code}: {r.text[:500]}")
        sys.exit(1)

    for i, item in enumerate(r.json()["data"], 1):
        out = out_dir / f"{name}_v{i}.png"
        out.write_bytes(base64.b64decode(item["b64_json"]))
        print(f"[{name}] wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    targets = sys.argv[1:] or [p.stem for p in (ROOT / "jobs").glob("*.json")]
    for t in targets:
        run_job(ROOT / "jobs" / f"{t}.json")
    print("done")
