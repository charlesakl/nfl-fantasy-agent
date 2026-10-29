from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from nfl_agent.report import build_snapshot
from nfl_agent.player_data import fetch_weekly_stats, normalize_weekly_stats, latest_available_week
from nfl_agent.trade_signals import build_watchlists
from nfl_agent.ai_analysis import analyze_with_openai
from dotenv import load_dotenv
load_dotenv()
from nfl_agent.rankings import build_rankings, load_previous, save_snapshot

st.set_page_config(page_title='Jason NFL Fantasy AI',page_icon='🏈',layout='wide')
st.title('🏈 Mr. Jason Akl — NFL Fantasy Intelligence')
st.caption('Phase 2.1 + Phase 3 preview · Full PPR · 4-point passing TD · Experimental projections')
score_tab, rankings_tab=st.tabs(['🏟️ NFL Scores','📈 Rest-of-Season Rankings'])
with score_tab:
    if st.button('Refresh last 24-hour game results'):
        try:
            snapshot=build_snapshot()
            st.success(f"Found {len(snapshot['games'])} completed games with kickoff in the last 24 hours")
            for game in snapshot['games']:
                st.subheader(game['name'])
                st.write(' | '.join(f"{t['name']}: {t['score']}" for t in game['teams']))
            if not snapshot['games']: st.info('No games in the 24-hour kickoff window. This is normal on off days.')
        except Exception as exc: st.error(f'Unable to retrieve scores: {exc}')
    st.caption('24-hour filter uses scheduled kickoff, not final whistle.')
with rankings_tab:
    st.warning('Rankings are experimental statistical estimates: they do NOT yet account for byes, injuries, matchups, trades, depth charts or consensus projections. No rankings are shown without real data.')
    year=datetime.now(ZoneInfo('America/New_York')).year
    season=st.number_input('NFL season',min_value=2020,max_value=year,value=year,step=1)
    st.caption('The latest published week will be detected automatically. Future weeks are never assumed to be available.')
    source=st.radio('Weekly stats source',['Download nflverse dataset','Upload CSV'],horizontal=True)
    uploaded=st.file_uploader('Upload weekly player stats CSV',type=['csv']) if source=='Upload CSV' else None
    if st.button('Calculate rankings'):
        try:
            if source=='Upload CSV':
                if uploaded is None: st.error('Please upload a CSV first.'); st.stop()
                weekly=pd.read_csv(uploaded)
                weekly=normalize_weekly_stats(weekly, int(season))
            else: weekly=fetch_weekly_stats(int(season))
            week=latest_available_week(weekly)
            if week is None: st.warning('No published regular-season player weeks found.'); st.stop()
            st.info(f'Latest available regular-season player statistics: Week {week} of {season}.')
            snapshot_path=Path('data')/f'ranks_{season}.json'
            previous=load_previous(snapshot_path)
            rankings=build_rankings(weekly,int(week),prior=previous)
            if rankings.empty: st.warning('No eligible player data found for that season and week.')
            else:
                st.session_state['rankings']=rankings
                st.session_state['snapshot_path']=str(snapshot_path)
                st.session_state['data_week']=week
                st.session_state['data_season']=int(season)
                st.success(f'Calculated {len(rankings)} rankings from actual weekly stats.')
        except Exception as exc: st.error(f'Unable to calculate rankings: {exc}')
    if 'rankings' in st.session_state:
        rankings=st.session_state['rankings']
        st.caption(f"Data through Week {st.session_state.get('data_week', '?')} of {st.session_state.get('data_season', '?')}. Estimates exclude injury, bye and opponent adjustments.")
        tabs=st.tabs(['QB','RB','WR','TE'])
        for tab,pos in zip(tabs,['QB','RB','WR','TE']):
            with tab:
                subset=rankings[rankings['position']==pos]
                st.dataframe(subset[['rank','player_name','team','games','avg_ppr','recent_avg_ppr','ros_ppr','previous_rank','movement_label']],hide_index=True,use_container_width=True)
        st.download_button('Download rankings CSV',rankings.to_csv(index=False).encode(),'jason_ros_rankings.csv','text/csv')
        if st.button('Save rankings as baseline for next comparison'):
            save_snapshot(rankings,Path(st.session_state['snapshot_path']))
            st.success('Saved locally. Future rankings will compare against this snapshot.')
        st.caption('Rank movement compares against the last saved snapshot on this computer. GitHub Actions will need persistent storage in a later phase.')

        st.subheader('📊 Trade radar — statistical watchlist')
        st.warning('These are form-based WATCHLISTS, not validated buy-low/sell-high trade values. Market pricing, news and usage must be checked.')
        watch = build_watchlists(rankings)
        if not watch.empty:
            signal = st.selectbox('Watchlist', ['Buy-low watch', 'Sell-high watch'])
            st.dataframe(watch[watch['signal']==signal][['position','player_name','team','rank','avg_ppr','recent_avg_ppr','form_gap','reason']], hide_index=True, use_container_width=True)
            st.download_button('Download trade watchlists CSV', watch.to_csv(index=False).encode(), 'jason_trade_watchlists.csv', 'text/csv')
        st.subheader('🤖 Optional AI briefing')
        st.caption('OpenAI analyzes calculated statistics and notes you provide; it does not automatically retrieve live NFL news yet.')
        notes = st.text_area('Optional verified injury, trade, depth-chart and free-agency notes (include sources and dates)', height=100)
        if st.button('Generate AI briefing'):
            try:
                with st.spinner('Preparing briefing...'):
                    st.markdown(analyze_with_openai(rankings, notes))
            except Exception as exc:
                st.error(f'Unable to generate AI briefing: {exc}')
