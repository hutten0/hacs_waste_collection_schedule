import json
import re
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
from waste_collection_schedule import Collection  # type: ignore[attr-defined]
#from collection import Collection

# Västblekinge Miljö AB, Blekinge Sweden
#
# The public URL is https://cal.vmab.se
#
# One first has to do a search since they put an ID in the list of
# search results which is required when sending the request to get the
# bin data. The data then comes injected into a script tag as it's
# normally used to build a browseable calendar for easy viewing.
#
# Standard bins housholds have four types of waste each, and each
# house has 2 bins, example raw data for the two bins:
# { title: 'Max 1, Fyrfackskärl', start: '2023-01-11' },
# { title: 'Max 2, Fyrfackskärl', start: '2023-01-20' },
#
# The API will return about a years worth of bin collection dates
# and only the dates will change, title remains the same for the two
# bins. First one being Food, Burnables, Colored glass and Newspapers,
# and the second is Plastics, Cardboard, Non-colored glass and Metal.
#
# Different bins to include later on..
# Karlshamns kommun: Rådhusgatan 10, Karlshamn
# Folkets hus Olofström: Östra Storgatan 24, Folkets Hus Olofström
#

TITLE = "Västblekinge Miljö AB"
DESCRIPTION = "Source for Västblekinge Miljö AB waste collection."
URL = "https://vmab.se"
TEST_CASES = {
    "Home": {"street_address": "Gullregnsvägen 3, Mörrum"},
    "Olofström": {"street_address": "Parkvägen 1, Olofström"},
    "Asarum": {"street_address": "Parkvägen 10, Asarum"},
    "Mörrum": {"street_address": "Parkvägen 11, Mörrum"},
    "Sölvesborg": {"street_address": "Parkvägen 11, Sölvesborg"}
}

API_URL = "https://cal.vmab.se/"


class Source:
    def __init__(self, street_address):
        addr_parts = street_address.split(',')
        self._street_address = addr_parts[0]
        self._city = addr_parts[1].lstrip()

    def fetch(self):
        data = {"search_address": self._street_address}
        headers = {
            'Accept-Encoding': 'identity',
            'Accept': '*/*',
            'Accept-Language': 'sv-SE,sv;q=0.8,en-US;q=0.5,en;q=0.3',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        response = requests.post(
            "https://cal.vmab.se/search_suggestions.php",
            data=data,
            headers=headers
        )

        soup = bs(response.text, 'html.parser')
        pickup_id = False
        for el_addr in soup.find_all('span', attrs={'class': 'address'}):
            if el_addr.string == self._street_address:
                for el_addr_sib in el_addr.next_siblings:
                    if el_addr_sib.name == 'span' and el_addr_sib.string == self._city:
                        pickup_id = el_addr.parent['id']
                        break
                if pickup_id:
                    break
        if not pickup_id:
            return []

        data = {
            "chosen_address": "{} {}".format(self._street_address, self._city),
            "chosen_address_pickupid": pickup_id
        }
        response = requests.post(
            "https://cal.vmab.se/get_data.php",
            data=data,
            headers=headers
        )

        entries = []
        for entry in re.findall(r'{.title:[^}]+}', response.text):
            json_entry = json.loads(re.sub(r'(title|start):', r'"\1":', entry.replace("'", '"')))
            # Same icon always, due to two bins both being various recycled things
            # Todo: includ all type of bins with different icons
            icon = "mdi:recycle"
            waste_type = json_entry['title'] #.split(':')[1].lstrip()
            pickup_date = datetime.fromisoformat(json_entry['start']).date()
            entries.append(Collection(date=pickup_date, t=waste_type, icon=icon))
        return entries

# if __name__ == "__main__":
#     s = Source("Gullregnsvägen 3, Mörrum")
#     lst = s.fetch()
