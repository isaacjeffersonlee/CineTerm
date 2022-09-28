import sys
import pickle
import numpy as np
from cineterm.config import LIB_PATH
# from cineterm.summary_mapper import summary_map
nan = np.nan

with open(f"{LIB_PATH}/summary_map.pkl", "rb") as f:
    summary_map = pickle.load(f)


def print_summary_str(title: str, summary_map: dict[str, str]) -> None:
    try:
        print(summary_map[title])
    except KeyError:
        print("Unable to find summary!")



if __name__ == "__main__":
    # populate_summary_mapper()
    title = sys.argv[1]
    print_summary_str(title, summary_map)
