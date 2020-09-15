import json
import requests
import sys

from bs4 import BeautifulSoup
from channels import channels
from datetime import datetime, timedelta
from provider import mnc
from xml.etree import ElementTree as ET


class TVScraper(object):
    def __init__(self):
        self.scrapers = {"mnc": mnc.Mnc()}
        with open("guide/config.json", "r") as f:
            self.choice = json.load(f)["sel_channels"]

        # self.session = requests.Session()
        # self.url = "https://mncvision.id/schedule/table"

        # page = self.session.get(self.url).text
        # soup = BeautifulSoup(page, "html.parser")
        # self.choice = {'mnc': [330]}
        # self.options = []
        # for option in soup.find_all("option"):
        #     self.options.append(option["value"])

    # TODO: Make this function able to get channels from multiple source
    def get_channels(self, print_=False):
        channels = []
        for provider in list(self.scrapers.keys()):
            try:
                for channel in self.choice[str(provider)]:
                    channels.append(channel)
            except KeyError:
                pass
        return channels
        # if print_:
        #     for option in self.options:
        #         print(f"{option} {channels['mnc'][int(option)]}")
        # return self.options

    def get_shows(self, selected_channel, date):
        # req = {
        #     "search_model": (None, "channel"),
        #     "af0rmelement": (None, "aformelement"),
        #     "fdate": (None, date),
        #     "fchannel": (None, selected_channel),
        #     "submit": (None, "Cari"),
        # }
        # channelPage = self.session.post(self.url, files=req).text
        # channelSoup = BeautifulSoup(channelPage, "html.parser")
        # table = channelSoup.table
        # table_time_raw = table.find_all("td", class_="text-center")
        # table_show_raw = table.find_all("a")

        # table_shows = []
        # for i in table_show_raw:
        #     table_shows.append(i.get("title"))

        # table_times = []
        # for i in range(len(table_time_raw)):
        #     if (i + 1) % 2 == 0:
        #         pass
        #     else:
        #         table_times.append(table_time_raw[i].get_text())
        if selected_channel in self.choice["mnc"]:
            scraper = self.scrapers["mnc"]
            # print(scraper.get_shows(selected_channel, date))
            return scraper.get_shows(selected_channel, date)
            # return table_times, table_shows, selected_channel
        else:
            return None

    def send_shows(self, ch, days):
        _date = datetime.now() + timedelta(days=days)
        times, shows_name, channel = self.get_shows(
            ch, datetime.now().strftime("%Y-%m-%d")
        )
        if not shows_name:
            return
        _next_date = _date + timedelta(days=1)
        shows = ""
        for i in range(len(times)):
            date = _date.strftime("%Y-%m-%d")
            next_date = _next_date.strftime("%Y%m%d")

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
            shows += (
                f'\n  <programme start="{time_1}" stop="{time_2}" channel="{channel}">'
            )
            shows += f'\n    <title lang="id">{shows_name[int(i)]}</title>'
            shows += f"\n  </programme>"
        return shows

    def start(self):
        days = int(input("Days: "))
        print("Starting Scraper...")
        xml_data = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            + '<tv generator-info-name="ziTVScraper" generator-info-url="http://github.com/null2264">'
        )
        tv_channels = self.get_channels()
        if len(tv_channels) <= 0:
            print("No channel selected")
            return
        print("Getting channels...")
        for _tv in tv_channels:
            channel = int(_tv)
            xml_data += f'\n  <channel id="{channel}">'
            xml_data += f"\n    <display-name lang=\"id\">{channels['mnc'][channel]}</display-name>"
            xml_data += f"\n  </channel>"
        for _tv in tv_channels:
            for day in range(days):
                print(
                    f"Getting shows from {channels['mnc'][int(_tv)]} [{day+1}/{days}]...\r",
                    end="",
                )
                # print(f"Day {day+1}...")
                xml_data += self.send_shows(int(_tv), day)
            print()
        xml_data += "\n</tv>"

        print("Creating EPG file...")
        with open("guide/guide.xml", "w+") as f:
            f.write(xml_data)
        print("EPG file has been created")


tv = TVScraper()
tv.start()
# xml_data = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n\
# <tv generator-info-name=\"ziTVScraper\" generator-info-url=\"http://github.com/null2264\">"
# tv_channels = tv.get_channels()
# print(tv_channels)
# print("Getting channels...")
# for _tv in tv_channels:
#     channel = int(_tv)
#     xml_data += f"\n  <channel id=\"{channel}\">"
#     xml_data += f"\n    <display-name lang=\"id\">{channels['mnc'][channel]}</display-name>"
#     xml_data += f"\n  </channel>"
# for _tv in tv_channels:
#     print(f"Getting shows from {channels['mnc'][int(_tv)]}...")
#     for day in range(days):
#         # print(f"Day {day+1}...")
#         xml_data += tv.print_things(int(_tv), day)
# xml_data += "\n</tv>"

# print("Creating file...")
# with open("guide/guide.xml", "w+") as f:
#     f.write(xml_data)
