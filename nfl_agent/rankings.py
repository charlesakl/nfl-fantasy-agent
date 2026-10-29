"""Transparent *model estimates*, not expert consensus or injury-adjusted projections."""
from datetime import datetime, timezone
from pathlib import Path
import json
import pandas as pd
from .scoring import ppr_points

POSITIONS = ('QB', 'RB', 'WR', 'TE')
STAT_COLUMNS = ('passing_yards','passing_tds','passing_interceptions','interceptions','rushing_yards','rushing_tds','receiving_yards','receiving_tds','receptions','fumbles_lost','two_point_conversions')
REQUIRED = ('player_id','player_name','position','week')

def build_rankings(weekly: pd.DataFrame, current_week: int, season_end_week: int = 18, prior: dict | None = None) -> pd.DataFrame:
    """Estimate remaining regular-season PPR using recent form and season average.

    Inputs must be verified weekly player stats. This is a baseline, not a
    matchup-, bye-, injury- or trade-adjusted forecast. Week 18 is included.
    """
    missing = set(REQUIRED) - set(weekly.columns)
    if missing: raise ValueError(f'Missing required columns: {sorted(missing)}')
    if not 1 <= current_week <= season_end_week <= 18: raise ValueError('Invalid current/end week')
    df = weekly.copy()
    df['position'] = df['position'].astype(str).str.upper()
    df = df[df['position'].isin(POSITIONS)].copy()
    df['week'] = pd.to_numeric(df['week'], errors='coerce')
    df = df[(df['week'] >= 1) & (df['week'] <= current_week)]
    for c in STAT_COLUMNS:
        if c not in df: df[c] = 0
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    if df.empty: return pd.DataFrame(columns=['position','rank','player_name','player_id','team','games','avg_ppr','recent_avg_ppr','ros_ppr','previous_rank','movement','movement_label'])
    # nflverse uses passing_interceptions; the scoring engine uses interceptions.
    if 'passing_interceptions' in weekly.columns:
        df['interceptions'] = df['passing_interceptions']
    df['ppr'] = df.apply(lambda row: ppr_points(row.to_dict()), axis=1)
    if 'team' not in df: df['team'] = ''
    if 'player_display_name' in df.columns:
        df['player_name'] = df['player_display_name'].fillna(df['player_name'])
    df = df.sort_values('week')
    records=[]
    for (position,pid), group in df.groupby(['position','player_id'],sort=False):
        # One observation per played game. Missing games are not counted as zero.
        group = group.drop_duplicates('week',keep='last')
        avg=float(group['ppr'].mean()); recent=float(group.tail(3)['ppr'].mean())
        estimate=round((.6*recent+.4*avg)*max(0,season_end_week-current_week),1)
        records.append(dict(position=position,player_id=str(pid),player_name=str(group.iloc[-1]['player_name']),team=str(group.iloc[-1]['team']),games=len(group),avg_ppr=round(avg,1),recent_avg_ppr=round(recent,1),ros_ppr=estimate))
    result=pd.DataFrame(records).sort_values(['position','ros_ppr','player_name'],ascending=[True,False,True]).copy()
    result['rank']=result.groupby('position').cumcount()+1
    prior=prior or {}
    result['previous_rank']=result.apply(lambda r: prior.get(f"{r['position']}:{r['player_id']}"),axis=1)
    result['movement']=result.apply(lambda r: int(r['previous_rank']-r['rank']) if pd.notna(r['previous_rank']) else None,axis=1)
    result['movement_label']=result['movement'].apply(lambda n: 'NEW' if pd.isna(n) else ('—' if n==0 else f'↑ {n}' if n>0 else f'↓ {abs(n)}'))
    return result[result['rank']<=50].reset_index(drop=True)

def load_previous(path: Path) -> dict:
    if not path.exists(): return {}
    return json.loads(path.read_text(encoding='utf8')).get('ranks',{})

def save_snapshot(rankings: pd.DataFrame, path: Path, asof: str | None = None):
    path.parent.mkdir(parents=True,exist_ok=True)
    ranks={f"{r.position}:{r.player_id}":int(r.rank) for r in rankings.itertuples()}
    payload={'asof':asof or datetime.now(timezone.utc).isoformat(),'ranks':ranks}
    path.write_text(json.dumps(payload,indent=2),encoding='utf8')
