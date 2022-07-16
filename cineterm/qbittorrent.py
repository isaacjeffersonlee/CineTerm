import requests
from requests.cookies import RequestsCookieJar  # For type hint
from rich.console import Console  # For pretty printing
import json
import psutil
import os
import subprocess
import time


def launch_qbittorrent(logfile_path: str) -> None:
    """Launch qbittorrent in a new process if not already running."""
    if "qbittorrent" not in (i.name() for i in psutil.process_iter()):
        subprocess.Popen(["qbittorrent"],
                         stdout=open("/dev/null", 'w'),
                         stderr=open(logfile_path, 'a'),
                         preexec_fn=os.setpgrp)  # Separate process from main thread

def login(qb_username: str, qb_password: str, logfile_path: str) -> RequestsCookieJar:
    """Launch qbittorrent if not running and get login cookies."""
    launch_qbittorrent(logfile_path)
    time.sleep(2)  # Sleep to allow enough time for qbittorrent to launch
    assert "qbittorrent" in (i.name() for i in psutil.process_iter()), \
        "qbittorrent not launched! Make sure it is installed!"
    r = requests.post(url="http://localhost:8080/api/v2/auth/login",
                      headers={"Referer": "http://localhost:8080"},
                      data={"username": qb_username, "password": qb_password})
    assert r.status_code == 200, f"Failed to login, status code: {r.status_code}"
    return r.cookies


def add_torrent(magnet_link: str, movie_title: str, save_path: str, login_cookies: RequestsCookieJar) -> None:
    """Add torrent and begin leeching torrent with qbittorrent."""
    data = {
        "urls": magnet_link,
        "savepath": save_path,
        "paused": "false",
        "root_folder": "true",
        "rename": movie_title,
        "sequentialDownload": "true",
        "firstLastPiecePrio": "true"
    }
    r = requests.post(url="http://localhost:8080/api/v2/torrents/add",
                      data=data,
                      cookies=login_cookies) 
    assert r.status_code == 200, f"Failed to add torrent!"


def remove_torrent(torrent_hash: str, delete_files: bool, login_cookies: RequestsCookieJar) -> None:
    """Remove a torrent and optionally delete files."""
    torrent_hash = torrent_hash.lower()
    data = {
        "hashes" : torrent_hash,
        "deleteFiles" : "true" if delete_files else "false"
    }
    r = requests.post(url="http://localhost:8080/api/v2/torrents/delete",
                      data=data,
                      cookies=login_cookies) 
    assert r.status_code == 200, f"Failed to remove torrent!"


def list_torrents(login_cookies: RequestsCookieJar) -> dict:
    """List all currently active torrents in qbittorrent."""
    r = requests.get(url="http://localhost:8080/api/v2/torrents/info",
                      cookies=login_cookies) 
    assert r.status_code == 200, f"Failed to add torrent!"
    return r.json()

def get_torrent_progress(torrent_hash: str, login_cookies: RequestsCookieJar) -> dict:
    torrent_hash = torrent_hash.lower()
    torrents = list_torrents(login_cookies=login_cookies)
    for torrent in torrents:
        if torrent["hash"] == torrent_hash:
            return {"downloaded": torrent["downloaded"],
                    "amount_left": torrent["amount_left"],
                    "size": torrent["size"],
                    "availability": torrent["availability"]}

    return {"downloaded": 0, "amount_left": 0, "size": 0}  # If we fail to get torrent data

if __name__ == "__main__":
    console = Console()
    with open("../credentials.json", 'r') as f:
        credentials = json.load(f)
    qb_username = credentials["qb_username"]
    qb_password = credentials["qb_password"]
    login_cookies = login(logfile_path="../logfile.log",
                          qb_username=qb_username,
                          qb_password=qb_password)
    console.print(list_torrents(login_cookies))
    # test_hash = "0365534D94E4D8412511C32FE0D288C0BEA8C911"
    # remove_torrent(torrent_hash=test_hash, delete_files=True, login_cookies=login_cookies)
    # example_magnet_link = "magnet:?xt=urn:btih:FDB569EC7F853672103FB82EA79F5FAB20247591&dn=https://yts.mx/torrent/download/FDB569EC7F853672103FB82EA79F5FAB20247591&tr=udp://open.demonii.com:1337/announce&tr=udp://tracker.openbittorrent.com:80&tr=udp://tracker.coppersurfer.tk:6969&tr=udp://glotorrents.pw:6969/announce&tr=udp://tracker.opentrackr.org:1337/announce&tr=udp://torrent.gresille.org:80/announce&tr=udp://p4p.arenabg.com:1337&tr=udp://tracker.leechers-paradise.org:6969"
    # add_torrent(magnet_link=example_magnet_link,
    #             movie_title="Predator (1987)",
    #             save_path="/home/isaac/Videos/Films/",
    #             login_cookies=login_cookies)

