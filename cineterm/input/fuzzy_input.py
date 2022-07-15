import pandas as pd
from rich.console import Console
from pyfzf.pyfzf import FzfPrompt
fzf = FzfPrompt()
yts_movie_df = pd.read_csv("yts_all_movies.csv")

if __name__ == "__main__":
    console = Console()
    movie_choice = fzf.prompt(choices=yts_movie_df["title"],
                              fzf_options="--border --margin 10% --preview-window='wrap' --preview='python previewer.py {}'")[0]
    console.print(f"You have chosen: {movie_choice}")
    
