from nfl_agent.email_delivery import recipient_list, html_report
import pandas as pd
import pytest

def test_multiple_recipients():
    assert recipient_list(' a@example.com, b@example.com; a@example.com ') == ['a@example.com','b@example.com']

def test_invalid_recipient():
    with pytest.raises(ValueError): recipient_list('not-an-email')

def test_html_escape():
    df=pd.DataFrame([dict(position='QB',rank=1,player_name='<script>',team='T',ros_ppr=100,movement_label='NEW')])
    out=html_report('Test','<unsafe>',df,pd.DataFrame(),7,2026)
    assert '&lt;script&gt;' in out and '&lt;unsafe&gt;' in out
