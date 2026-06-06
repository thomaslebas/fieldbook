#!/usr/bin/env python3
"""Update caught column in pokedex_log.csv from the Pokémon GO Gameplay.txt export."""

import csv
import re
from pathlib import Path

GAMEPLAY_PATH = Path(__file__).parent.parent / "user_data" / \
    "251229_PokemonGo_Tulb_110699767985815168807_files" / "Gameplay.txt"
CSV_PATH = Path(__file__).parent.parent / "user_data" / "pokedex_log.csv"

# Manual slug corrections for names that don't convert cleanly
NAME_OVERRIDES = {
    "mr. mime":    "mr-mime",
    "mr mime":     "mr-mime",
    "mime jr.":    "mime-jr",
    "mime jr":     "mime-jr",
    "farfetch'd":  "farfetchd",
    "ho-oh":       "ho-oh",
    "porygon2":    "porygon2",
    "porygon-z":   "porygon-z",
    "nidoran♀":    "nidoran-f",
    "nidoran♂":    "nidoran-m",
    "nidoran (f)": "nidoran-f",
    "nidoran (m)": "nidoran-m",
    "flabébé":     "flabebe",
    "type: null":  "type-null",
}


def name_to_slug(raw: str) -> str:
    """Convert a Pokémon GO display name to a PokeAPI pokemon_id slug."""
    # Strip nickname in parentheses  e.g. "Groudon (Groudon)" → "Groudon"
    name = re.sub(r"\s*\(.*\)$", "", raw).strip()
    lower = name.lower()

    if lower in NAME_OVERRIDES:
        return NAME_OVERRIDES[lower]

    # Replace spaces and remaining dots with hyphens, collapse multiple hyphens
    slug = re.sub(r"[.\s]+", "-", lower)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


def parse_v_format(token: str) -> str:
    """V0413_POKEMON_WORMADAM → 'wormadam' (hyphen-joined, lowercase)."""
    # Remove the V{num}_POKEMON_ prefix
    name_part = re.sub(r"^V\d+_POKEMON_", "", token)
    return name_part.lower().replace("_", "-")


def extract_collection(path: Path) -> list[str]:
    """Return a list of raw Pokémon name tokens from the collection section."""
    text = path.read_text(encoding="utf-8")
    # Grab the block between the two markers
    match = re.search(
        r"Pokemon in your collection:\n(.*?)\nYou have hatched",
        text,
        re.DOTALL,
    )
    if not match:
        raise ValueError("Could not find collection section in Gameplay.txt")

    tokens = []
    for line in match.group(1).splitlines():
        raw = line.strip()
        if not raw:
            continue
        # Strip any trailing nickname in parentheses for V-format too
        raw = re.sub(r"\s*\(.*\)$", "", raw).strip()
        tokens.append(raw)
    return tokens


def main() -> None:
    tokens = extract_collection(GAMEPLAY_PATH)
    print(f"Parsed {len(tokens)} collection entries")

    # Build the set of slugs the player has
    caught_slugs: set[str] = set()
    for token in tokens:
        if re.match(r"^V\d+_POKEMON_", token):
            slug = parse_v_format(token)
        else:
            slug = name_to_slug(token)
        caught_slugs.add(slug)

    print(f"Unique slugs in collection: {len(caught_slugs)}")

    # Read CSV, update caught, write back
    rows = []
    updated = 0
    unmatched_slugs: set[str] = set(caught_slugs)

    with CSV_PATH.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            pid = row["pokemon_id"]
            if pid in caught_slugs:
                row["caught"] = "YES"
                updated += 1
                unmatched_slugs.discard(pid)
            rows.append(row)

    with CSV_PATH.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["pokedex_id", "pokemon_id", "caught", "shiny_caught"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Updated {updated} rows to caught=YES")

    if unmatched_slugs:
        print(f"\n{len(unmatched_slugs)} collection slug(s) had no CSV match:")
        for s in sorted(unmatched_slugs):
            print(f"  {s}")


if __name__ == "__main__":
    main()
