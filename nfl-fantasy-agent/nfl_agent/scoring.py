"""Standard full-PPR fantasy scoring, with configurable scoring assumptions."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Scoring:
    passing_yards: float = 0.04
    passing_tds: float = 4.0
    interceptions: float = -2.0
    rushing_yards: float = 0.1
    receiving_yards: float = 0.1
    rushing_tds: float = 6.0
    receiving_tds: float = 6.0
    receptions: float = 1.0
    fumbles_lost: float = -2.0
    two_point_conversions: float = 2.0


def ppr_points(stats: dict, rules: Scoring = Scoring()) -> float:
    """Calculate offensive fantasy points. Missing fields count as zero."""
    weights = {
        'passing_yards': rules.passing_yards,
        'passing_tds': rules.passing_tds,
        'interceptions': rules.interceptions,
        'rushing_yards': rules.rushing_yards,
        'receiving_yards': rules.receiving_yards,
        'rushing_tds': rules.rushing_tds,
        'receiving_tds': rules.receiving_tds,
        'receptions': rules.receptions,
        'fumbles_lost': rules.fumbles_lost,
        'two_point_conversions': rules.two_point_conversions,
    }
    return round(sum(float(stats.get(k) or 0) * w for k, w in weights.items()), 2)
