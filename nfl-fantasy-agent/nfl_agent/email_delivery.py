"""Transactional email through Brevo. Never log API keys."""
import os
import re
import requests
from html import escape

EMAIL = re.compile(r"^[^\s@,;]+@[^\s@,;]+\.[^\s@,;]+$")

def recipient_list(value):
    addresses = [x.strip() for x in value.replace(';', ',').split(',') if x.strip()]
    if not addresses or any(not EMAIL.fullmatch(x) for x in addresses):
        raise ValueError('REPORT_RECIPIENT_EMAILS must contain valid comma-separated email addresses')
    return list(dict.fromkeys(addresses))

def html_report(title, summary, rankings, watchlists, week, season):
    def table(df, columns, labels):
        if df.empty: return '<p>No data available.</p>'
        header = ''.join(f'<th style="padding:7px;text-align:left;border-bottom:1px solid #ddd">{escape(x)}</th>' for x in labels)
        rows = []
        for _, row in df.iterrows():
            cells = ''.join(f'<td style="padding:7px;border-bottom:1px solid #eee">{escape(str(row[c]))}</td>' for c in columns)
            rows.append('<tr>'+cells+'</tr>')
        return '<table style="border-collapse:collapse;width:100%;font-size:13px"><tr>'+header+'</tr>'+''.join(rows)+'</table>'
    parts = [f'<h1>🏈 {escape(title)}</h1>',f'<p>Season {season}, through published week {week}. Full-PPR statistical estimates; not injury- or bye-adjusted.</p>', '<h2>Daily briefing</h2>', '<div style="white-space:pre-wrap">'+escape(summary)+'</div>']
    for pos in ('QB','RB','WR','TE'):
        subset=rankings[rankings.position==pos].head(50)
        parts.extend([f'<h2>{pos} — Top 50</h2>',table(subset,['rank','player_name','team','ros_ppr','movement_label'],['Rank','Player','Team','ROS PPR est.','Change'])])
        for signal in ('Buy-low watch','Sell-high watch'):
            choices=watchlists[(watchlists.position==pos)&(watchlists.signal==signal)].head(10) if not watchlists.empty else watchlists
            parts.extend([f'<h3>{pos}: {escape(signal)}</h3>',table(choices,['player_name','team','reason'],['Player','Team','Statistical rationale'])])
    parts.append('<p><small>Statistical watchlists are not market-based trade valuations. Live injuries, trades and depth charts are not independently checked by this version.</small></p>')
    return '<!doctype html><html><body style="font-family:Arial,sans-serif;color:#20242b;max-width:900px;margin:auto;padding:20px">'+''.join(parts)+'</body></html>'

def send_brevo(subject, html):
    key=os.environ.get('BREVO_API_KEY','').strip()
    sender=os.environ.get('BREVO_SENDER_EMAIL','').strip()
    if not key or not sender: raise RuntimeError('Missing BREVO_API_KEY or BREVO_SENDER_EMAIL')
    recipients=recipient_list(os.environ.get('REPORT_RECIPIENT_EMAILS',''))
    payload={'sender':{'name':os.getenv('BREVO_SENDER_NAME','NFL Fantasy AI Agent'),'email':sender},'to':[{'email':email} for email in recipients],'subject':subject,'htmlContent':html}
    response=requests.post('https://api.brevo.com/v3/smtp/email',headers={'api-key':key,'accept':'application/json','content-type':'application/json'},json=payload,timeout=30)
    if not response.ok:
        raise RuntimeError(f'Brevo send failed (HTTP {response.status_code}): {response.text[:400]}')
    return {'recipient_count':len(recipients),'message_id':response.json().get('messageId','unknown')}
