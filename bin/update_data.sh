#!/bin/bash
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Usage: update_data.sh
#
# Sets up a Python venv, installs requirements, and then runs update data.

if [ ! -d ".venv" ];
then
  echo ">>> venv does not exist; creating..."
  python -m venv .venv
fi
echo ">>> updating requirements in venv..."
.venv/bin/pip install -r requirements.txt
echo ">>> updating data..."
.venv/bin/python bin/update_data.py socorro_stats.json
