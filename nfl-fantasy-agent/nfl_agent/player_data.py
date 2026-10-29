"""Season-specific nflverse weekly player statistics."""
from io import BytesIO
import requests
import pandas as pd

URL_TEMPLATE = "https://github.com/nflverse/nflverse-data/releases/download/stats_player/stats_player_week_{season}.csv"

def normalize_weekly_stats(raw: pd.DataFrame, season: int) -> pd.DataFrame:
    df = raw.copy()
    if 'season' not in df.columns:
        raise ValueError('Missing season column')
    df = df[pd.to_numeric(df['season'], errors='coerce') == season].copy()
    if 'season_type' in df.columns:
        df = df[df['season_type'].astype(str).str.upper() == 'REG'].copy()
    if 'player_display_name' in df.columns:
        # Prefer full display name; do not rename into an existing player_name column.
        df['player_name'] = df['player_display_name'].fillna(df.get('player_name', pd.Series(index=df.index, dtype='object')))
    elif 'player_name' not in df.columns:
        raise ValueError('Missing player name')
    if 'team' not in df.columns and 'recent_team' in df.columns:
        df['team'] = df['recent_team']
    required = {'player_id', 'player_name', 'position', 'week'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f'Missing nflverse columns: {sorted(missing)}')
    df['week'] = pd.to_numeric(df['week'], errors='coerce')
    df = df.dropna(subset=['week', 'player_id', 'player_name'])
    return df

def fetch_weekly_stats(season: int) -> pd.DataFrame:
    url = URL_TEMPLATE.format(season=int(season))
    response = requests.get(url, timeout=60, headers={'User-Agent': 'JasonFantasyAgent/0.3'})
    response.raise_for_status()
    raw = pd.read_csv(BytesIO(response.content), low_memory=False)
    return normalize_weekly_stats(raw, season)

def latest_available_week(df: pd.DataFrame) -> int | None:
    weeks = pd.to_numeric(df.get('week', pd.Series(dtype='float64')), errors='coerce').dropna()
    return int(weeks.max()) if not weeks.empty else None
