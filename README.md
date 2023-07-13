# socorro stats

Crash report stats over time.

* License: MPLv2
* Author: Will Kahn-Greene

Note: The number of crash reports isn't wildly meaningful. This is not helpful
for determining crash rates for Firefox or other Mozilla products. Crash
reports are throttled, removed, duplicated, omitted entirely, etc. Further, crash
reports are not sent by default, so in many cases, we never get a crash report.

This is helpful for historical metrics for crash ingestion. For example, this
would let us see changes in crash ingestion numbers over time. Maybe we can
reduce or boost infrastructure. Our existing metrics systems only go back 6
months, so this would allow us to see further into the past.

This is all very prototype-y and hand-waving and alpha-quality at best.

In table form: https://flatgithub.com/willkg/socorro-stats
