#!/usr/bin/env python3
"""Baut feed.xml und index.html für den Podcast DailyPri.

Aufruf: python3 feed_bauen.py <ordner> [--heute JJJJ-MM-TT] [--tage 7]

Im <ordner> liegen die Folgen als JJJJ-MM-TT.mp3. Folgen, die älter als
--tage Tage sind (heute mitgezählt), werden gelöscht. Nur Standardbibliothek.
"""
import argparse
import datetime as dt
import html
import os
import re
import sys
from email.utils import format_datetime
from zoneinfo import ZoneInfo

BASIS_URL = "https://apri69.github.io/DailyPri"
TITEL = "DailyPri"
BESCHREIBUNG = "Tägliches Morgen-Briefing zu Euro-Anleihen, EZB und Makro – nur öffentliche Quellen."
BERLIN = ZoneInfo("Europe/Berlin")
FOLGE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.mp3$")


def folgen(ordner):
    """Liefert [(datum, dateiname)] neueste zuerst."""
    gefunden = []
    for name in os.listdir(ordner):
        treffer = FOLGE.match(name)
        if treffer:
            gefunden.append((dt.date.fromisoformat(treffer.group(1)), name))
    return sorted(gefunden, reverse=True)


def aufraeumen(ordner, heute, tage):
    grenze = heute - dt.timedelta(days=tage - 1)
    geloescht = []
    for datum, name in folgen(ordner):
        if datum < grenze:
            os.remove(os.path.join(ordner, name))
            geloescht.append(name)
    return geloescht


def feed(ordner):
    items = []
    for datum, name in folgen(ordner):
        groesse = os.path.getsize(os.path.join(ordner, name))
        # 6:00 Uhr Berliner Zeit als Erscheinungszeit
        zeit = dt.datetime.combine(datum, dt.time(6, 0), tzinfo=BERLIN)
        url = f"{BASIS_URL}/{name}"
        items.append(f"""    <item>
      <title>{TITEL} – {datum.strftime('%d.%m.%Y')}</title>
      <enclosure url="{url}" length="{groesse}" type="audio/mpeg"/>
      <guid isPermaLink="false">dailypri-{datum.isoformat()}</guid>
      <pubDate>{format_datetime(zeit)}</pubDate>
      <itunes:explicit>false</itunes:explicit>
    </item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>{TITEL}</title>
    <link>{BASIS_URL}/</link>
    <description>{html.escape(BESCHREIBUNG)}</description>
    <language>de</language>
    <itunes:author>André Prietzel</itunes:author>
    <itunes:image href="{BASIS_URL}/cover.png"/>
    <itunes:category text="Business"/>
    <itunes:explicit>false</itunes:explicit>
    <itunes:block>Yes</itunes:block>
{chr(10).join(items)}
  </channel>
</rss>
"""


def seite(ordner):
    zeilen = []
    for datum, name in folgen(ordner):
        zeilen.append(f"""  <li><b>{datum.strftime('%d.%m.%Y')}</b><br>
    <audio controls preload="none" src="{name}"></audio></li>""")
    liste = "\n".join(zeilen) or "  <li>Noch keine Folge.</li>"
    feed_ohne_https = BASIS_URL.removeprefix("https://")
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{TITEL}</title>
<style>
  body {{ font-family: -apple-system, system-ui, sans-serif; max-width: 34rem; margin: 2rem auto; padding: 0 16px; }}
  img {{ width: 8rem; border-radius: 12px; }}
  li {{ margin: 1rem 0; list-style: none; }}
  ul {{ padding: 0; }}
  audio {{ width: 100%; }}
  a.knopf {{ display: inline-block; padding: .6rem 1rem; background: #7a3cff; color: #fff; border-radius: 8px; text-decoration: none; }}
</style>
</head>
<body>
<img src="cover.png" alt="">
<h1>{TITEL}</h1>
<p>{html.escape(BESCHREIBUNG)}</p>
<p><a class="knopf" href="podcast://{feed_ohne_https}/feed.xml">In Apple Podcasts abonnieren</a></p>
<p><small>Feed-Adresse: {BASIS_URL}/feed.xml</small></p>
<h2>Folgen (letzte 7 Tage)</h2>
<ul>
{liste}
</ul>
</body>
</html>
"""


def main():
    teil = argparse.ArgumentParser()
    teil.add_argument("ordner")
    teil.add_argument("--heute", type=dt.date.fromisoformat,
                      default=dt.datetime.now(BERLIN).date())
    teil.add_argument("--tage", type=int, default=7)
    args = teil.parse_args()

    geloescht = aufraeumen(args.ordner, args.heute, args.tage)
    with open(os.path.join(args.ordner, "feed.xml"), "w", encoding="utf-8") as f:
        f.write(feed(args.ordner))
    with open(os.path.join(args.ordner, "index.html"), "w", encoding="utf-8") as f:
        f.write(seite(args.ordner))
    print(f"Folgen im Feed: {len(folgen(args.ordner))}, gelöscht: {len(geloescht)} {geloescht}")


if __name__ == "__main__":
    sys.exit(main())
