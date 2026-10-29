import pandas as pd
from nfl_agent.player_data import normalize_weekly_stats, latest_available_week
from nfl_agent.rankings import build_rankings
from nfl_agent.trade_signals import build_watchlists

def test_name_and_week():
    raw=pd.DataFrame([dict(season=2026,week=7,season_type='REG',player_id='a',player_name='J.Maye',player_display_name='Drake Maye',position='QB',team='NE',passing_yards=300,passing_tds=2,passing_interceptions=1)])
    df=normalize_weekly_stats(raw,2026)
    assert df.iloc[0]['player_name']=='Drake Maye'
    assert latest_available_week(df)==7
    ranks=build_rankings(df,7)
    assert ranks.iloc[0]['player_name']=='Drake Maye'
    assert ranks.iloc[0]['avg_ppr']==18.0

def test_trade_watchlist():
    rows=[]
    for week, yards in [(1,100),(2,120),(3,80),(4,40)]:
        rows.append(dict(player_id='a',player_name='Runner A',position='RB',team='ABC',week=week,rushing_yards=yards))
    ranked=build_rankings(pd.DataFrame(rows),4)
    result=build_watchlists(ranked)
    assert not result.empty
