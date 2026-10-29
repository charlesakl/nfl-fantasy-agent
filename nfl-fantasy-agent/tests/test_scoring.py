from nfl_agent.scoring import ppr_points


def test_receiver():
    assert ppr_points({'receptions': 6, 'receiving_yards': 80, 'receiving_tds': 1}) == 20.0


def test_quarterback():
    assert ppr_points({'passing_yards': 250, 'passing_tds': 2, 'interceptions': 1}) == 16.0


def test_empty():
    assert ppr_points({}) == 0.0
