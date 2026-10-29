"""Phase 1: reliable, factual scoreboard snapshot; no invented analysis."""
from datetime import datetime, timezone
from .espn import games_last_24h


def build_snapshot() -> dict:
    now = datetime.now(timezone.utc)
    return {
        'generated_at_utc': now.isoformat(),
        'window_hours': 24,
        'scoring': 'full_ppr_4pt_pass_td',
        'games': games_last_24h(now),
        'notes': [
            'Game inclusion currently uses scheduled kickoff time, not confirmed final-whistle time.',
            'Player stats, injuries, projections, depth charts, trades and rankings are not yet implemented.',
            'An empty game list means no qualifying final games were found, not that no NFL news occurred.',
        ],
    }
