"""Optional OpenAI commentary using explicitly supplied evidence only."""
import os

def analyze_with_openai(rankings, news_text: str = '') -> str:
    from openai import OpenAI
    if not os.getenv('OPENAI_API_KEY'):
        raise RuntimeError('OPENAI_API_KEY is not configured. Add it to your local .env file.')
    # Do not claim to have independently checked live injuries, trades or depth charts.
    top = rankings.groupby('position', sort=False).head(10)
    payload = top[['position','rank','player_name','team','avg_ppr','recent_avg_ppr','ros_ppr']].to_csv(index=False)
    prompt = f"""Write a concise fantasy football briefing addressed to Mr. Jason Akl.
Only use the statistics and source notes below. Never invent injuries, transactions,
matchups, projections or player news. If news notes are empty, explicitly say live
injury/trade/depth-chart news was not checked. Explain these are experimental ROS
estimates, not consensus rankings. Distinguish observed form from trade market value.

Top-10 per-position statistical rankings:
{payload}

User-provided news notes (unverified unless user has checked sources):
{news_text or '(none)'}"""
    client = OpenAI()
    response = client.responses.create(model=os.getenv('OPENAI_MODEL','gpt-4.1-mini'), input=prompt, max_output_tokens=1600)
    return response.output_text
