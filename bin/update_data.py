#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import datetime
import json
import logging

import requests


# These two lines enable debugging at httplib level
# (requests->urllib3->http.client) You will see the REQUEST, including HEADERS
# and DATA, and RESPONSE with HEADERS but without DATA. The only thing missing
# will be the response.body which is not logged.
import http.client as http_client
http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


API_URL = "https://crash-stats.mozilla.org/api/SuperSearch/"


def fetch_data(start_date, end_date):
    default_params = {
        "date": [f">={start_date}", f"<{end_date}"],
        "_results_number": "0",
    }

    headers = {
        "User-Agent": "socorro-stats <https://github.com/willkg/socorro-stats>",
    }

    # Get a facet of products and counts for yesterday
    resp = requests.get(
        API_URL,
        params=dict(
            _facets="product",
            **default_params,
        ),
        headers=headers,
    )

    resp.raise_for_status()
    resp_data = resp.json()
    print(resp_data)
    return resp_data


today_dt = datetime.datetime.today()
end_date = today_dt.strftime("%Y-%m-%d")
start_date = (today_dt - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

resp_data = fetch_data(start_date, end_date)

# Generate record
data_item = {
    "date": start_date,
    "total": resp_data["total"],
}
data_item.update(
    {
        item["term"]: item["count"]
        for item in resp_data["facets"]["product"]
    }
)

with open("socorro_stats.json", "r") as fp:
    all_data = json.load(fp)

# Replace an existing item with the date or append the new item
for i in range(len(all_data)):
    if all_data[i]["date"] == start_date:
        all_data[i] = data_item
        break
else:
    all_data.append(data_item)

with open("socorro_stats.json", "w") as fp:
    json.dump(all_data, fp)
