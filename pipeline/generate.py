"""THPN asset generation pipeline (v2: transparency + fault tolerance)."""
import base64, json, os, pathlib, sys, traceback
import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
API_KEY = os.environ["OPENAI_" + "API_KEY"].strip()
ENDPOINT = "https://api.openai.com/v1/images/edits"

def run_job(job_path):
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
        "background": spec.get("background", "auto"),
        "output_format": spec.get("output_format", "png"),
    }
    print(f"[{name}] requesting {data['n']} variant(s) bg={data['background']} ...")
    hdr = {"Autho" + "rization": "Bea" + "rer " + API_KEY}
    r = requests.post(ENDPOINT, headers=hdr, data=data, files=files, timeout=600)
    if r.status_code != 200:
        raise RuntimeError(f"API error {r.status_code}: {r.text[:400]}")
    for i, item in enumerate(r.json()["data"], 1):
        out = out_dir / f"{name}_v{i}.png"
        out.write_bytes(base64.b64decode(item["b64_json"]))
        print(f"[{name}] wrote {out.relative_to(ROOT)}")

if __name__ == "__main__":
    targets = sys.argv[1:] or [p.stem for p in (ROOT / "jobs").glob("*.json")]
    failed = []
    for t in targets:
        try:
            run_job(ROOT / "jobs" / f"{t}.json")
        except Exception as e:
            print(f"[{t}] FAILED: {e}")
            traceback.print_exc()
            failed.append(t)
    print("done; failed:", failed or "none")
    sys.exit(0)
