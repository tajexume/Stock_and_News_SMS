import requests
import os
import datetime
import json
import newsapi
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
Stock_url = 'https://www.alphavantage.co/query'
Stock_key = os.environ.get("alpha_hey")
Stock_param = {
    "function": "TIME_SERIES_Daily",
    "symbol": STOCK,
    "Output Size": "Compact",
    "apikey": Stock_key
}
Stock_API_Request = requests.get(url=Stock_url, params=Stock_param)
Stock_API_Request.raise_for_status()
Stock_Info = Stock_API_Request.json()
day_one = datetime.datetime.today() - datetime.timedelta(days=1)
day_two = datetime.datetime.today() - datetime.timedelta(days=2)


def findOpenorClose(day, Open=True):
    if Open:
        state = "1. open"
    else:
        state = "4. close"
    try:
        stock_value = float(Stock_Info["Time Series (Daily)"][f"{day.year}-{day.month}-{day.day}"]
                            [f"{state}"])
        return stock_value
    except KeyError:
        if day.day < 10 and day.month < 10:
            stock_value = float(Stock_Info["Time Series (Daily)"][f"{day.year}-0{day.month}-0{day.day}"]
                                [f"{state}"])
        elif day.month < 10:
            stock_value = float(Stock_Info["Time Series (Daily)"][f"{day.year}-0{day.month}-{day.day}"]
                                [f"{state}"])
        elif day.day < 10:
            stock_value = float(Stock_Info["Time Series (Daily)"][f"{day.year}-{day.month}-0{day.day}"]
                                [f"{state}"])
        return stock_value


day_one_open = findOpenorClose(day_one)
day_two_close = findOpenorClose(day_two, Open=False)
inc = day_two_close + (.05 * day_two_close)
dec = day_two_close- (.05 * day_two_close)

## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.
newsapi = newsapi.NewsApiClient(os.environ.get("news_key"))
stories = newsapi.get_everything(q=COMPANY_NAME)
if inc >= day_one_open or dec >= day_one_open:
    article = 0
    try:
        while article < 3 and article < stories["totalResults"]:
            print(f"{stories['articles'][article]}\n")
            article += 1
    except IndexError:
        print("No stories exist or ran out of stories")


## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number. 
    article = 0
    sms_sid = os.environ.get("sms_acc")
    sms_token = os.environ.get("sms_tok")
    sms_client = Client(sms_sid, sms_token)
    if inc <= day_one_open:
        diff = (day_one_open / day_two_close) * 100 - 100
        alert = f"{STOCK}: 🔺{diff}%\n"
    else:
        diff = 100 - (day_one_open / day_two_close) * 100
        alert = f"{STOCK}: 🔻{diff}%\n"

    while article != 3:
        alert += f"Headline: {stories['articles'][article]['title']}" \
                 f"\nBrief: {stories['articles'][article]['description']}\n"
        article += 1
    print(f"{alert}")
    message = sms_client.messages \
        .create(
        body=alert,
        from_="+19896238579",
        to="+13365758369"
    )

else:
    print("Nothing Happening")
# Optional: Format the SMS message like this:0
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""
