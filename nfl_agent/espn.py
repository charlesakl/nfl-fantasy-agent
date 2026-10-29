"""ESPN public scoreboard adapter. Unofficial endpoint; availability may change."""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import requests

URL = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard'


def games_last_24h(now: datetime | None = None) -> list[dict]:
    """Return games whose final status became available in the last 24h.

    ESPN's public scoreboard does not consistently expose the exact final-whistle
    timestamp. We therefore include completed games with scheduled kickoff inside
    the window and flag this limitation in the output. Overnight games that began
    before the window may be missed; a later adapter should use official end times.
    """
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError('now must be timezone-aware')
    now = now.astimezone(timezone.utc)
    start = now - timedelta(hours=24)
    local = ZoneInfo('America/New_York')
    days = {start.astimezone(local).strftime('%Y%m%d'), now.astimezone(local).strftime('%Y%m%d')}
    seen = {}
    with requests.Session() as session:
        for day in sorted(days):
            response = session.get(URL, params={'dates': day, 'limit': 100}, timeout=20)
            response.raise_for_status()
            for event in response.json().get('events', []):
                kickoff = datetime.fromisoformat(event['date'].replace('Z', '+00:00'))
                if not (start <= kickoff <= now):
                    continue
                comp = (event.get('competitions') or [{}])[0]
                status = comp.get('status') or event.get('status') or {}
                if not status.get('type', {}).get('completed', False):
                    continue
                teams = comp.get('competitors', [])
                seen[event['id']] = {
                    'id': event['id'],
                    'name': event.get('name'),
                    'kickoff_utc': kickoff.isoformat(),
                    'status': 'final',
                    'teams': [{'name': t.get('team', {}).get('displayName'), 'home_away': t.get('homeAway'), 'score': t.get('score')} for t in teams],
                    'window_basis': 'scheduled_kickoff_not_final_whistle',
                }
    return sorted(seen.values(), key=lambda e: e['kickoff_utc'])
