import pandas as pd
from pyfzf.pyfzf import FzfPrompt
from rich.console import Console
from cineterm.yts import yts_request


def fzf_get_movie_id(yts_movies_df: pd.DataFrame) -> int:
    """Prompt user movie choice, uses fzf to fuzzy match and display summar."""
    fzf = FzfPrompt()
    movie_choices = fzf.prompt(choices=yts_movies_df["title"],
                               fzf_options="-i --border " +
                               "--margin 1% --preview-window='wrap' " +
                               "--preview='" + f"python -m cineterm.previewer " + "{}'")
    if not movie_choices:  # If we escape we get an empty list
        return -1
    else:
        title = movie_choices[0]
        return yts_movies_df.loc[yts_movies_df["title"] == title]["id"].iloc[0]


def fzf_request_movie(yts_movies_df: pd.DataFrame, console: Console) -> dict:
    """Fuzzy prompt the user for search query and send a request to yts."""
    movie_id = fzf_get_movie_id(yts_movies_df)
    if movie_id != -1:  # Use -1 instead of 0 encase 0 is a valid movie id
        console.print(
            "[yellow] Caution:[/yellow] if a vpn is not active, your ISP may have blocked YTS so this could hang.")
        console.print(
            "To prevent this, make sure to either pass --vpn and use activate_vpn.sh or activate a vpn before launch.")
        with console.status(" Sending a request to [green]YTS[/green] to get torrents..."):
            r = yts_request(endpoint="movie_details.json",
                                params={"movie_id": movie_id})
        return r
    else:  # If we exit
        return {}


if __name__ == "__main__":
    yts_movies_df = pd.read_pickle("cache/yts_movies_df.pkl")
    print(fzf_get_movie_id(yts_movies_df))
