import json
import requests

from bs4 import BeautifulSoup
from channels import channels
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET

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

    def print_things(self, ch, days):
        _date = datetime.now() + timedelta(days=days)
        times, shows_name, channel = self.get_shows(ch, datetime.now().strftime('%Y-%m-%d'))
        _next_date = _date + timedelta(days=1)
        shows = ""
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
            shows += f'\n  <programme start="{time_1}" stop="{time_2}" channel="{channel[1]}">'
            shows += f'\n    <title lang="id">{shows_name[int(i)]}</title>'
            shows += f"\n  </programme>"
        return shows
            
days = int(input("Days: "))
print("Starting Scraper...")
tv = TVScraper()
xml_data = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n\
<tv generator-info-name=\"ziTVScraper\" generator-info-url=\"http://github.com/null2264\">"
tv_channels = list(tv.get_channels())
print("Getting channels...")
for _tv in tv_channels:
    channel = int(_tv)
    xml_data += f"\n  <channel id=\"{channel}\">"
    xml_data += f"\n    <display-name lang=\"id\">{channels['mnc'][channel]}</display-name>"
    xml_data += f"\n  </channel>"
for _tv in tv_channels:
    print(f"Getting shows from {channels['mnc'][int(_tv)]}...")
    for day in range(days):
        # print(f"Day {day+1}...")
        xml_data += tv.print_things(int(_tv), day)
xml_data += "\n</tv>"

print("Creating file...")
with open("guide/guide.xml", "w+") as f:
    f.write(xml_data)
