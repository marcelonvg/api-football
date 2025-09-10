import os
import logging
from pathlib import Path
from dotenv import load_dotenv

from .api_client import ApiFootballClient
from .collectors import (
    collect_countries,
    collect_seasons,
    collect_leagues,
    collect_teams,
    collect_venues,
)
from .io_utils import ensure_dir


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def main():
    load_dotenv()
    setup_logging()

    api_key = os.getenv("API_FOOTBALL_KEY")
    base_url = os.getenv("BASE_URL", "https://v3.football.api-sports.io")
    year = int(os.getenv("SEED_YEAR", "2025"))

    if not api_key:
        raise RuntimeError("API_FOOTBALL_KEY não encontrado nas variáveis de ambiente (.env)")

    # Saída: ./output/api_football/seed/year=YYYY/
    outdir = Path(f"./output/api_football/seed/year={year}")
    ensure_dir(outdir)

    client = ApiFootballClient(api_key=api_key, base_url=base_url)

    # 1) Countries
    collect_countries(client, outdir)

    # 2) Seasons
    collect_seasons(client, outdir)

    # 3) Leagues (filtradas por Europa / América do Sul / Intercontinentais)
    _, _, league_ids = collect_leagues(client, year, outdir)

    # 4) Teams
    _, _, venue_ids = collect_teams(client, year, league_ids, outdir, limit=5)

    # 5) Venues
    collect_venues(client, venue_ids, outdir, limit=5)

    logging.info("Pipeline concluído com sucesso.")

    try:
        os.startfile(outdir)
    except AttributeError:

        logging.info(f"Pasta final: {outdir}")


if __name__ == "__main__":
    main()
