import time
from rich.prompt import Confirm
from rich.console import Console  # For pretty printing
from rich.progress import Progress
import pandas as pd
import requests
import aiohttp
import asyncio
import pickle
import os
from cineterm.config import LIB_PATH, CACHE_PATH

console = Console()

BASE_URL = "https://yts.mx/api/v2/"


def yts_request(endpoint: str, params: dict) -> dict:
    r = requests.get(url=BASE_URL + endpoint, params=params)
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
        "udp://tracker.leechers-paradise.org:6969",
    ]
    magnet_link = f"magnet:?xt=urn:btih:{torrent_hash}&dn={torrent_url}"
    for tracker in trackers:
        magnet_link += f"&tr={tracker}"

    return magnet_link


async def get_movies_py_page(page_num: int, limit: int, session: aiohttp.ClientSession):
    r = await session.get(
        url=BASE_URL + "list_movies.json",
        params={"limit": limit, "query_term": "", "page": page_num},
    )
    r_json = await r.json()

    return r_json


async def get_all_movies(results_per_page: int = 20) -> list[dict]:
    """Get all movies in the yts database."""
    tasks = []
    page_num = 1  # Index starts from 1
    # Use a normal synchronous request to get the total movie count
    r = requests.get(
        url=BASE_URL + "list_movies.json",
        params={"limit": results_per_page, "query_term": "", "page": page_num},
    )
    movie_count = r.json()["data"]["movie_count"]

    async with aiohttp.ClientSession() as session:
        results_count = 0
        # total_pages = movie_count // results_per_page
        with Progress() as progress:
            update_task = progress.add_task(
                description="[yellow] Sending requests to YTS...[/yellow]", total=None
            )
            while results_count < movie_count:
                # console.print(f"Firing request => {page_num} / {total_pages}")
                # console.print(f"Movies Retrieved => {results_count} / {movie_count}")
                tasks.append(get_movies_py_page(page_num, results_per_page, session))
                results_count += results_per_page
                page_num += 1
                # Update total size once torrent starts downloading
                progress.update(
                    task_id=update_task,
                    description=" [green]Firing async requests...[/green]",
                    completed=results_count,
                    total=movie_count,
                )

        with console.status("Waiting for request responses..."):
            all_movies = await asyncio.gather(*tasks, return_exceptions=True)

    return all_movies


def update_database(cache_path: str) -> None:
    console.rule(title="Update Movie Database")
    console.print(
        "[yellow bold]Note:[/yellow bold] this could take quite a while depending on connection speed!"
    )
    run = Confirm.ask("[yellow]Are you sure you want to continue?[/yellow]")
    if run:
        start_time = time.perf_counter()
        all_pages = asyncio.run(get_all_movies(results_per_page=50))
        end_time = time.perf_counter()
        console.print("")
        console.rule(
            title=f"[green]Finished requesting database in:[/green] {round(end_time-start_time, 2)}s"
        )
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
            console.print(
                f"[bold]{new_movie_count-previous_movie_count}[/bold] new movies found!"
            )

        console.print(f"Caching results to {cache_path}")
        all_movies_df.to_pickle(cache_path)

        with console.status("Generating summary map..."):
            title_to_info_map = {
                all_movies_df["title"].iloc[i]: "\033[96m Summary:"
                + f" {all_movies_df['title_long'].iloc[i]}\033[00m\n"
                + "-" * len(f"Summary: {all_movies_df['title_long'].iloc[i]}")
                + "\n"
                + "[\033[92mReleased\033[00m]:"
                + f" {all_movies_df['year'].iloc[i]}\n"
                + "[\033[92mRating\033[00m]:"
                + f" {all_movies_df['rating'].iloc[i]}/10.0"
                + "\n\n"
                + f"{all_movies_df['summary'].iloc[i]}"
                + "\n\n"
                + "[\033[91mGenres\033[00m]: "
                + str(all_movies_df["genres"].iloc[i])
                for i in range(all_movies_df.shape[0])
            }
            with open(f"{LIB_PATH}/summary_map.pkl", "wb") as f:
                pickle.dump(title_to_info_map, f, protocol=pickle.HIGHEST_PROTOCOL)
            # with open(f"", 'w') as f:
            #     f.write("import numpy as np\nnan = np.nan\n")
            #     f.write("summary_map = " + str(title_to_info_map))

        console.print("[green bold]Success! Summary map generated[/]")


def read_in_movies_df(cache_path: str) -> pd.DataFrame:
    with console.status("Reading in movie database..."):
        try:
            yts_movies_df = pd.read_pickle(cache_path)
            return yts_movies_df
        except FileNotFoundError:
            print("Cache file not found!")

    update_database(cache_path)
    yts_movies_df = pd.read_pickle(cache_path)
    return yts_movies_df


if __name__ == "__main__":
    update_database(CACHE_PATH)
