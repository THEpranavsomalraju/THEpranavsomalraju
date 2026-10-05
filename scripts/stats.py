"""Builds stats.svg: total contributions, total commits and commits in the last 30 days, from GitHub's GraphQL API."""
from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone

USER = "THEpranavsomalraju"
NAME = "Pranav Somalraju"
TOKEN = os.environ["GITHUB_TOKEN"]


def gql(query: str) -> dict:
    req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": query}).encode(),
                                 headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)["data"]["user"]


def window(start: str, end: str | None = None) -> dict:
    to = f', to: "{end}"' if end else ""
    return gql(f'{{ user(login: "{USER}") {{ contributionsCollection(from: "{start}"{to}) '
               '{ totalCommitContributions contributionCalendar { totalContributions } } } }')["contributionsCollection"]


years = gql(f'{{ user(login: "{USER}") {{ contributionsCollection {{ contributionYears }} }} }}')["contributionsCollection"]["contributionYears"]
contributions = commits = 0
for y in years:
    c = window(f"{y}-01-01T00:00:00Z", f"{y}-12-31T23:59:59Z")
    contributions += c["contributionCalendar"]["totalContributions"]
    commits += c["totalCommitContributions"]
since = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
recent = window(since)["totalCommitContributions"]

ICONS = {
    "contrib": "M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9zm10.5-1V9h-8c-.356 0-.694.074-1 .208V2.5a1 1 0 011-1h8zM5 12.25v3.25a.25.25 0 00.4.2l1.45-1.087a.25.25 0 01.3 0L8.6 15.7a.25.25 0 00.4-.2v-3.25a.25.25 0 00-.25-.25h-3.5a.25.25 0 00-.25.25z",
    "commits": "M1.643 3.143L.427 1.927A.25.25 0 000 2.104V5.75c0 .138.112.25.25.25h3.646a.25.25 0 00.177-.427L2.715 4.215a6.5 6.5 0 11-1.18 4.458.75.75 0 10-1.493.154 8.001 8.001 0 101.6-5.684zM7.75 4a.75.75 0 01.75.75v2.992l2.028.812a.75.75 0 01-.557 1.392l-2.5-1A.75.75 0 017 8.25v-3.5A.75.75 0 017.75 4z",
    "recent": "M11.93 8.5a4.002 4.002 0 0 1-7.86 0H.75a.75.75 0 0 1 0-1.5h3.32a4.002 4.002 0 0 1 7.86 0h3.32a.75.75 0 0 1 0 1.5Zm-1.43-.75a2.5 2.5 0 1 0-5 0 2.5 2.5 0 0 0 5 0Z",
}
prs = gql(f'{{ user(login: "{USER}") {{ pullRequests {{ totalCount }} }} }}')["pullRequests"]["totalCount"]
since_year = gql(f'{{ user(login: "{USER}") {{ createdAt }} }}')["createdAt"][:4]

rows = [("commits", "Total Commits", commits), ("recent", "Commits (last 30 days)", recent), ("pr", "Pull Requests", prs)]
ICONS["pr"] = ("M7.177 3.073L9.573.677A.25.25 0 0110 .854v4.792a.25.25 0 01-.427.177L7.177 3.427a.25.25 0 010-.354zM3.75 2.5a.75.75 0 100 1.5.75.75 0 000-1.5zm-2.25.75a2.25 2.25 0 113 2.122v5.256a2.251 2.251 0 11-1.5 0V5.372A2.25 2.25 0 011.5 3.25zM11 2.5h-1V4h1a1 1 0 011 1v5.628a2.251 2.251 0 101.5 0V5A2.5 2.5 0 0011 2.5zm1 10.25a.75.75 0 111.5 0 .75.75 0 01-1.5 0zM3.75 12a.75.75 0 100 1.5.75.75 0 000-1.5z")
W, H = 760, 230
CX, CY, R = 610, 101, 62
body = "".join(
    f'<g transform="translate(48,{69 + i * 52})"><svg x="0" y="-19" width="22" height="22" viewBox="0 0 16 16">'
    f'<path fill="#1F6FEB" fill-rule="evenodd" d="{ICONS[k]}"/></svg>'
    f'<text class="stat" x="36" y="0">{label}</text><text class="value" x="400" y="0" text-anchor="end">{value:,}</text></g>'
    for i, (k, label, value) in enumerate(rows))
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
.header {{ font: 600 24px 'Segoe UI', Ubuntu, Sans-Serif; fill: #58A6FF; }}
.stat {{ font: 600 19px 'Segoe UI', Ubuntu, "Helvetica Neue", Sans-Serif; fill: #C3D1D9; }}
.value {{ font: 700 19px 'Segoe UI', Ubuntu, "Helvetica Neue", Sans-Serif; fill: #C3D1D9; }}
.big {{ font: 700 34px 'Segoe UI', Ubuntu, Sans-Serif; fill: #F0F6FC; }}
.label {{ font: 600 15px 'Segoe UI', Ubuntu, Sans-Serif; fill: #F0F6FC; }}
.sub {{ font: 400 13px 'Segoe UI', Ubuntu, Sans-Serif; fill: #8B949E; }}
</style>
<rect x="0.5" y="0.5" rx="10" width="{W - 1}" height="{H - 1}" fill="#0D1117" stroke="#30363D"/>
{body}
<line x1="470" y1="36" x2="470" y2="{H - 36}" stroke="#30363D" stroke-width="1"/>
<circle cx="{CX}" cy="{CY - 12}" r="{R}" fill="none" stroke="#1F6FEB" stroke-width="6"/>
<text class="big" x="{CX}" y="{CY - 1}" text-anchor="middle">{contributions:,}</text>
<text class="label" x="{CX}" y="{CY + 78}" text-anchor="middle">Total Contributions</text>
<text class="sub" x="{CX}" y="{CY + 98}" text-anchor="middle">since {since_year}</text>
</svg>
'''
open("stats-card.svg", "w").write(svg)
print(contributions, commits, recent, prs)
