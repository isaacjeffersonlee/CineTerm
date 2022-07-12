import requests
import json
from rich.console import Console  # For pretty printing

console = Console()


base_url = "https://yts.mx/api/v2/"


def yts_request(endpoint: str, params: dict) -> dict:
    r = requests.get(url=base_url + endpoint, params=params)
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
        "udp://tracker.leechers-paradise.org:6969"
    ]
    magnet_link = f"magnet:?xt=urn:btih:{torrent_hash}&dn={torrent_url}"
    for tracker in trackers:
        magnet_link += f"&tr={tracker}"

    return magnet_link


if __name__ == "__main__":
    search_query = "Harry Potter"
    console.print(yts_request(endpoint="list_movies.json", params={"query_term": search_query}))
    # yts_request(endpoint="movie_suggestions.json", params={"movie_id": movie_id})
    torrent_hash = "D1766D6B7FE09E35C9A7471761D629B1EB7B34A4"
    torrent_url = "https://yts.mx/movies/harry-potter-and-the-deathly-hallows-part-1-2010"
    console.print(parse_magnet_link(torrent_hash, torrent_url))
