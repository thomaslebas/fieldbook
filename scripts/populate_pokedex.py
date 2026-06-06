#!/usr/bin/env python3
"""Populate pokedex_log.csv with all Pokémon and their forms from PokeAPI."""

import csv
import sys
import time
import urllib.request
import json
from pathlib import Path

POKEAPI_BASE = "https://pokeapi.co/api/v2"
OUTPUT_PATH = Path(__file__).parent.parent / "user_data" / "pokedex_log.csv"


def fetch_json(url: str, retries: int = 3) -> dict:
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "fieldbook-pokedex/1.0 (github.com/user/fieldbook)"},
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read())
        except Exception as exc:
            if attempt < retries - 1:
                time.sleep(1 + attempt)
            else:
                raise RuntimeError(f"Failed to fetch {url}: {exc}") from exc


def main() -> None:
    print("Fetching full Pokémon list…")
    listing = fetch_json(f"{POKEAPI_BASE}/pokemon?limit=10000")
    entries = listing["results"]
    print(f"  {len(entries)} Pokémon found")

    rows: list[dict] = []

    for i, entry in enumerate(entries, start=1):
        if i % 100 == 0 or i == len(entries):
            print(f"  [{i}/{len(entries)}] {entry['name']}", flush=True)

        details = fetch_json(entry["url"])
        pokedex_id: int = details["id"]
        forms: list[dict] = details.get("forms", [])

        # Base form row uses the Pokémon's own name
        rows.append({
            "pokedex_id": pokedex_id,
            "pokemon_id": details["name"],
            "caught": "NO",
            "shiny_caught": "NO",
        })

        # Additional forms (index 1+) use each form's name field
        for form in forms[1:]:
            rows.append({
                "pokedex_id": pokedex_id,
                "pokemon_id": form["name"],
                "caught": "NO",
                "shiny_caught": "NO",
            })

        # Be polite to the public API
        time.sleep(0.05)

    rows.sort(key=lambda r: r["pokedex_id"])

    print(f"\nWriting {len(rows)} rows to {OUTPUT_PATH}")
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["pokedex_id", "pokemon_id", "caught", "shiny_caught"])
        writer.writeheader()
        writer.writerows(rows)

    print("Done.")


if __name__ == "__main__":
    main()
