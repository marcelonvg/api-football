# src/collectors.py
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple

from .api_client import ApiFootballClient
from .io_utils import save_json

# Regiões alvo para ligas
ALLOWED_REGIONS: Set[str] = {"Europe", "South America", "World"}


def collect_countries(client: ApiFootballClient, outdir: Path) -> Tuple[int, List[Path]]:
    logging.info("Coletando countries...")
    data = client.get("/countries")
    out_path = outdir / "countries.json"
    save_json(out_path, data)
    total = int(data.get("results") or 0)
    logging.info(f"Coletando countries... ok, {total} registros")
    return total, [out_path]


def collect_seasons(client: ApiFootballClient, outdir: Path) -> Tuple[int, List[Path]]:
    logging.info("Coletando seasons...")
    data = client.get("/leagues/seasons")
    out_path = outdir / "seasons.json"
    save_json(out_path, data)
    total = len(data.get("response") or [])
    logging.info(f"Coletando seasons... ok, {total} registros")
    return total, [out_path]


def collect_leagues(client: ApiFootballClient, year: int, outdir: Path) -> Tuple[int, List[Path], List[int]]:
    logging.info(f"Coletando leagues (season={year})...")
    data = client.get("/leagues", params={"season": year})
    out_path = outdir / "leagues.json"
    save_json(out_path, data)

    league_ids: List[int] = []
    for item in data.get("response") or []:
        country_name = ((item.get("country") or {}).get("name") or "").strip()
        if country_name in ALLOWED_REGIONS:
            league = item.get("league") or {}
            lid = league.get("id")
            if lid:
                league_ids.append(int(lid))

    logging.info(f"Coletando leagues... ok, {len(league_ids)} ligas mantidas (regiões alvo)")
    return len(league_ids), [out_path], sorted(set(league_ids))


def collect_teams(
    client: ApiFootballClient, year: int, league_ids: List[int], outdir: Path, limit: int = 5
) -> Tuple[int, List[Path], List[int]]:
    logging.info(f"Coletando até {limit} teams para {len(league_ids)} ligas (season={year})...")
    saved_files: List[Path] = []
    venue_ids: List[int] = []
    total = 0

    for lid in league_ids:
        if total >= limit:
            break
        data = client.get("/teams", params={"league": lid, "season": year})
        out_path = outdir / f"teams_league-{lid}.json"
        save_json(out_path, data)
        saved_files.append(out_path)
        total += int(data.get("results") or 0)

        for item in data.get("response") or []:
            if len(venue_ids) >= limit:  # também limitar venues coletados
                break
            venue = item.get("venue") or {}
            vid = venue.get("id")
            if vid:
                venue_ids.append(int(vid))

    logging.info(
        f"Coletando teams... ok, {total} registros (limitado a {limit}); venues únicos: {len(set(venue_ids))}"
    )
    return total, saved_files, sorted(set(venue_ids))



def collect_venues(
    client: ApiFootballClient, venue_ids: List[int], outdir: Path, limit: int = 5
) -> Tuple[int, List[Path]]:
    logging.info(f"Coletando até {limit} venues (dos times coletados)...")
    saved_files: List[Path] = []
    total = 0

    for idx, vid in enumerate(venue_ids):
        if idx >= limit:
            break
        data = client.get("/venues", params={"id": vid})
        out_path = outdir / f"venues_id-{vid}.json"
        save_json(out_path, data)
        saved_files.append(out_path)
        total += int(data.get("results") or 0)

    logging.info(f"Coletando venues... ok, {total} registros (limitado a {limit})")
    return total, saved_files

