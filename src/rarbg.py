# qb = Client('http://192.168.0.16:8080/', verify=False)

# https://yts.mx/api?amp=1
# https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#add-new-torrent

# from qbittorrent import Client
# from py1337x import py1337x

# torrents = py1337x(proxy=None)

# results = torrents.search("Predator")

# for result in results["items"]:
#     print(result)
#     print("")
#     print("")

import rarbgapi
client = rarbgapi.RarbgAPI()

categories = [ 
    rarbgapi.RarbgAPI.CATEGORY_MOVIE_XVID,
    rarbgapi.RarbgAPI.CATEGORY_MOVIE_XVID_720P,
    rarbgapi.RarbgAPI.CATEGORY_MOVIE_H264,
    rarbgapi.RarbgAPI.CATEGORY_MOVIE_H264_1080P,
    rarbgapi.RarbgAPI.CATEGORY_MOVIE_H264_720P,
    rarbgapi.RarbgAPI.CATEGORY_MOVIE_H264_3D,
    rarbgapi.RarbgAPI.CATEGORY_MOVIE_H264_4K,
    rarbgapi.RarbgAPI.CATEGORY_MOVIE_H265_4K,
    rarbgapi.RarbgAPI.CATEGORY_MOVIE_H265_4K_HDR,
    rarbgapi.RarbgAPI.CATEGORY_MOVIE_FULL_BD,
    rarbgapi.RarbgAPI.CATEGORY_MOVIE_BD_REMUX
]

results = client.search(search_string="Predator 1987", categories=categories)

for torrent in results:
    print("________________________________________________")
    print(torrent.filename)
    print("")
    print("Magnet Link: ", torrent.download)
    print("")
    print("Seeders: ", torrent.seeders)
    print("Leechers: ", torrent.leechers)
    print("")
    print("Torrent Size: ", torrent.size)
    print("")

