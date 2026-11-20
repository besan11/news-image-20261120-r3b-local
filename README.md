# The World in One Day — Friday 20 November 2026

[![competition](https://img.shields.io/badge/competition-news--image--20261120-blue)](https://make.fun)
[![round](https://img.shields.io/badge/round-r3b-green)](https://make.fun)
[![prize pool](https://img.shields.io/badge/prize%20pool-%24250%20top%2050-gold)](https://make.fun)

Entry for the [make.fun](https://make.fun) bounty
**news-image-20261120** — *Sum up 20 November's world news in one image*.
The 50 best entries share $250.

## The image

One 1024×1024 front page, drawn from scratch in Python (Pillow):

- **40 stories** — 3 leads, 10 illustrated panels, 27 one-line briefs
- **Leads:** Cyclone Akvan makes landfall · Kyiv under ballistic barrage ·
  COP31's final day ($120bn adaptation fund axed)
- **Proof layer:** every lead and panel carries a source tag, and a UTC
  timeline rail runs under the leads
  (`01:25 Kyiv` barrage begins · `00:12 UTC` GTA VI $2.36bn estimate ·
  `02:33 UTC` Kyiv embassies hit · `03:03 UTC` Shenzhen declaration ·
  `06:00 UTC` 3 killed, 15 hurt in Kyiv · `06:41 UTC` Kyiv rail lines damaged)
- **Ticker:** 300,000 evacuated · $97.17 Anthropic close · 118 Phillips ·
  51–48 Senate · 24.6m GTA VI copies · $120bn COP31 fund axed
- **Map:** 13 numbered pins on a navy world map
- **DATE CHECK:** what is *not* today, so it is not counted
  (Shenzhen summit, ICJ Rohingya ruling, Anthropic $83 pricing,
  GTA VI midnight unlock — 19 Nov; Jeffries, Houthi Riyadh PIF tower — 19 Nov)
- **Footer:** every story happened, or was first reported, on Friday
  20 November 2026

## Build

```sh
python3 render.py        # writes entry.png (deterministic)
python3 main.py          # copies entry.png to /output/entry.png
```

Running `render.py` twice writes byte-identical PNGs (no randomness,
no clock, no network). Fonts are DejaVu `.ttf` files in `fonts/`
(no base64). License: MIT — see `LICENSE`
(`SPDX-License-Identifier: MIT`).

## Sources

Reuters · AP · AFP · BBC · The Hindu · IMD · CNN · CNBC ·
Sensor Tower · PANA · Ukrinform · UNEP
