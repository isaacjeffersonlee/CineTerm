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
import argparse
import os
import cineterm.title as title_printer
import cineterm.selector as selector
import cineterm.qbittorrent as qb
import cineterm.yts as yts
from cineterm.config import (
    ROOT_PATH,
    CACHE_PATH,
    LOG_PATH,
    DOWNLOAD_DIR,
    QB_USERNAME,
    QB_PASSWORD,
)


# Rich setup for pretty printing
status_spinner = "dots"
console = Console()

# For text to speech
speech_language = "en-uk-wmids"


def check_connection(timeout: int = 1) -> bool:
    """Ping google to check internet connection."""
    try:
        requests.head("http://www.google.com/", timeout=timeout)
        return True
    except requests.ConnectionError:
        return False


def populate_results_table(search_results: list[dict]) -> Table:
    """Populate a rich table using search_results."""
    results_table = Table(title=None, show_lines=False)
    results_table.add_column("", justify="left", style="cyan")
    results_table.add_column("Title", justify="left", style="white")
    results_table.add_column("Year", justify="left", style="green")
    for idx, result in enumerate(search_results):
        results_table.add_row(
            str(idx), f"[bold]{result['title']}[/bold]", str(result["year"])
        )
    return results_table


def print_movie_info(
    title: str, summary: str, rating: float, runtime: int, genres: list[str]
) -> None:
    console.print(Markdown(f"## {title}:"))
    print("")
    if not summary or summary == " ":
        summary = "[red]Sorry![/red] No summary available."

    console.print(Align(renderable=Panel(renderable=summary, width=50), align="center"))
    print("")
    console.print(Align(renderable=f"Rating: {rating}/10.0", align="center"))
    print("")
    console.print(Align(renderable=f"Runtime: {runtime} mins", align="center"))
    print("")
    console.print(
        Align(
            renderable="Genres: "
            + " | ".join([f"[blue]{genre}[/blue]" for genre in genres]),
            align="center",
        )
    )


def get_mode_choice() -> str:
    console.print(
        Align(
            renderable=" ([red bold]s[/red bold])tream"
            + " ([red bold]d[/red bold])ownload "
            + "([red bold]r[/red bold])e-search ([red bold]S[/red bold])peak "
            + "([red bold]t[/red bold])railer ([red bold]u[/red bold])pdate"
            + " ([red bold]q[/red bold])uit",
            align="center",
        )
    )
    return Prompt.ask(
        " [yellow]Enter action letter[/yellow]",
        show_choices=False,
        choices=["d", "r", "s", "S", "t", "u", "q"],
    )


def print_torrent_info(torrents: list[dict]) -> None:
    torrent_title_str = title_printer.get_title_str(
        small_str="Torrents",
        medium_str=title_printer.medium_torrent_str,
        large_str=title_printer.large_torrent_str,
    )
    console.print(Panel(Align(renderable=torrent_title_str, align="center")))
    for idx, torrent in enumerate(torrents):
        panel_str = ""
        panel_str += f"[green]Seeds:[/green] {torrent['seeds']}\n"
        panel_str += f"[red]Peers:[/red] {torrent['peers']}\n"
        panel_str += f"Torrent Quality: [bold]{torrent['quality']}[/bold]\n"
        panel_str += f"Torrent Size: [blue]{torrent['size']}[/blue]"
        console.print(
            Align(
                Panel(
                    renderable=panel_str, title=f"Torrent [[red]{idx}[/red]]", width=30
                ),
                align="center",
            )
        )


def connect_vpn() -> None:
    """Activate expressvpn connection."""
    try:
        # with console.status("Connecting to vpn...", spinner=status_spinner):
        console.print(f"Running {ROOT_PATH}/activate_vpn.sh")
        subprocess.run([f"{ROOT_PATH}/activate_vpn.sh"])
        # stdout=open("/dev/null", 'w'),
        # stderr=open(LOG_PATH, 'a'))
        # console.print("[green]Success:[/green] connected to vpn!")
    except Exception:
        console.print("[red]Warning:[/red] vpn failed to connect!")


