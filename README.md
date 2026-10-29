# Mr. Jason Akl — NFL Fantasy Intelligence (Phase 2.1 + Phase 3 preview)

## What is included
- Season-specific nflverse weekly player stats (2026 and other seasons, if published)
- Automatic detection of latest available regular-season week
- Clean full player names and nflverse passing-interception mapping
- Full-PPR baseline ROS rankings for QB, RB, WR and TE (top 50 each where available)
- Previous ranking snapshot comparison and CSV downloads
- Form-based buy-low and sell-high *watchlists* (10 per position when enough eligible players exist)
- Optional OpenAI narrative using computed stats and manually supplied news notes

**Not yet included:** automated injury/trade/depth-chart feeds, market-based trade valuations, schedule/bye-adjusted ROS projections, Brevo emails, GitHub Actions delivery. The AI cannot verify news automatically. Week 18 is included in the simple remaining-week projection. Do not interpret it as an accurate games-remaining forecast.

## Windows setup
```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

For optional AI commentary, copy `.env.example` to `.env`, add your own OpenAI API key locally, and never commit `.env` to GitHub. OpenAI API usage is billed separately. Ranking and watchlist calculations work without an API key.

The app saves baselines locally under `data/`. For daily cloud automation, persistent snapshots will be needed.
