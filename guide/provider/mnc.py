import json
import requests

from bs4 import BeautifulSoup
from channels import channels
from datetime import datetime, timedelta

channels = {
    350: "ABC Australia",
    331: "Al Jazeera English",
    93: "Al Quran Al Kareem",
    203: "Animal Planet",
    157: "Animax",
    115: "ANTV",
    351: "Arirang",
    240: "Asian Food Network",
    450: "Asian Food Network HD",
    154: "AXN",
    438: "AXN HD",
    40: "BabyTV",
    200: "BBC Earth",
    461: "BBC Earth HD",
    332: "BBC World News",
    305: "beIN Sports 1",
    425: "beIN Sports 1 HD",
    306: "beIN Sports 2",
    426: "beIN Sports 2 HD",
    103: "Berita Satu",
    112: "besmart",
    338: "Bloomberg",
    39: "Boomerang",
    47: "Cartoon Network",
    473: "Cartoon Network HD",
    41: "CBeebies",
    22: "CCM",
    20: "Celestial Movies",
    330: "Channel News Asia",
    272: "Channel [V]",
    8: "CINEMAX",
    402: "CINEMAX HD",
    337: "CNBC",
    333: "CNN International",
    207: "Crime Investigation",
    201: "Discovery Channel",
    45: "Disney Channel",
    471: "Disney Channel HD",
    43: "Disney Junior",
    472: "Disney Junior HD",
    44: "Disney XD",
    357: "DW English",
    86: "Entertainment",
    304: "Fight Sports",
    150: "FMN",
    153: "FOX",
    16: "FOX Action Movies",
    411: "FOX Action Movies HD",
    152: "FOX Crime",
    440: "Fox Crime HD",
    15: "FOX Family Movies",
    410: "FOX Family Movies HD",
    437: "FOX HD",
    156: "Fox Life",
    439: "Fox Life HD",
    14: "FOX Movies",
    409: "FOX Movies Premium HD",
    335: "FOX News",
    301: "FOX Sports",
    302: "FOX Sports 2",
    422: "FOX Sports 2 HD",
    303: "FOX Sports 3",
    421: "FOX Sports HD",
    352: "France 24 English",
    159: "FX",
    81: "Global TV",
    431: "GTV HD",
    7: "HBO",
    9: "HBO Family",
    403: "HBO Family HD",
    401: "HBO HD",
    10: "HBO Hits",
    404: "HBO Hits HD",
    6: "HBO Signature",
    405: "HBO Signature HD",
    245: "HGTV",
    451: "HGTV HD",
    206: "History",
    160: "HITS",
    11: "HITS Movies",
    100: "IDX",
    78: "Indosiar",
    83: "iNews",
    96: "Infotaiment",
    113: "JAKTV",
    46: "Kids TV",
    161: "KIX",
    106: "Kompas TV",
    91: "LIFE",
    90: "Lifestyle & Fashion",
    167: "Lifetime",
    107: "Metro TV",
    38: "Miao Mi",
    84: "MNC News",
    79: "MNC Shop Smart",
    88: "MNC Shop Trendy",
    102: "MNC Sports",
    101: "MNC Sports 2",
    82: "MNCTV",
    432: "MNCTV HD",
    111: "Music TV",
    92: "Muslim TV",
    202: "National Geographic Channel",
    460: "National Geographic Channel HD",
    247: "National Geographic People",
    204: "National Geographic Wild",
    116: "Net TV",
    355: "NHK World",
    354: "NHK World Premium",
    49: "Nickelodeon",
    37: "Nickelodeon Jr",
    95: "OK TV",
    164: "ONE",
    445: "ONE HD",
    80: "RCTI",
    430: "RCTI HD",
    18: "SCM",
    416: "SCM HD",
    24: "SCM Legend",
    89: "SCTV",
    105: "Tawaf TV",
    19: "Thrill",
    248: "TLC",
    110: "Trans 7",
    87: "Trans TV",
    158: "tvN",
    446: "tvN HD",
    25: "tvN Movies",
    415: "tvN Movies HD",
    97: "tvOne",
    118: "TVRI",
    94: "Vision Prime",
    1: "Vision Prime HD",
    168: "WAKUWAKU JAPAN",
    163: "Warner TV",
    441: "Warner TV HD",
    23: "ZEE",
}

class Mnc(object):
    def __init__(self):
        self.session = requests.Session()
        self.url = "https://mncvision.id/schedule/table"

        page = self.session.get(self.url).text
        soup = BeautifulSoup(page, "html.parser")
        self.options = []
        for option in soup.find_all("option"):
            self.options.append(option["value"])

    def get_channels(self, print_=False):
        if print_:
            for option in self.options:
                print(f"{option} {channels['mnc'][int(option)]}")
        return self.options

    def get_shows(self, selected_channel, date):
        req = {
            "search_model": (None, "channel"),
            "af0rmelement": (None, "aformelement"),
            "fdate": (None, date),
            "fchannel": (None, selected_channel),
            "submit": (None, "Cari"),
        }
        channelPage = self.session.post(self.url, files=req).text
        channelSoup = BeautifulSoup(channelPage, "html.parser")
        table = channelSoup.table
        table_time_raw = table.find_all("td", class_="text-center")
        table_show_raw = table.find_all("a")

        table_shows = []
        for i in table_show_raw:
            table_shows.append(i.get("title"))

        table_times = []
        for i in range(len(table_time_raw)):
            if (i + 1) % 2 == 0:
                pass
            else:
                table_times.append(table_time_raw[i].get_text())

        return table_times, table_shows, selected_channel

    def print_things(self, ch):
        date, times, shows, channel = self.get_shows(ch)
        for i in range(len(times)):
            try:
                time_1 = str(date[1]).replace("-", "") + str(times[int(i)]).replace(
                    ":", ""
                )
                time_2 = str(date[1]).replace("-", "") + str(times[int(i + 1)]).replace(
                    ":", ""
                )
            except IndexError:
                time_1 = str(date[1]).replace("-", "") + str(times[int(i)]).replace(
                    ":", ""
                )
                time_2 = str(date[1]).replace("-", "") + str(times[int(0)]).replace(
                    ":", ""
                )
            time_1 += " +0700"
            time_2 += " +0700"
            print(
                f'  <programme start="{time_1}" stop="{time_2}" channel="{channel[1]}">'
            )
            print(f'    <title lang="id">{shows[int(i)]}</title>')
            print(f"  </programme>")
