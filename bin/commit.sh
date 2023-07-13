#!/bin/bash
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Usage: commit.sh
#
# Commits and pushes any changes in the workspace.

TIMESTAMP=$(date -u)

# Create a commit if there's anything to commit
echo ">>> adding changes (if any)..."
git config user.name "Automated"
git config user.email "actions@users.noreply.github.com"
git add -A

echo ">>> committing..."
git commit -m "Update data: ${TIMESTAMP}" || (echo ">>> nothing to commit"; exit 0)

# Push changes
echo ">>> pushing changes..."
git push
