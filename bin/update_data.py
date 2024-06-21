#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import datetime
import json
import logging
import time

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


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


class HTTPAdapterWithTimeout(HTTPAdapter):
    """HTTPAdapter with a default timeout

    This allows you to set a default timeout when creating the adapter.
    It can be overridden here as well as when doing individual
    requests.

    :arg varies default_timeout: number of seconds before timing out

        This can be a float or a (connect timeout, read timeout) tuple
        of floats.

        Defaults to 5.0 seconds.

    """

    def __init__(self, *args, **kwargs):
        self._default_timeout = kwargs.pop("default_timeout", 5.0)
        super().__init__(*args, **kwargs)

    def send(self, *args, **kwargs):
        # If there's a timeout, use that. Otherwise, use the default.
        kwargs["timeout"] = kwargs.get("timeout") or self._default_timeout
        return super().send(*args, **kwargs)


def session_with_retries(
    total_retries=5,
    backoff_factor=0.1,
    status_forcelist=(429, 500, 502, 504),
    default_timeout=3.0,
):
    """Returns session that retries on retryable HTTP errors with default timeout

    :arg int total_retries: total number of times to retry

    :arg float backoff_factor: number of seconds to apply between attempts

        The sleep amount is calculated like this::

            sleep = backoff_factor * (2 ** (num_retries - 1))

        For example, backoff_factor 0.1 will back off :

        * 0.1
        * 0.2
        * 0.4
        * 0.8
        * 1.6 ...

    :arg tuple of HTTP codes status_forcelist: tuple of HTTP codes to
        retry on

    :arg varies default_timeout: number of seconds before timing out

        This can be a float or a (connect timeout, read timeout) tuple
        of floats.

    :returns: a requests Session instance

    """
    retries = Retry(
        total=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=list(status_forcelist),
    )

    session = requests.Session()

    # Set the User-Agent header so we can distinguish our stuff from other stuff
    session.headers.update(
        {
            "User-Agent": "socorro-stats <https://github.com/willkg/socorro-stats>",
        }
    )

    adapter = HTTPAdapterWithTimeout(
        max_retries=retries, default_timeout=default_timeout
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def fetch_data(start_date, end_date):
    default_params = {
        "date": [f">={start_date}", f"<{end_date}"],
        "_results_number": "0",
    }

    session = session_with_retries()

    # Get a facet of products and counts for yesterday
    resp = session.get(
        API_URL,
        params=dict(
            _facets="product",
            **default_params,
        ),
    )

    resp.raise_for_status()
    resp_data = resp.json()
    print(resp_data)
    return resp_data


def update_data(today_dt):
    end_date = today_dt.strftime("%Y-%m-%d")
    start_date = (today_dt - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    data_start_date = (today_dt - datetime.timedelta(days=1)).strftime("%m-%d-%Y")

    resp_data = fetch_data(start_date, end_date)

    if resp_data["errors"]:
        return

    # Generate record
    data_item = {
        "date": data_start_date,
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


def rebuild_data():
    """Use for rebuilding the data for the last 180 days"""
    for i in range(180):
        today_dt = datetime.datetime.today() - datetime.timedelta(days=i)
        update_data(today_dt)
        if i % 20 == 0:
            time.sleep(30)


today_dt = datetime.datetime.today()
update_data(today_dt)
