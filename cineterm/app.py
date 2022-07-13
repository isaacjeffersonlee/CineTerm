import os
import sys
lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../cineterm"))
root_path = os.path.dirname(lib_path)
logfile_path = root_path + "/logfile.log"
print(root_path)
sys.path.append(lib_path)

import yts
import qbittorrent as qb
import json
from rich.console import Console  # For pretty printing
from rich.prompt import IntPrompt, Prompt
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

play_sounds = True
try:
    start_sound = vlc.MediaPlayer(f"{root_path}/media/start_sound.mp3")
    error_sound = vlc.MediaPlayer(f"{root_path}/media/error_sound.mp3")
    torrent_added_sound = vlc.MediaPlayer(f"{root_path}/media/yeah_boy.mp3")
except:
    play_sounds = False

# Todo List
# Add sound effects
# TODO: Add option to delete torrent when mpv is closed
# TODO: Add more error checking
# TODO: Refactor
# - More separation of concerns
# - Docstrings
# - Cleaner dir structure
# TODO: Upload to git
# - Nice README.md 
# - .gitignore
# TODO: Add install.sh
#



console = Console()

with open(f"{root_path}/credentials.json", 'r') as f:
    credentials = json.load(f)

# qbittorrent details
qb_username = credentials["qb_username"]
qb_password = credentials["qb_password"]

# For text to speech
speech_language = "en-uk-wmids"

medium_title_str = """
 ██████╗██╗███╗   ██╗███████╗████████╗███████╗██████╗ ███╗   ███╗
██╔════╝██║████╗  ██║██╔════╝╚══██╔══╝██╔════╝██╔══██╗████╗ ████║
██║     ██║██╔██╗ ██║█████╗     ██║   █████╗  ██████╔╝██╔████╔██║
██║     ██║██║╚██╗██║██╔══╝     ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║
╚██████╗██║██║ ╚████║███████╗   ██║   ███████╗██║  ██║██║ ╚═╝ ██║
 ╚═════╝╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝
"""

large_title_str = """
 ▄████████  ▄█  ███▄▄▄▄      ▄████████     ███        ▄████████    ▄████████   ▄▄▄▄███▄▄▄▄   
███    ███ ███  ███▀▀▀██▄   ███    ███ ▀█████████▄   ███    ███   ███    ███ ▄██▀▀▀███▀▀▀██▄ 
███    █▀  ███▌ ███   ███   ███    █▀     ▀███▀▀██   ███    █▀    ███    ███ ███   ███   ███ 
███        ███▌ ███   ███  ▄███▄▄▄         ███   ▀  ▄███▄▄▄      ▄███▄▄▄▄██▀ ███   ███   ███ 
███        ███▌ ███   ███ ▀▀███▀▀▀         ███     ▀▀███▀▀▀     ▀▀███▀▀▀▀▀   ███   ███   ███ 
███    █▄  ███  ███   ███   ███    █▄      ███       ███    █▄  ▀███████████ ███   ███   ███ 
███    ███ ███  ███   ███   ███    ███     ███       ███    ███   ███    ███ ███   ███   ███ 
████████▀  █▀    ▀█   █▀    ██████████    ▄████▀     ██████████   ███    ███  ▀█   ███   █▀  
                                                                  ███    ███         
"""


medium_results_str = """
██████╗ ███████╗███████╗██╗   ██╗██╗  ████████╗███████╗
██╔══██╗██╔════╝██╔════╝██║   ██║██║  ╚══██╔══╝██╔════╝
██████╔╝█████╗  ███████╗██║   ██║██║     ██║   ███████╗
██╔══██╗██╔══╝  ╚════██║██║   ██║██║     ██║   ╚════██║
██║  ██║███████╗███████║╚██████╔╝███████╗██║   ███████║
╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚══════╝╚═╝   ╚══════╝
"""


