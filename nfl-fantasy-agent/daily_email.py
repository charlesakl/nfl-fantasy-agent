"""Run once in GitHub Actions or locally; no emails are sent unless --send is used."""
import argparse
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from nfl_agent.player_data import fetch_weekly_stats, latest_available_week
from nfl_agent.rankings import build_rankings, load_previous, save_snapshot
from nfl_agent.trade_signals import build_watchlists
from nfl_agent.email_delivery import html_report, send_brevo

def main():
    load_dotenv()
    parser=argparse.ArgumentParser()
    parser.add_argument('--send',action='store_true',help='Actually send through Brevo')
    parser.add_argument('--test',action='store_true',help='Send short connectivity test only (requires --send)')
    parser.add_argument('--season',type=int,default=None)
    parser.add_argument('--snapshot',default='data/ranking_snapshot.json')
    args=parser.parse_args()
    now=datetime.now(ZoneInfo('America/New_York'))
    if args.test:
        html='<h1>🏈 NFL Fantasy AI Agent</h1><p>Brevo test successful. This is a connectivity test, not a fantasy report.</p>'
        if args.send: print('Brevo response:',send_brevo('🏈 NFL Fantasy Agent — Email Test',html))
        else: print('Dry-run test: add --send to deliver')
        return
    season=args.season or now.year
    stats=fetch_weekly_stats(season)
    week=latest_available_week(stats)
    if week is None: raise RuntimeError('No published regular-season weekly data available; no email sent')
    snapshot=Path(args.snapshot)
    rankings=build_rankings(stats,week,prior=load_previous(snapshot))
    if rankings.empty: raise RuntimeError('No rankings generated; no email sent')
    watchlists=build_watchlists(rankings)
    if os.getenv('OPENAI_API_KEY'):
        from nfl_agent.ai_analysis import analyze_with_openai
        summary=analyze_with_openai(rankings)
    else:
        summary='Latest published weekly stats have been processed. This version does not independently verify injuries, trades or depth charts.'
    html=html_report('NFL Fantasy Intelligence',summary,rankings,watchlists,week,season)
    Path('data').mkdir(exist_ok=True)
    Path('data/latest_report.html').write_text(html,encoding='utf8')
    print(f'Generated report for season {season} week {week}; {len(rankings)} ranked players, {len(watchlists)} statistical watchlist entries')
    if args.send:
        result=send_brevo(f'🏈 NFL Fantasy Intelligence — {now:%b %d, %Y}',html)
        print('Brevo response:',result)
        save_snapshot(rankings,snapshot)
    else:
        print('DRY RUN — no email sent; preview saved to data/latest_report.html')

if __name__=='__main__': main()
