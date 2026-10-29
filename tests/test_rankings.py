import pandas as pd
from nfl_agent.rankings import build_rankings, save_snapshot, load_previous

def test_rankings_and_movement(tmp_path):
    df=pd.DataFrame([
        dict(player_id='a',player_name='Alpha',position='RB',week=1,receptions=5,receiving_yards=50),
        dict(player_id='b',player_name='Beta',position='RB',week=1,receptions=1,receiving_yards=10),
        dict(player_id='a',player_name='Alpha',position='RB',week=2,receptions=6,receiving_yards=60),
        dict(player_id='b',player_name='Beta',position='RB',week=2,receptions=2,receiving_yards=20),
    ])
    r=build_rankings(df,2,prior={'RB:a':2,'RB:b':1})
    assert list(r.player_id)==['a','b']
    assert list(r.movement_label)==['↑ 1','↓ 1']
    path=tmp_path/'snapshot.json'
    save_snapshot(r,path)
    assert load_previous(path)['RB:a']==1

def test_missing_columns():
    try: build_rankings(pd.DataFrame({'week':[1]}),1)
    except ValueError: pass
    else: assert False

def test_empty_data():
    df=pd.DataFrame(columns=['player_id','player_name','position','week'])
    assert build_rankings(df,8).empty
