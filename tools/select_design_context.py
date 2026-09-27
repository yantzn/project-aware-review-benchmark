from __future__ import annotations

import argparse
import json
from pathlib import Path


def select_context(payload: dict[str, object], keywords: list[str]) -> dict[str, object]:
    lowered = [keyword.lower() for keyword in keywords]
    selected: list[dict[str, object]] = []

    for sheet in payload.get("sheets", []):
        if not isinstance(sheet, dict):
            continue
        matches = []
        for cell in sheet.get("cells", []):
            text = str(cell.get("value", "")).lower()
            if any(keyword in text for keyword in lowered):
                matches.append(cell)
        if matches:
            selected.append(
                {
                    "source_file": payload.get("source_file"),
                    "sheet": sheet.get("sheet"),
                    "matches": matches,
                }
            )

    return {"keywords": keywords, "selected": selected}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("context_json", type=Path)
    parser.add_argument("keywords", nargs="+")
    args = parser.parse_args()

    payload = json.loads(args.context_json.read_text(encoding="utf-8"))
    print(json.dumps(select_context(payload, args.keywords), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
