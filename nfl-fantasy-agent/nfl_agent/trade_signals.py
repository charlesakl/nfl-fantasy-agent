"""Heuristic watchlists, NOT actual market-based trade valuations."""
import pandas as pd

def build_watchlists(rankings: pd.DataFrame, per_position: int = 10) -> pd.DataFrame:
    if rankings.empty:
        return pd.DataFrame()
    df = rankings.copy()
    df['form_gap'] = df['recent_avg_ppr'] - df['avg_ppr']
    # Positive gap: recent performance is stronger than historical average;
    # negative gap: recent performance is weaker. Neither proves trade value.
    rows = []
    for position in ('QB', 'RB', 'WR', 'TE'):
        group = df[(df['position'] == position) & (df['games'] >= 3)].copy()
        for action, ascending in [('Buy-low watch', True), ('Sell-high watch', False)]:
            subset = group.sort_values('form_gap', ascending=ascending).head(per_position).copy()
            subset['signal'] = action
            subset['reason'] = subset['form_gap'].map(lambda x: f'Recent 3-game average differs from season average by {x:+.1f} PPR/game; check usage, injuries and market price before trading.')
            rows.append(subset)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
