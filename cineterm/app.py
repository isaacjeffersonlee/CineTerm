import json
import pandas as pd
from rich.console import Console  # For pretty printing
from rich.prompt import IntPrompt, Prompt, Confirm
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.progress import Progress
import subprocess
import time
import requests
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import vlc
import os
import sys
lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../cineterm"))
root_path = os.path.dirname(lib_path)
logfile_path = root_path + "/logfile.log"
sys.path.append(lib_path)
cache_path = f"{lib_path}/cache/yts_movies_df.pkl"

import yts
import qbittorrent as qb
import selector
import title


# Todo List
# TODO: Refactor
# - More separation of concerns
# - Docstrings
# - Cleaner dir structure
# TODO: Add fuzzy searching
# TODO: Add recommendation system
# TODO: Add option to delete torrent when mpv is closed
# TODO: Add more error checking
# TODO: Upload to git
# - Nice README.md 
# - .gitignore
# TODO: Add install.sh

# Rich setup for pretty printing
status_spinner = "dots"
console = Console()

play_sounds = True
try:
    start_sound = vlc.MediaPlayer(f"{root_path}/media/start_sound.mp3")
    error_sound = vlc.MediaPlayer(f"{root_path}/media/error_sound.mp3")
    torrent_added_sound = vlc.MediaPlayer(f"{root_path}/media/yeah_boy.mp3")
    prof_sound = vlc.MediaPlayer(f"{root_path}/media/watch_your_profanity.mp3")
except:
    play_sounds = False

with open(f"{root_path}/credentials.json", 'r') as f:
    credentials = json.load(f)

# qbittorrent details
qb_username = credentials["qb_username"]
qb_password = credentials["qb_password"]

# For text to speech
speech_language = "en-uk-wmids"




medium_torrent_str = """
████████╗ ██████╗ ██████╗ ██████╗ ███████╗███╗   ██╗████████╗
╚══██╔══╝██╔═══██╗██╔══██╗██╔══██╗██╔════╝████╗  ██║╚══██╔══╝
   ██║   ██║   ██║██████╔╝██████╔╝█████╗  ██╔██╗ ██║   ██║   
   ██║   ██║   ██║██╔══██╗██╔══██╗██╔══╝  ██║╚██╗██║   ██║   
   ██║   ╚██████╔╝██║  ██║██║  ██║███████╗██║ ╚████║   ██║   
   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝   
"""

large_torrent_str = """
    ███      ▄██████▄     ▄████████    ▄████████    ▄████████ ███▄▄▄▄       ███        ▄████████ 
▀█████████▄ ███    ███   ███    ███   ███    ███   ███    ███ ███▀▀▀██▄ ▀█████████▄   ███    ███ 
   ▀███▀▀██ ███    ███   ███    ███   ███    ███   ███    █▀  ███   ███    ▀███▀▀██   ███    █▀  
    ███   ▀ ███    ███  ▄███▄▄▄▄██▀  ▄███▄▄▄▄██▀  ▄███▄▄▄     ███   ███     ███   ▀   ███        
    ███     ███    ███ ▀▀███▀▀▀▀▀   ▀▀███▀▀▀▀▀   ▀▀███▀▀▀     ███   ███     ███     ▀███████████ 
    ███     ███    ███ ▀███████████ ▀███████████   ███    █▄  ███   ███     ███              ███ 
    ███     ███    ███   ███    ███   ███    ███   ███    ███ ███   ███     ███        ▄█    ███ 
   ▄████▀    ▀██████▀    ███    ███   ███    ███   ██████████  ▀█   █▀     ▄████▀    ▄████████▀  
                         ███    ███   ███    ███                                                
"""




def check_connection(timeout: int=1) -> bool:
    """Ping google to check internet connection."""
    try:
        requests.head("http://www.google.com/", timeout=timeout)
        return True
    except requests.ConnectionError:
        if play_sounds: error_sound.play()
        return False


def populate_results_table(search_results: list[dict]) -> Table:
    """Populate a rich table using search_results."""
    results_table = Table(title=None, show_lines=False)
    results_table.add_column("", justify="left", style="cyan")
    results_table.add_column("Title", justify="left", style="white")
    results_table.add_column("Year", justify="left", style="green")
    for idx, result in enumerate(search_results):
        results_table.add_row(str(idx),
                              f"[bold]{result['title']}[/bold]",
                              str(result["year"]))
    return results_table


def connect_expressvpn() -> None:
    """Activate expressvpn connection."""
    try:
        with console.status("Connecting to expressvpn...", spinner=status_spinner):
            subprocess.run(["expressvpn", "connect"],
                           stdout=open("/dev/null", 'w'),
                           stderr=open(logfile_path, 'a'))
        console.print("[green]Success:[/green] connected to expressvpn!")
    except:
        console.print("[red]Warning:[/red] expressvpn failed to connect!")