def run(
    download_dir: str,
    activate_vpn: bool,
    buffer_percent: float = 0.05,
) -> None:

    with console.status("Checking internet connection...", spinner=status_spinner):
        connected = check_connection()

    if not connected:
        console.print("[red]Error:[/red] Internet is not connected!")
        return None

    os.system("clear")

    if activate_vpn:
        connect_vpn()

    yts_movies_df = yts.read_in_movies_df(CACHE_PATH)

    title_printer.display_live_title()

    r = selector.fzf_request_movie(yts_movies_df, console)
    os.system("clear")

    while True:
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
            # r = selector.fzf_request_movie(yts_movies_df, console)
            continue

        movie = r["data"]["movie"]
        movie_title = movie["title_long"]
        summary = movie["description_intro"]
        genres = movie["genres"]
        rating = movie["rating"]
        runtime = movie["runtime"]

        print_movie_info(
            title=movie_title,
            summary=summary,
            genres=genres,
            rating=rating,
            runtime=runtime,
        )
        print("")
        console.print(Markdown("---"))
        print("")
        mode_choice = get_mode_choice()

        if mode_choice == "u":
            yts.update_database(CACHE_PATH)
            input("Press any key to return to main menu...")
            os.system("clear")
            continue

        if mode_choice == "q":
            break

        elif mode_choice == "r":
            r = selector.fzf_request_movie(yts_movies_df, console)
            os.system("clear")
            continue

        elif mode_choice == "t":
            console.print(
                "[yellow]Caution:[/yellow] sometimes this will open a"
                + "random youtube video if the trailer is [red]not found[/red]."
            )
            console.print(f"Opening trailer for {movie_title}...")
            trailer_url = "https://www.youtube.com/watch?v=" + movie["yt_trailer_code"]
            subprocess.run(["mpv", trailer_url])

        elif mode_choice == "S":
            os.system("clear")
            console.print(Markdown("---"))
            print_movie_info(
                title=movie_title,
                summary=summary,
                genres=genres,
                rating=rating,
                runtime=runtime,
            )

            try:
                console.print("[red]Ctrl-c[/red] to stop voice.")
                subprocess.run(
                    ["espeak", "-v", speech_language, summary],
                    stdout=open("/dev/null", "w"),
                    stderr=open(LOG_PATH, "a"),
                )
            except KeyboardInterrupt:
                pass

            print("")
            os.system("clear")
            continue

        else:  # Either stream or download
            torrents = movie["torrents"]
            os.system("clear")
            console.print(f"You have chosen: {movie_title}")
            print_torrent_info(torrents)
            console.print(Markdown("---"))
            torrent_idx = IntPrompt.ask(
                " [yellow]Choose a torrent number"
                + f" [[red]0-{len(torrents)-1}[/red]][/yellow]",
                show_choices=False,
                choices=[str(i) for i in range(len(torrents))],
            )

            torrent_hash = torrents[torrent_idx]["hash"]
            torrent_url = torrents[torrent_idx]["url"]

            magnet_link = yts.parse_magnet_link(torrent_hash, torrent_url)

            with console.status("Connecting to qbittorrent...", spinner=status_spinner):
                login_cookies = qb.login(
                    logfile_path=LOG_PATH,
                    qb_username=QB_USERNAME,
                    qb_password=QB_PASSWORD,
                )

            with console.status("Adding torrent to qbittorrent..."):
                qb.add_torrent(
                    magnet_link=magnet_link,
                    movie_title=movie_title,
                    save_path=download_dir,
                    login_cookies=login_cookies,
                )

            console.print(" [green]Added torrent![/green]")

            if mode_choice == "s":  # Open the torrent in mpv
                delete_after_viewing = Confirm.ask(
                    " [yellow]Delete torrent files after viewing?[/yellow]"
                )
                # console.print(f"Total torrent bytes: {torrent_size_bytes}")
                download_info = qb.get_torrent_progress(
                    torrent_hash=torrent_hash, login_cookies=login_cookies
                )

                with Progress() as progress:
                    buffer_task = progress.add_task(
                        description="[yellow] Waiting to begin download...[/yellow]",
                        total=None,
                    )

                    # Wait until torrent has started downloading
                    while not download_info["size"]:
                        time.sleep(0.5)
                        download_info = qb.get_torrent_progress(
                            torrent_hash=torrent_hash, login_cookies=login_cookies
                        )

                    # Update total size once torrent starts downloading
                    progress.update(
                        task_id=buffer_task,
                        description=f" [green]Buffering to {buffer_percent*100}% of file...[/green]",
                        completed=download_info["downloaded"],
                        total=buffer_percent * download_info["size"],
                    )

                    # We only wait for 10% completion before opening the file.
                    while (
                        download_info["availability"] != -1
                        and download_info["downloaded"] / download_info["size"]
                        < buffer_percent
                    ):
                        download_info = qb.get_torrent_progress(
                            torrent_hash=torrent_hash, login_cookies=login_cookies
                        )
                        progress.update(
                            buffer_task, completed=download_info["downloaded"]
                        )
                        time.sleep(0.5)

                all_items_in_download_dir = os.listdir(download_dir)
                # Fuzzy match the file name since the torrent files often have unexpected names.
                best_match = process.extractOne(
                    movie_title, all_items_in_download_dir, scorer=fuzz.token_sort_ratio
                )[0]
                if download_dir[-1] != "/":
                    download_dir += "/"
                torrent_dir = download_dir + best_match + "/"
                for file in os.listdir(torrent_dir):
                    ext = file.split(".")[-1]
                    if ext == "mp4" or ext == "mkv":
                        console.print(
                            f" [green]Opening:[/green][white]{torrent_dir + file}[/white] in mpv."
                        )
                        subprocess.run(["mpv", torrent_dir + file])
                        break

                if (
                    not delete_after_viewing
                ):  # Wait for the torrent to finish downloading
                    with Progress() as progress:
                        buffer_task = progress.add_task(
                            description="Checking on torrent...", total=None
                        )

                        # Wait until torrent has started downloading
                        while not download_info["size"]:
                            time.sleep(0.5)
                            download_info = qb.get_torrent_progress(
                                torrent_hash=torrent_hash, login_cookies=login_cookies
                            )

                        # Update total size once torrent starts downloading
                        progress.update(
                            task_id=buffer_task,
                            description=f" [green]Downloading to 100%...[/green]",
                            completed=download_info["downloaded"],
                            total=download_info["size"],
                        )

                        # We only wait for 10% completion before opening the file.
                        # While we are not seeding
                        while download_info["availability"] != -1:
                            download_info = qb.get_torrent_progress(
                                torrent_hash=torrent_hash, login_cookies=login_cookies
                            )
                            progress.update(
                                buffer_task, completed=download_info["downloaded"]
                            )
                            time.sleep(0.5)

                with console.status(
                    "[cyan bold]qbittorrent:[/cyan bold] Removing torrent..."
                ):
                    qb.remove_torrent(
                        torrent_hash=torrent_hash,
                        delete_files=delete_after_viewing,
                        login_cookies=login_cookies,
                    )

                console.print("[green]Seeding[/green] / [red]Leeching[/red] stopped!")
                console.print(
                    f"Files{' ' if delete_after_viewing else ' [green]not[/green] '}deleted!"
                )

            console.print("[red]❤[/red] [cyan]Goodbye![/cyan] [red]❤[/red]")
            break


def main():
    """Entry point."""
    parser = argparse.ArgumentParser()  # For command line args

    parser.add_argument(
        "-d",
        "--download-dir",
        dest="download_dir",
        help="Path of directory to download films to.",
    )
    parser.add_argument(
        "-v",
        "--vpn",
        action="store_true",
        dest="activate_vpn",
        help="Call activate_vpn.sh on startup.",
    )
    parser.add_argument(
        "-b",
        "--buffer-percent",
        dest="buffer_percent",
        type=float,
        help="Percentage to download file before opening.\n Recommended is 0.05",
    )

    args = parser.parse_args()

    if not args.download_dir:
        download_dir = DOWNLOAD_DIR
    else:
        download_dir = args.download_dir

    if not args.buffer_percent:
        buffer_percent = 0.05
    else:
        buffer_percent = args.buffer_percent
        assert (
            0.0 < buffer_percent and buffer_percent < 1.0
        ), "Buffer percent must be between 0.0 and 1.0"

    run(
        download_dir=download_dir,
        activate_vpn=args.activate_vpn,
        buffer_percent=buffer_percent,
    )


if __name__ == "__main__":
    main()
