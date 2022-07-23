from rich.live import Live
from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from rich.console import Console
import os
import time

# For ascii text generation
# https://www.texttool.com/ascii-font#p=display&f=Delta%20Corps%20Priest%201&t=ACTIONS
# ANSI Shadow
medium_title_str = """

 ██████╗██╗███╗   ██╗███████╗████████╗███████╗██████╗ ███╗   ███╗
██╔════╝██║████╗  ██║██╔════╝╚══██╔══╝██╔════╝██╔══██╗████╗ ████║
██║     ██║██╔██╗ ██║█████╗     ██║   █████╗  ██████╔╝██╔████╔██║
██║     ██║██║╚██╗██║██╔══╝     ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║
╚██████╗██║██║ ╚████║███████╗   ██║   ███████╗██║  ██║██║ ╚═╝ ██║
 ╚═════╝╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝

"""

# Delta Coprs Priest 1
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


color_list = [
    "light_sea_green",
    "deep_sky_blue2",
    "deep_sky_blue1",
    "green3",
    "spring_green3",
    "cyan3",
    "dark_turquoise",
    "turquoise2",
    "green1",
    "spring_green2",
    "spring_green1",
    "medium_spring_green",
    "cyan2",
    "cyan1",
    "purple4",
    "purple3",
    "blue_violet",
    "grey37",
    "medium_purple4",
    "slate_blue3",
    "royal_blue1",
    "chartreuse4",
    "pale_turquoise4",
    "steel_blue",
    "steel_blue3",
    "cornflower_blue",
    "dark_sea_green4",
    "cadet_blue",
    "sky_blue3",
    "chartreuse3",
    "sea_green3",
    "aquamarine3",
    "medium_turquoise",
    "steel_blue1",
    "sea_green2",
    "sea_green1",
    "dark_slate_gray2",
    "dark_red",
    "dark_magenta",
    "orange4",
    "light_pink4",
    "plum4",
    "medium_purple3",
    "slate_blue1",
    "wheat4",
    "grey53",
    "light_slate_grey",
    "medium_purple",
    "light_slate_blue",
    "yellow4",
    "dark_sea_green",
    "light_sky_blue3",
    "sky_blue2",
    "chartreuse2",
    "pale_green3",
    "dark_slate_gray3",
    "sky_blue1",
    "chartreuse1",
    "light_green",
    "aquamarine1",
    "dark_slate_gray1",
    "deep_pink4",
    "medium_violet_red",
    "dark_violet",
    "purple",
    "medium_orchid3",
    "medium_orchid",
    "dark_goldenrod",
    "rosy_brown",
    "grey63",
    "medium_purple2",
    "medium_purple1",
    "dark_khaki",
    "navajo_white3",
    "grey69",
    "light_steel_blue3",
    "light_steel_blue",
    "dark_olive_green3",
    "dark_sea_green3",
    "light_cyan3",
    "light_sky_blue1",
    "green_yellow",
    "dark_olive_green2",
    "pale_green1",
    "dark_sea_green2",
    "pale_turquoise1",
    "red3",
    "deep_pink3",
    "magenta3",
    "dark_orange3",
    "indian_red",
    "hot_pink3",
    "hot_pink2",
    "orchid",
    "orange3",
    "light_salmon3",
    "light_pink3",
    "pink3",
    "plum3",
    "violet",
    "gold3",
    "light_goldenrod3",
    "tan",
    "misty_rose3",
    "thistle3",
    "plum2",
    "yellow3",
    "khaki3",
    "light_yellow3",
    "grey84",
    "light_steel_blue1",
    "yellow2",
    "dark_olive_green1",
    "dark_sea_green1",
    "honeydew2",
    "light_cyan1",
    "red1",
    "deep_pink2",
    "deep_pink1",
    "magenta2",
    "magenta1",
    "orange_red1",
    "indian_red1",
    "hot_pink",
    "medium_orchid1",
    "dark_orange",
    "salmon1",
    "light_coral",
    "pale_violet_red1",
    "orchid2",
    "orchid1",
    "orange1",
    "sandy_brown",
    "light_salmon1",
    "light_pink1",
    "pink1",
    "plum1",
    "gold1",
    "light_goldenrod2",
    "navajo_white1",
    "misty_rose1",
    "thistle1",
    "yellow1",
    "light_goldenrod1",
    "khaki1",
    "wheat1",
    "cornsilk"
]

# color_list = ["rgb(253,126,126)", "rgb(253,191,134)", "rgb(172,253,179)", "rgb(117,253,242)", "rgb(120,131,253)", "rgb(196,120,253)"]

# color_list = ["#2e41ef", "#4260ea", "#5680e5", "#6a9fe0",
#               "#7ebfdb", "#92ded6", "#7ebfdb", "#6a9fe0",
#               "#5680e5", "#4260ea"]

# color_list = ["#ff0000", "#ffa500", "#ffff00", "#008000", "#0000ff", "#4b0082", "#ee82ee"]
# color_list = ["red", "green", "yellow", "blue", "magenta", "cyan", "white"]


def get_title_str(small_str: str, medium_str: str, large_str: str) -> str:
    """Return small_str, medium_str or large_str depending on terminal width."""
    term_width = os.get_terminal_size().columns
    if term_width > 100:
        return large_str
    elif 60 < term_width and term_width < 100:
        return medium_str
    else:
        return small_str


def display_static_title(console: Console) -> None:
    title_str = get_title_str(small_str="CineTerm",
                              medium_str=medium_title_str,
                              large_str=large_title_str)
    console.print(Panel(Align(renderable=title_str, align="center")))


def display_live_title() -> None:

    def generate_title_table(i: int) -> Table:
        joke_str = "Hi, welcome to chillis!!!!!!!!!!!!!"
        term_width = os.get_terminal_size().columns
        color_1 = color_list[i % len(color_list)]
        color_2 = color_list[(2 * i) % len(color_list)]
        title_str = f"[{color_1}]" + get_title_str("CineTerm",
                                                   medium_title_str,
                                                   large_title_str) + \
            f"[/{color_1}]" + '\n' + \
            f"[{color_2}]{joke_str[:i % (len(joke_str) + 1)]}[/{color_2}]"

        t = Table(width=term_width, box=None,
                  show_header=False, show_footer=False,
                  show_lines=False, show_edge=False)
        t.add_row(Panel(Align(renderable=title_str, align="center")))
        t.add_row("[red]Ctrl-c[/red] to search for a movie...")
        return t

    with Live(generate_title_table(0), refresh_per_second=4) as live:
        i = 0
        while True:
            try:
                time.sleep(0.25)
                live.update(generate_title_table(i))
                i = (i + 1) % len(color_list)
            except KeyboardInterrupt:  # Break out of while loop with Ctrl-c
                break


if __name__ == "__main__":
    display_live_title()
