import pandas as pd
from pyfzf.pyfzf import FzfPrompt
import yts


def fzf_get_movie_id(yts_movies_df: pd.DataFrame) -> int:
    """Prompt user movie choice, uses fzf to fuzzy match and display summar."""
    fzf = FzfPrompt()
    movie_choices = fzf.prompt(choices=yts_movies_df["title"], 
                               fzf_options="-i --border --margin 10% --preview-window='wrap' --preview='python previewer.py {}'")
    if not movie_choices:  # If we escape we get an empty list
        return -1
    else:
        title = movie_choices[0]
        return yts_movies_df.loc[yts_movies_df["title"] == title]["id"].iloc[0]


if __name__ == "__main__":
    yts_movies_df = pd.read_pickle("cache/yts_movies_df.pkl")
    print(fzf_get_movie_id(yts_movies_df))
    
