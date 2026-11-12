#!/usr/bin/env python3
"""Export maintained skill templates into a staging directory, without installing."""
import argparse
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True, help="Task staging directory")
    a = p.parse_args()
    source = Path(__file__).resolve().parents[1] / "skill-distribution"
    output = a.output.resolve()
    if output == (Path.home() / ".openclaw/skills").resolve():
        p.error("Export to task staging, then use the shared skill publisher.")
    for name in ["word-report-builder", "speech-narration-builder"]:
        for src, rel in [(source / (name + ".md"), "SKILL.md"),
                         (source / (name + ".py"), "scripts/build.py")]:
            target = output / name / rel
            data = src.read_bytes()
            if target.exists() and target.read_bytes() != data:
                raise ValueError("Preserve changed staged file: " + str(target))
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        print(output / name)


if __name__ == "__main__":
    main()