def main(download_dir: str, check_for_expressvpn: bool,
         buffer_percent: float=0.05) -> None:

    with console.status("Checking internet connection...", spinner=status_spinner):
        connected = check_connection()

    if not connected:
        console.print("[red]Error:[/red] Internet is not connected!")
        if play_sounds: error_sound.play()
        return None

    os.system("clear")

    if check_for_expressvpn: connect_expressvpn()

    if play_sounds:
        try:
            start_sound.play()
        except:
            console.print("[gray]Error playing start sound effect![/gray]")
            error_sound.play()

    yts_movies_df = yts.read_in_movies_df(cache_path)

    title.display_live_title()


    console.print(Markdown("---"))

    os.system("clear")
    r = selector.fzf_request_movie(yts_movies_df, console)

    while True:
        os.system("clear")
        if not r:  # If the user exists the initial fuzzy search.
            break
        status = r["status"]
        if status == "ok":
            console.print(f"[green]Status:[/green] {status}")
            console.print(f"[green]Status Message:[/green] {r['status_message']}")
        else:
            console.print(f"[red]Status:[/red] {status}")
            console.print(f"[red]:[/red] {r['status_message']}")
            console.print(Markdown("---"))
            r = selector.fzf_request_movie(yts_movies_df, console)
            continue

        movie = r["data"]["movie"]
        movie_title = movie["title_long"]

        # results_table = populate_results_table(movie)

        # dynamic_print(small_str="ACTIONS", medium_str=medium_actions_str, large_str=large_actions_str)
        console.print(Markdown(f"## {movie_title}:"))
        print("")
        summary = movie["description_intro"]
        genres = movie["genres"]
        if not summary or summary == ' ':
            summary = "[red]Sorry![/red] No summary available."

        console.print(Align(renderable=Panel(renderable=summary, width=50), align="center"))
        print("")
        console.print(Align(renderable=f"Rating: {movie['rating']}/10.0", align="center"))
        print("")
        console.print(Align(renderable="Genres: " + " | ".join([f"[blue]{genre}[/blue]" for genre in genres]),
                            align="center"))
        print("")
        console.print(Markdown("---"))
        print("")
        # console.print(Align(results_table, align="center"))
        console.print(Align(renderable=" ([red bold]s[/red bold])tream ([red bold]d[/red bold])ownload ([red bold]r[/red bold])e-search ([red bold]S[/red bold])peak ([red bold]t[/red bold])railer ([red bold]q[/red bold])uit", align="center"))
        mode_choice = Prompt.ask(" [yellow]Enter action letter[/yellow]",
                                 show_choices=False,
                                 choices=['d', 'r', 's', 'S', 't', 'q']) 
        if mode_choice == 'q':
            break

        elif mode_choice == 'r':
            console.print(Markdown("---"))
            r = selector.fzf_request_movie(yts_movies_df, console)
            continue

        elif mode_choice == 't':
            console.print("[yellow]Caution:[/yellow] sometimes this will open a random youtube video if the trailer is [red]not found[/red].")
            console.print(f"Opening trailer for {movie_title}...")
            trailer_url = "https://www.youtube.com/watch?v=" + movie["yt_trailer_code"]
            subprocess.run(["mpv", trailer_url])
        
        elif mode_choice == 'S':
            os.system("clear")
            console.print(Markdown("---"))
            console.print(Markdown(f"## Summary for {movie_title}:"))
            print("")
            summary = movie["description_intro"]
            genres = movie["genres"]
            if not summary or summary == ' ':
                console.print("   [red]Sorry![/red] No summary available.")
            else:
                console.print(Align(renderable=Panel(renderable=summary, width=50), align="center"))
                console.print(Align(renderable="Genres: " + " | ".join([f"[blue]{genre}[/blue]" for genre in genres]),
                                    align="center"))
                try:
                    console.print("[red]Ctrl-c[/red] to stop voice.")
                    subprocess.run(["espeak", "-v", speech_language, summary],
                                   stdout=open("/dev/null", 'w'),
                                   stderr=open(logfile_path, 'a'))
                except:
                    pass
    
            print("")
            os.system("clear")
            continue
        
        else:  # Either stream or download
            os.system("clear")
            console.print(f"You have chosen: {movie_title}")
            torrent_title_str = title.get_title_str(small_str="Torrents", medium_str=medium_torrent_str, large_str=large_torrent_str)
            console.print(Panel(Align(renderable=torrent_title_str, align="center")))
            torrents = movie["torrents"]
            for idx, torrent in enumerate(torrents):
                panel_str = ""
                panel_str += f"[green]Seeds:[/green] {torrent['seeds']}\n"
                panel_str += f"[red]Peers:[/red] {torrent['peers']}\n"
                panel_str += f"Torrent Quality: [bold]{torrent['quality']}[/bold]\n"
                panel_str += f"Torrent Size: [blue]{torrent['size']}[/blue]"
                console.print(Align(Panel(renderable=panel_str, title=f"Torrent [[red]{idx}[/red]]", width=30), align="center"))

            console.print(Markdown("---"))
            torrent_idx = IntPrompt.ask(f" [yellow]Choose a torrent number [[red]0-{len(torrents)-1}[/red]][/yellow]",
                                      show_choices=False,
                                      choices=[str(i) for i in range(len(torrents))])

            torrent_hash = torrents[torrent_idx]["hash"]
            torrent_url = torrents[torrent_idx]["url"]

            magnet_link = yts.parse_magnet_link(torrent_hash, torrent_url)

            with console.status(f"Connecting to qbittorrent...", spinner=status_spinner):
                login_cookies = qb.login(logfile_path=logfile_path,
                                         qb_username=qb_username,
                                         qb_password=qb_password)

            with console.status(f"Adding torrent to qbittorrent..."):
                qb.add_torrent(magnet_link=magnet_link,
                               movie_title=movie_title,
                               save_path=download_dir,
                               login_cookies=login_cookies)

            console.print(" [green]Added torrent![/green]")

            if mode_choice == 's':  # Open the torrent in mpv
                delete_after_viewing = Confirm.ask(" [yellow]Delete torrent files after viewing?[/yellow]")
                if play_sounds:
                    try:
                        torrent_added_sound.play()
                    except:
                        console.print("[gray]Error playing sound effect.[/gray]")
                        error_sound.play()
                # console.print(f"Total torrent bytes: {torrent_size_bytes}")
                download_info = qb.get_torrent_progress(torrent_hash=torrent_hash, login_cookies=login_cookies)

                with Progress() as progress:
                    buffer_task = progress.add_task(description="[yellow] Waiting to begin download...[/yellow]", total=None)

                    while not download_info["size"]:  # Wait until torrent has started downloading
                        time.sleep(0.5)
                        download_info = qb.get_torrent_progress(torrent_hash=torrent_hash, login_cookies=login_cookies)
                    
                    # Update total size once torrent starts downloading
                    progress.update(task_id=buffer_task,
                                    description=f" [green]Buffering to {buffer_percent*100}% of file...[/green]",
                                    completed=download_info["downloaded"],
                                    total=buffer_percent*download_info["size"])

                    # We only wait for 10% completion before opening the file.
                    while download_info["availability"] != -1 and download_info["downloaded"] / download_info["size"] < buffer_percent:
                        download_info = qb.get_torrent_progress(torrent_hash=torrent_hash, login_cookies=login_cookies)
                        progress.update(buffer_task, completed=download_info["downloaded"])
                        time.sleep(0.5)

                all_items_in_download_dir = os.listdir(download_dir)
                # Fuzzy match the file name since the torrent files often have unexpected names.
                best_match = process.extractOne(movie_title, all_items_in_download_dir, scorer=fuzz.token_sort_ratio)[0]
                torrent_dir = download_dir + best_match + '/'
                for file in os.listdir(torrent_dir):
                    ext = file.split('.')[-1]
                    if ext == 'mp4' or ext == 'mkv':
                        console.print(f" [green]Opening:[/green][white]{torrent_dir + file}[/white] in mpv.")
                        subprocess.run(["mpv", torrent_dir + file])
                        break


                if not delete_after_viewing:  # Wait for the torrent to finish downloading
                    with Progress() as progress:
                        buffer_task = progress.add_task(description="Checking on torrent...", total=None)

                        while not download_info["size"]:  # Wait until torrent has started downloading
                            time.sleep(0.5)
                            download_info = qb.get_torrent_progress(torrent_hash=torrent_hash, login_cookies=login_cookies)
                        
                        # Update total size once torrent starts downloading
                        progress.update(task_id=buffer_task,
                                        description=f" [green]Downloading to 100%...[/green]",
                                        completed=download_info["downloaded"],
                                        total=download_info["size"])

                        # We only wait for 10% completion before opening the file.
                        while download_info["availability"] != -1:  # While we are not seeding
                            download_info = qb.get_torrent_progress(torrent_hash=torrent_hash, login_cookies=login_cookies)
                            progress.update(buffer_task, completed=download_info["downloaded"])
                            time.sleep(0.5)


                with console.status("[cyan bold]qbittorrent:[/cyan bold] Removing torrent..."):
                    qb.remove_torrent(torrent_hash=torrent_hash, delete_files=delete_after_viewing, login_cookies=login_cookies)

                console.print("[green]Seeding[/green] / [red]Leeching[/red] stopped!")
                console.print(f"Files{' ' if delete_after_viewing else ' [green]not[/green] '}deleted!")

            print("")
            console.print("[red]❤[/red] [cyan]Goodbye![/cyan] [red]❤[/red]")
            print("")
            break





if __name__ == "__main__":
    main(download_dir="/home/isaac/Videos/Films/",
         check_for_expressvpn=True,
         buffer_percent=0.05)
