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
import os
import time
import requests
from fuzzywuzzy import process
from fuzzywuzzy import fuzz

# Todo List
# TODO: Add progress bars
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

with open("../credentials.json", 'r') as f:
    credentials = json.load(f)

# qbittorrent details
qb_username = credentials["qb_username"]
qb_password = credentials["qb_password"]

app_start_str = """
        [red]_____________________________________________
      //:::::::::::::::::::::::::::::::::::::::::::::\\
    //:::_______:::::::::________::::::::::_____:::::::\\
  //:::_/   _-'':::_--'''        '''--_::::\_  ):::::::::\\
 //:::/    /:::::_'                    '-_:::\/:::::|^\\:::\\
//:::/   /~::::::I__                      \:::::::::|  \\:::\\
\\:::\\   (::::::::::''''---___________     '--------'  /::://
 \\:::\\  |::::::::::::::::::::::::::::''''==____      /::://
  \\:::'\\/::::::::::::::::::::::::::::::::::::::\\   /~::://
    \\:::::::::::::::::::::::::::::::::::::::::::)/~::://
      \\::::\\''''''------_____::::::::::::::::::::::://
        \\:::'\\               '''''-----_____:::::://
          \\:::'\\    __----__                )::://
            \\:::'\\/~::::::::~\_         __/~:://
              \\::::::::::::::::''----''':::://
                \\::::::::::::::::::::::::://
                  \\:::\\^''--._.--''^/::://
                    \\::'\\         /':://
                      \\::'\\     /':://
                        \\::'\\_/':://
                          \\::::://
                            \\_//
                              '[/red]
"""


def check_connection(timeout: int=1) -> bool:
    try:
        requests.head("http://www.google.com/", timeout=timeout)
        return True
    except requests.ConnectionError:
        return False


def populate_results_table(search_results: list[dict]) -> Table:
    results_table = Table(title="Search Results", show_lines=False)
    results_table.add_column("", justify="left", style="cyan")
    results_table.add_column("Title", justify="left", style="white")
    results_table.add_column("Year", justify="left", style="green")
    for idx, result in enumerate(search_results):
        results_table.add_row(str(idx),
                              f"[bold]{result['title']}[/bold]",
                              str(result["year"]))
    return results_table


