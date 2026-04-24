#!/usr/bin/env python3
"""Export outputs from notebook: clean widget state, extract outputs, export HTML.

Usage:
  python3 scripts/export_outputs.py \
      --notebook student_start_pack/ArtBench10_Student_Start_Pack.ipynb \
      --outdir artifacts/raw_outputs

This will write:
 - cleaned notebook next to the original with suffix "-cleaned.ipynb"
 - extracted text files and images into the `outdir` folder
 - exported HTML at the project root as `outputs.html`

After running, you can open `outputs.html` in a browser to view all outputs.
"""

import argparse
import json
import base64
import subprocess
from pathlib import Path
import sys

WIDGET_MIMES = {
    "application/vnd.jupyter.widget-view+json",
    "application/vnd.jupyter.widget-state+json",
}


def clean_notebook(nb: dict) -> dict:
    for cell in nb.get("cells", []):
        new_outputs = []
        for out in cell.get("outputs", []):
            # remove widget metadata if present
            meta = out.get("metadata")
            if isinstance(meta, dict) and "widgets" in meta:
                meta.pop("widgets", None)
            # drop outputs that contain widget mime types
            data = out.get("data")
            if isinstance(data, dict) and any(m in data for m in WIDGET_MIMES):
                # skip this output entirely
                continue
            # sometimes execute_result may have malformed widget metadata; keep common outputs
            new_outputs.append(out)
        cell["outputs"] = new_outputs
    # also clear top-level nb metadata widgets state if present
    nb_meta = nb.get("metadata")
    if isinstance(nb_meta, dict) and "widgets" in nb_meta:
        nb_meta.pop("widgets", None)
    return nb


def extract_outputs(nb: dict, out_root: Path):
    out_root.mkdir(parents=True, exist_ok=True)
    for ci, cell in enumerate(nb.get("cells", []), start=1):
        for oi, out in enumerate(cell.get("outputs", []), start=1):
            tag = f"cell{ci:03d}_out{oi:03d}"
            # stream outputs
            if out.get("output_type") == "stream":
                text = "".join(out.get("text", []))
                if text:
                    (out_root / f"{tag}.txt").write_text(text, encoding="utf-8")
            # data outputs
            data = out.get("data", {}) or {}
            if isinstance(data, dict):
                # text/plain
                if "text/plain" in data:
                    txt = "".join(data["text/plain"] if isinstance(data["text/plain"], list) else [data["text/plain"]])
                    (out_root / f"{tag}_plain.txt").write_text(txt, encoding="utf-8")
                # images
                for img_type in ("image/png", "image/jpeg"):
                    if img_type in data:
                        b64 = data[img_type]
                        if isinstance(b64, list):
                            b64 = "".join(b64)
                        try:
                            img_bytes = base64.b64decode(b64)
                        except Exception as e:
                            print(f"Warning: failed to decode {tag} {img_type}: {e}")
                            continue
                        ext = "png" if "png" in img_type else "jpg"
                        (out_root / f"{tag}.{ext}").write_bytes(img_bytes)


def main():
    p = argparse.ArgumentParser()
    # defaults are relative to the project root (two levels above this script)
    project_root = Path(__file__).parent.parent
    default_nb = project_root / "student_start_pack" / "ArtBench10_Student_Start_Pack.ipynb"
    default_out = project_root / "outputs"

    p.add_argument("--notebook", "-n", default=str(default_nb), help="Path to notebook (.ipynb)")
    p.add_argument("--outdir", "-o", default=str(default_out), help="Output folder for extracted files")
    p.add_argument("--cleaned-name", "-c", default=None, help="Optional cleaned notebook filename")
    args = p.parse_args()

    nb_path = Path(args.notebook)
    if not nb_path.exists():
        print("Notebook not found:", nb_path, file=sys.stderr)
        sys.exit(2)

    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    cleaned = clean_notebook(nb)

    cleaned_name = args.cleaned_name
    if not cleaned_name:
        cleaned_name = nb_path.with_name(nb_path.stem + "-cleaned.ipynb")
    else:
        cleaned_name = Path(cleaned_name)

    cleaned_name.write_text(json.dumps(cleaned, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Wrote cleaned notebook:", cleaned_name)

    out_root = Path(args.outdir)
    # ensure out_root exists and is empty: delete its contents each run
    if out_root.exists():
        for child in list(out_root.iterdir()):
            try:
                if child.is_dir():
                    import shutil

                    shutil.rmtree(child)
                else:
                    child.unlink()
            except Exception as e:
                print(f"Warning: failed to remove {child}: {e}")
    else:
        out_root.mkdir(parents=True, exist_ok=True)

    extract_outputs(cleaned, out_root)
    print("Extracted outputs to:", out_root)
    print("You can now open the extracted files directly.")

    # Export cleaned notebook to HTML (no execute) using the current Python environment
    exported = False
    # Prefer using the nbconvert Python API to avoid subprocess E2BIG errors
    try:
        import nbformat
        from nbconvert import HTMLExporter

        print("Exporting cleaned notebook to HTML using nbconvert API...")
        nb_node = nbformat.read(str(cleaned_name), as_version=4)
        html_exporter = HTMLExporter()
        body, resources = html_exporter.from_notebook_node(nb_node)
        out_html = project_root / "outputs.html"
        out_html.write_text(body, encoding="utf-8")
        print(f"Wrote {out_html}")
        exported = True
    except Exception as e:
        print("Warning: nbconvert API export failed:", e)
        # fallback to subprocess call (best-effort)
        try:
            cmd = [sys.executable, "-m", "nbconvert", "--to", "html", str(cleaned_name), "--output", str(project_root / "outputs.html")]
            print("Falling back to subprocess nbconvert...")
            subprocess.run(cmd, check=True)
            print(f"Wrote {project_root / 'outputs.html'}")
            exported = True
        except Exception as e2:
            print("Fallback nbconvert also failed:", e2)

    if exported:
        # remove the cleaned notebook as requested
        try:
            cleaned_name.unlink()
            print(f"Removed temporary cleaned notebook: {cleaned_name}")
        except Exception as e:
            print(f"Warning: failed to remove cleaned notebook {cleaned_name}: {e}")


if __name__ == "__main__":
    main()
