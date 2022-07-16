import requests
import aiohttp
import asyncio
import json
import os
import sys
lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../cineterm"))
root_path = os.path.dirname(lib_path)
logfile_path = root_path + "/logfile.log"
sys.path.append(lib_path)
import pandas as pd
from rich.console import Console  # For pretty printing
from rich.prompt import Confirm
import time

console = Console()

base_url = "https://yts.mx/api/v2/"


def yts_request(endpoint: str, params: dict) -> dict:
    r = requests.get(url=base_url + endpoint, params=params)
    assert r.status_code == 200, f"Error: status code {r.status_code}"
    return r.json()


def parse_magnet_link(torrent_hash: str, torrent_url: str) -> str:
    trackers = [
        "udp://open.demonii.com:1337/announce",
        "udp://tracker.openbittorrent.com:80",
        "udp://tracker.coppersurfer.tk:6969",
        "udp://glotorrents.pw:6969/announce",
        "udp://tracker.opentrackr.org:1337/announce",
        "udp://torrent.gresille.org:80/announce",
        "udp://p4p.arenabg.com:1337",
        "udp://tracker.leechers-paradise.org:6969"
    ]
    magnet_link = f"magnet:?xt=urn:btih:{torrent_hash}&dn={torrent_url}"
    for tracker in trackers:
        magnet_link += f"&tr={tracker}"

    return magnet_link



async def get_movies_py_page(page_num, limit, session):
    r = await session.get(url=base_url+"list_movies.json",
                                     params={"limit": limit,
                                             "query_term": '',
                                             "page": page_num})
    r_json = await r.json()

    return r_json


async def get_all_movies(limit: int=20) -> list[dict]:
    """Get all movies in the yts database."""
    tasks = []
    page_num = 1  # Index starts from 1
    # Use a normal synchronous request to get the total movie count
    r = requests.get(url=base_url+"list_movies.json",
                                     params={"limit": limit,
                                             "query_term": '',
                                             "page": page_num})
    movie_count = r.json()["data"]["movie_count"]

    async with aiohttp.ClientSession() as session:
        results_count = 0
        while results_count < movie_count:
            tasks.append(get_movies_py_page(page_num, limit, session))
            results_count += limit
            page_num += 1
            console.print(f"Firing request => {results_count} / {movie_count}")
        
        with console.status("Gathering results, this may take a while..."):
            all_movies = await asyncio.gather(*tasks, return_exceptions=True)

    return all_movies


def update_database(cache_path: str) -> None:
    console.rule(title="Update Movie Database")
    console.print("[yellow bold]Note:[/yellow bold] this could take quite a while depending on connection speed!")
    run = Confirm.ask("[yellow]Are you sure you want to continue?[/yellow]")
    if run:
        start_time = time.time()
        all_pages = asyncio.run(get_all_movies(50))
        end_time = time.time()
        console.print("")
        console.rule(title=f"[green]Finished in:[/green] {end_time-start_time}")
        all_movies = []
        with console.status("Unpacking results..."):
            for r in all_pages:
                all_movies += r["data"]["movies"]

        console.print(f"Found {len(all_movies)} movies!")
        all_movies_df = pd.DataFrame.from_dict(data=all_movies)

        if os.path.exists(cache_path):
            old_df = pd.read_pickle(cache_path)
            previous_movie_count = old_df.shape[0]
            new_movie_count = all_movies_df.shape[0]
            console.print(f"[bold]{new_movie_count-previous_movie_count}[/bold] new movies found!")

        console.print(f"Caching results to {cache_path}")
        all_movies_df.to_pickle(f"{lib_path}/yts_movies_df.pkl")

        with console.status("Generating summary map..."):
            title_to_info_map = {all_movies_df["title"].iloc[i] : f"\033[96m Summary: {all_movies_df['title_long'].iloc[i]}\033[00m\n" + '-'*len(f"Summary: {all_movies_df['title_long'].iloc[i]}") + '\n' + f"[\033[92mReleased\033[00m]: {all_movies_df['year'].iloc[i]}\n" + f"[\033[92mRating\033[00m]: {all_movies_df['rating'].iloc[i]}/10.0" + "\n\n" + str(all_movies_df["summary"].iloc[i]) + "\n\n" + "[\033[91mGenres\033[00m]: " + str(all_movies_df["genres"].iloc[i]) for i in range(all_movies_df.shape[0])}
            with open(f"{lib_path}/summary_mapper.py", 'w') as f:
                f.write("import numpy as np\nnan = np.nan\n")
                f.write("summary_map = " + str(title_to_info_map))

        console.print("[green bold]Success! Summary map generated[/]")


if __name__ == "__main__":
    # TODO: Extract this all to a function: "update_database"
    cache_path = f"{lib_path}/yts_movies_df.pkl"
    update_database(cache_path)

