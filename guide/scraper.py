import json
import requests

from bs4 import BeautifulSoup
from channels import channels
from datetime import datetime, timedelta

class TVScraper(object):
    def __init__(self):
        self.session = requests.Session()
        self.url = "https://mncvision.id/schedule/table"

        page = self.session.get(self.url).text
        soup = BeautifulSoup(page, "html.parser")
        self.options = []
        for option in soup.find_all("option"):
            self.options.append(option["value"])
    
    #TODO: Make this function able to get channels from multiple source
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

        return table_times, table_shows, req["fchannel"]

    def print_things(self, ch):
        times, shows, channel = self.get_shows(ch, datetime.now().strftime('%Y-%m-%d'))
        _date = datetime.now()
        _next_date = _date + timedelta(days=1)
        for i in range(len(times)):
            date = _date.strftime('%Y-%m-%d')
            next_date = _next_date.strftime('%Y%m%d')

            try:
                time_1 = str(date).replace("-", "") + str(times[int(i)]).replace(
                    ":", ""
                )
                time_2 = str(date).replace("-", "") + str(times[int(i + 1)]).replace(
                    ":", ""
                )
            except IndexError:
                time_1 = str(date).replace("-", "") + str(times[int(i)]).replace(
                    ":", ""
                )
                time_2 = str(next_date).replace("-", "") + str(times[int(0)]).replace(
                    ":", ""
                )
            time_1 += " +0700"
            time_2 += " +0700"
            print(
                f'  <programme start="{time_1}" stop="{time_2}" channel="{channel[1]}">'
            )
            print(f'    <title lang="id">{shows[int(i)]}</title>')
            print(f"  </programme>")
            # print(f"{time_1} {time_2} - {shows[int(i)]}")


tv = TVScraper()
print('<?xml version="1.0" encoding="UTF-8"?>')
print(
    '<tv generator-info-name="ziTVScraper" generator-info-url="http://github.com/null2264">'
)
tv_channels = list(tv.get_channels())
for _tv in tv_channels:
    channel = int(_tv)
    print(f'  <channel id="{channel}">')
    print(f"    <display-name lang=\"id\">{channels['mnc'][channel]}</display-name>")
    print(f"  </channel>")
for _tv in tv_channels:
    tv.print_things(int(_tv))
print("</tv>")
# _input=int(input())
# print(chr(27) + "[2J")
