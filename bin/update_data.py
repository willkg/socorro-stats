#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import datetime
import json

import requests

import logging

# These two lines enable debugging at httplib level (requests->urllib3->http.client)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# The only thing missing will be the response.body which is not logged.
try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


API_URL = "https://crash-stats.mozilla.org/api/SuperSearch/"

TODAY = datetime.datetime.today().strftime("%Y-%m-%d")
YESTERDAY = (
    (datetime.datetime.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
)


DEFAULT_PARAMS = {
    "date": [f">={YESTERDAY}", f"<{TODAY}"],
    "_results_number": "0",
}

HEADERS = {
    "User-Agent": "socorro-stats <https://github.com/willkg/socorro-stats>",
}


# Get a facet of products and counts for yesterday
resp = requests.get(
    API_URL,
    params=dict(
        _facets="product",
        **DEFAULT_PARAMS
    ),
    headers=HEADERS,
)

resp.raise_for_status()
resp_data = resp.json()
print(resp_data)

with open("socorro_stats.json", "r") as fp:
    all_data = json.load(fp)

data_item = {
    "date": YESTERDAY,
    "total": resp_data["total"],
    "facet_product": resp_data["facets"]["product"],
}
# Replace an existing item with the date or append the new item
for i in range(len(all_data)):
    if all_data[i]["date"] == YESTERDAY:
        all_data[i] = data_item
else:
    all_data.append(data_item)

with open("socorro_stats.json", "w") as fp:
    json.dump(all_data, fp)