def main(check_for_expressvpn: bool, buffer_percent: float=0.05) -> None:
    if not check_connection():
        console.print("[red]Error:[/red] Internet is not connected!")
        return None

    os.system("clear")

    if check_for_expressvpn:
        try:
            print("Connecting to vpn...")
            subprocess.run(["expressvpn", "connect"],
                           stdout=open("/dev/null", 'w'),
                           stderr=open("../logfile.log", 'a'))
            console.print("[green]Success:[/green] connected to expressvpn!")
        except:
            console.print("[red]Warning:[/red] expressvpn failed to connect!")

    console.print(Panel(Align(renderable=app_start_str, align="center")))
    console.print(Align(Markdown("# Super Streamer"), align="center"))

    search_query = Prompt.ask("Enter movie to search")
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
            search_query = Prompt.ask("Retry search")
            r = yts.yts_request(endpoint="list_movies.json",
                                         params={"query_term": search_query})
            continue

        try:
            search_results = r["data"]["movies"]
        except KeyError:
            console.print(f"[red]Failed:[/red] Unable to find results for {search_query}")
            search_query = Prompt.ask("Retry search")
            r = yts.yts_request(endpoint="list_movies.json",
                                         params={"query_term": search_query})
            continue

        results_table = populate_results_table(search_results)
        console.print(Markdown("---"))
        console.print(Align(results_table, align="center"))
        mode_choice = Prompt.ask("([red]s[/red])tream ([red]d[/red])ownload ([red]r[/red])e-search ([red]S[/red])ummaries ([red]t[/red])railers ([red]q[/red])uit",
                                 show_choices=False,
                                 choices=['d', 'r', 's', 'S', 't', 'q']) 
        if mode_choice == 'q':
            break

        elif mode_choice == 'r':
            search_query = Prompt.ask("Enter movie to search")
            r = yts.yts_request(endpoint="list_movies.json",
                                params={"query_term": search_query})
            continue

        elif mode_choice == 't':
            movie_idx = IntPrompt.ask(f"Choose a movie number to watch the trailer for [0-{len(search_results)-1}]",
                                      show_choices=False,
                                      choices=[str(i) for i in range(len(search_results))])

            movie_title = search_results[movie_idx]["title_long"]
            console.print(f"Opening trailer for {movie_title}...")
            console.print("[yellow]Caution:[/yellow] sometimes this will open a random youtube video if the trailer is not found.")
            trailer_url = "https://www.youtube.com/watch?v=" + search_results[movie_idx]["yt_trailer_code"]

            subprocess.run(["mpv", trailer_url])
            # subprocess.Popen(["mpv", trailer_url],
            #                  stdout=open('/dev/null', 'w'),
            #                  stderr=open('mpv.log', 'a'),
            #                  preexec_fn=os.setpgrp)  # Separate process from main thread
        
        elif mode_choice == 'S':
            movie_idx = IntPrompt.ask(f"Choose a movie number to summarize [0-{len(search_results)-1}]",
                                      show_choices=False,
                                      choices=[str(i) for i in range(len(search_results))])

            movie_title = search_results[movie_idx]["title_long"]
            console.print(Markdown("---"))
            console.print(Markdown(f"## Summary for {movie_title}:"))
            print("")
            summary = search_results[movie_idx]["summary"]
            if not summary or summary == ' ':
                console.print("   [red]Sorry![/red] No summary available.")
            else:
                console.print(Panel(summary))
    
            print("")
            return_input = input("Press any key to return to main menu: ")
            continue
        
        else:  # Either stream or download
            movie_idx = IntPrompt.ask(f"Choose a movie number [0-{len(search_results)-1}]",
                                      show_choices=False,
                                      choices=[str(i) for i in range(len(search_results))])

            movie_title = search_results[movie_idx]["title_long"]

            os.system("clear")
            console.print(f"You have chosen: {movie_title}")
            console.print(Markdown("### Torrent Information"))
            torrents = search_results[movie_idx]["torrents"]
            for idx, torrent in enumerate(torrents):
                panel_str = ""
                panel_str += f"Seeds: {torrent['seeds']}\n"
                panel_str += f"Peers: {torrent['peers']}\n"
                panel_str += f"Torrent Quality: {torrent['quality']}\n"
                panel_str += f"Torrent Size: {torrent['size']}"
                console.print(Panel.fit(panel_str, title=f"Torrent [{idx}]"))

            torrent_idx = IntPrompt.ask(f"Choose a torrent number [0-{len(torrents)-1}]",
                                      show_choices=False,
                                      choices=[str(i) for i in range(len(torrents))])

            torrent_hash = torrents[torrent_idx]["hash"]
            torrent_url = torrents[torrent_idx]["url"]

            magnet_link = yts.parse_magnet_link(torrent_hash, torrent_url)

            login_cookies = qb.login(qb_username, qb_password)
            download_dir = "/home/isaac/Videos/Films/"

            qb.add_torrent(magnet_link=magnet_link,
                           movie_title=movie_title,
                           save_path=download_dir,
                           login_cookies=login_cookies)

            console.print("[green]Added torrent![/green]")
            console.print(Markdown("---"))

            if mode_choice == 's':  # Open the torrent in mpv
                # console.print(f"Total torrent bytes: {torrent_size_bytes}")
                download_info = qb.get_torrent_progress(torrent_hash=torrent_hash, login_cookies=login_cookies)

                with Progress() as progress:
                    buffer_task = progress.add_task(description="[yellow]Waiting to begin download...[/yellow]", total=None)

                    while not download_info["size"]:  # Wait until torrent has started downloading
                        time.sleep(0.5)
                        download_info = qb.get_torrent_progress(torrent_hash=torrent_hash, login_cookies=login_cookies)
                    
                    # Update total size once torrent starts downloading
                    progress.update(task_id=buffer_task,
                                    description=f"[green]Buffering to {buffer_percent*100}% of file...[/green]",
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
                        console.print(f"[green]Opening:[/green][white]{torrent_dir + file}[/white] in mpv.")
                        subprocess.run(["mpv", torrent_dir + file])
                        break
            break





if __name__ == "__main__":
    main(check_for_expressvpn=True, buffer_percent=0.1)
