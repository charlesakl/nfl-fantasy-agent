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


## Daily Brevo email automation

This edition adds `daily_email.py`, `nfl_agent/email_delivery.py`, and `.github/workflows/daily-email.yml`.

GitHub Actions repository secrets: `BREVO_API_KEY`, `BREVO_SENDER_EMAIL`, `BREVO_SENDER_NAME`, `REPORT_RECIPIENT_EMAILS` (comma-separated), optionally `OPENAI_API_KEY` and `OPENAI_MODEL`. Use a **Brevo v3 API key**, not the SMTP password.

To test without sending: `python daily_email.py --test`. To send a short test: `python daily_email.py --test --send`. To preview a report without sending: `python daily_email.py`. To send a real report: `python daily_email.py --send`.

In GitHub > Actions > NFL Fantasy Daily Email > Run workflow, choose **test** first. Only after successful test choose **report**. The schedule uses 10:00/11:00 UTC with an Eastern-time guard; GitHub scheduling is best-effort and can be late.

**Limitations:** The report contains model-derived statistical estimates and form-based watchlists, not verified injury/transaction news. Ranking movement history is not persistent across GitHub Actions runs because snapshots are not committed to a durable store; a future phase should add persistent storage. A generated report is uploaded as an Actions artifact. GitHub Actions secrets do not automatically propagate to Streamlit Cloud.