large_results_str = """
   ▄████████    ▄████████    ▄████████ ███    █▄   ▄█           ███        ▄████████ 
  ███    ███   ███    ███   ███    ███ ███    ███ ███       ▀█████████▄   ███    ███ 
  ███    ███   ███    █▀    ███    █▀  ███    ███ ███          ▀███▀▀██   ███    █▀  
 ▄███▄▄▄▄██▀  ▄███▄▄▄       ███        ███    ███ ███           ███   ▀   ███        
▀▀███▀▀▀▀▀   ▀▀███▀▀▀     ▀███████████ ███    ███ ███           ███     ▀███████████ 
▀███████████   ███    █▄           ███ ███    ███ ███           ███              ███ 
  ███    ███   ███    ███    ▄█    ███ ███    ███ ███▌    ▄     ███        ▄█    ███ 
  ███    ███   ██████████  ▄████████▀  ████████▀  █████▄▄██    ▄████▀    ▄████████▀  
  ███    ███  
"""

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

def dynamic_print(small_str: str, medium_str: str, large_str: str) -> None:
    term_width = os.get_terminal_size().columns
    if term_width > 100:
        console.print(Panel(Align(renderable=large_str, align="center")))
    elif 60 < term_width and term_width < 100:
        console.print(Panel(Align(renderable=medium_str, align="center")))
    else:
        console.print(Markdown(f"# {small_str}"))


def check_connection(timeout: int=1) -> bool:
    try:
        requests.head("http://www.google.com/", timeout=timeout)
        return True
    except requests.ConnectionError:
        if play_sounds: error_sound.play()
        return False


def populate_results_table(search_results: list[dict]) -> Table:
    results_table = Table(title=None, show_lines=False)
    results_table.add_column("", justify="left", style="cyan")
    results_table.add_column("Title", justify="left", style="white")
    results_table.add_column("Year", justify="left", style="green")
    for idx, result in enumerate(search_results):
        results_table.add_row(str(idx),
                              f"[bold]{result['title']}[/bold]",
                              str(result["year"]))
    return results_table


