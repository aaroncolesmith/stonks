import pandas as pd
import streamlit as st
import plotly_express as px
import requests
import datetime
from bs4 import BeautifulSoup
from pytz import timezone
import pytz

st.set_page_config(layout='wide',initial_sidebar_state='collapsed')

def load_data():
    df = pd.read_csv('./stonks_data.csv')
    df['occurences']=pd.to_numeric(df['occurences'])
    df['positive']=pd.to_numeric(df['positive'])
    df['negative']=pd.to_numeric(df['negative'])

    df['date'] = pd.to_datetime(df['date'])
    return df


def update_data(df):
    url='https://stocks.comment.ai/trending.html'
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    table = soup.find('table', class_='trending_table')
    rows=list()
    for row in table.findAll("tr"):
        rows.append(row)
    a=[]
    for x in range(0,len(rows)):
        for i in rows[x].findAll('td'):
            a.append(i.text)

    l1=[]
    l2=[]
    l3=[]
    l4=[]
    for i in range(0,len(a),4):
        l1.append(a[i])
    for i in range(1,len(a),4):
        l2.append(a[i])
    for i in range(2,len(a),4):
        l3.append(a[i])
    for i in range(3,len(a),4):
        l4.append(a[i])

    d = pd.DataFrame(
    {
        'occurences':l1,
        'sentiment':l2,
        'ticker':l3,
        'company':l4,
        'date':pd.to_datetime(datetime.datetime.now().astimezone(timezone('US/Pacific')))
    })

    st.write(pd.to_datetime(datetime.datetime.now().astimezone(timezone('US/Pacific'))))

    d=pd.merge(d,d.sentiment.str.split(expand=True),left_index=True,right_index=True)
    d.columns = ['occurences','sentiment','ticker','company','date','positive','negative','neutral']

    df = pd.concat([df,d])
    df['occurences']=pd.to_numeric(df['occurences'])
    df['positive']=pd.to_numeric(df['positive'])
    df['negative']=pd.to_numeric(df['negative'])

    df['date'] = pd.to_datetime(df['date'],utc=True)

    df = df.sort_values(['ticker', 'date']).reset_index(drop=True)
    df['pos_pct_chg'] = df.groupby('ticker', sort=False)['positive'].apply(
         lambda x: x.pct_change()).to_numpy()

    df['date'] = pd.to_datetime(df.date).dt.tz_localize(None)
    df=df.loc[df.date < pd.to_datetime(datetime.datetime.now())]
    return df


def main():
    st.title('Stonks!!')

    df=load_data()
    df=update_data(df)

    st.write(df.date.max())

    df = df.sort_values(['ticker', 'date']).reset_index(drop=True)
    df['pos_pct_chg'] = df.groupby('ticker', sort=False)['positive'].apply(lambda x: x.pct_change()).to_numpy()


    fig=px.scatter(df,
              x='date',
              y='positive',
              color='ticker',
                  title='WSB Postive Sentiment Over Time')
    fig.update_traces(mode='lines+markers',
                          marker=dict(size=8,
                                      line=dict(width=1,
                                                color='DarkSlateGrey')))
    st.plotly_chart(fig,use_container_width=True)


    fig=px.scatter(df.loc[df.date == df.date.max()],
               x='positive',
               y='pos_pct_chg',
               color='ticker',
               title='Most Recent Positive Sentiment vs. Pct Change')
    fig.update_traces(mode='markers',
                          marker=dict(size=8,
                                      line=dict(width=1,
                                                color='DarkSlateGrey')))
    st.plotly_chart(fig,use_container_width=True)


    fig=px.scatter(df,
              x='date',
              y='pos_pct_chg',
              color='ticker',
                  title='WSB Positive Sentiment Pct Change Over Time')
    fig.update_traces(mode='lines+markers',
                          marker=dict(size=8,
                                      line=dict(width=1,
                                                color='DarkSlateGrey')))
    st.plotly_chart(fig,use_container_width=True)



if __name__ == "__main__":
    #execute
    main()