def main(download_dir: str, check_for_expressvpn: bool, buffer_percent: float=0.05) -> None:
    if not check_connection():
        console.print("[red]Error:[/red] Internet is not connected!")
        if play_sounds: error_sound.play()
        return None

    os.system("clear")

    if check_for_expressvpn:
        try:
            print("Connecting to vpn...")
            subprocess.run(["expressvpn", "connect"],
                           stdout=open("/dev/null", 'w'),
                           stderr=open(logfile_path, 'a'))
            console.print("[green]Success:[/green] connected to expressvpn!")
        except:
            console.print("[red]Warning:[/red] expressvpn failed to connect!")

    dynamic_print(small_str="CineTerm", medium_str=medium_title_str, large_str=large_title_str)

    try:
        if play_sounds: start_sound.play()
    except:
        console.print("[gray]Error playing start sound effect![/gray]")
        if play_sounds: error_sound.play()

    console.print(Markdown("---"))
    search_query = Prompt.ask(" [yellow]Enter movie to search[/yellow]")
    r = yts.yts_request(endpoint="list_movies.json",
                        params={"query_term": search_query})
    while True:
        os.system("clear")
        status = r["status"]
        if status == "ok":
            console.print(f"[green]Status:[/green] {status}")
            console.print(f"[green]Status Message:[/green] {r['status_message']}")
        else:
            console.print(f"[red]Status:[/red] {status}")
            console.print(f"[red]:[/red] {r['status_message']}")
            console.print(Markdown("---"))
            search_query = Prompt.ask(" [yellow]Retry search[/yellow]")
            r = yts.yts_request(endpoint="list_movies.json",
                                         params={"query_term": search_query})
            continue

        try:
            search_results = r["data"]["movies"]
        except KeyError:
            console.print(f"[red]Failed:[/red] Unable to find results for {search_query}")
            if play_sounds: error_sound.play()
            console.print(Markdown("---"))
            search_query = Prompt.ask(" [yellow]Retry search[/yellow]")
            r = yts.yts_request(endpoint="list_movies.json",
                                         params={"query_term": search_query})
            continue

        results_table = populate_results_table(search_results)

        dynamic_print(small_str="Results", medium_str=medium_results_str, large_str=large_results_str)
        console.print(Markdown("---"))
        console.print(Align(results_table, align="center"))
        mode_choice = Prompt.ask(" ([red]s[/red])tream ([red]d[/red])ownload ([red]r[/red])e-search ([red]S[/red])ummaries ([red]t[/red])railers ([red]q[/red])uit",
                                 show_choices=False,
                                 choices=['d', 'r', 's', 'S', 't', 'q']) 
        if mode_choice == 'q':
            break

        elif mode_choice == 'r':
            console.print(Markdown("---"))
            search_query = Prompt.ask(" [yellow]Search again[/yellow]")
            r = yts.yts_request(endpoint="list_movies.json",
                                params={"query_term": search_query})
            continue

        elif mode_choice == 't':
            movie_idx = IntPrompt.ask(f" [yellow]Choose a movie number to watch the trailer for [[red]0-{len(search_results)-1}[/red]][/yellow]",
                                      show_choices=False,
                                      choices=[str(i) for i in range(len(search_results))])

            movie_title = search_results[movie_idx]["title_long"]
            console.print(f"Opening trailer for {movie_title}...")
            console.print("[yellow]Caution:[/yellow] sometimes this will open a random youtube video if the trailer is not found.")
            trailer_url = "https://www.youtube.com/watch?v=" + search_results[movie_idx]["yt_trailer_code"]

            subprocess.run(["mpv", trailer_url])
        
        elif mode_choice == 'S':
            movie_idx = IntPrompt.ask(f" [yellow]Choose a movie number to summarize [[red]0-{len(search_results)-1}[/red]][/yellow]",
                                      show_choices=False,
                                      choices=[str(i) for i in range(len(search_results))])

            os.system("clear")
            console.print(Markdown("---"))
            movie_title = search_results[movie_idx]["title_long"]
            console.print(Markdown(f"## Summary for {movie_title}:"))
            print("")
            summary = search_results[movie_idx]["summary"]
            genres = search_results[movie_idx]["genres"]
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
            return_input = input("Press any key to return to main menu: ")
            continue
        
        else:  # Either stream or download
            movie_idx = IntPrompt.ask(f" [yellow]Choose a movie number [[red]0-{len(search_results)-1}[/red]][/yellow]",
                                      show_choices=False,
                                      choices=[str(i) for i in range(len(search_results))])

            movie_title = search_results[movie_idx]["title_long"]

            os.system("clear")
            console.print(f"You have chosen: {movie_title}")
            dynamic_print(small_str="Torrents", medium_str=medium_torrent_str, large_str=large_torrent_str)
            torrents = search_results[movie_idx]["torrents"]
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

            login_cookies = qb.login(logfile_path=logfile_path,
                                     qb_username=qb_username,
                                     qb_password=qb_password)

            qb.add_torrent(magnet_link=magnet_link,
                           movie_title=movie_title,
                           save_path=download_dir,
                           login_cookies=login_cookies)

            console.print(" [green]Added torrent![/green]")
            # subprocess.run(["espeak", "-v",
            #                 speech_language,
            #                 "You'll be pleased to hear that I've just added the torrent for yoos!"],
            #                stdout=open("/dev/null", 'w'),
            #                stderr=open(logfile_path, 'a'))

            if mode_choice == 's':  # Open the torrent in mpv
                try:
                    if play_sounds: torrent_added_sound.play()
                except:
                    console.print("[gray]Error playing sound effect.[/gray]")
                    if play_sounds: error_sound.play()
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
                    while download_info["downloaded"] / download_info["size"] < buffer_percent:
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
            break





if __name__ == "__main__":
    main(download_dir = "/home/isaac/Videos/Films/", check_for_expressvpn=True, buffer_percent=0.1)
