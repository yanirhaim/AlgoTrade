from django.shortcuts import render, redirect
from .models import Stock
from .forms import StockForm
from django.contrib import messages


def stock(request, stock_id):
    import requests
    import json

    stock_data = requests.get(
        'https://fmpcloud.io/api/v3/company/profile/' + stock_id + '?apikey=4f2b01132ec60b46eaa5a5916775d383')

    try:
        stock_data = json.loads(stock_data.content)

    except Exception as e:
        api = 'Error'

    return render(request, "stock.html", {
        'stock': stock_data,
    })


# MAIN PAGE
def index(request):
    import requests
    import json

    api_gainer = requests.get(
        "https://financialmodelingprep.com/api/v3/stock/gainers?apikey=4f2b01132ec60b46eaa5a5916775d383")
    api_loser = requests.get(
        "https://financialmodelingprep.com/api/v3/stock/losers?apikey=4f2b01132ec60b46eaa5a5916775d383")
    api_active = requests.get(
        "https://financialmodelingprep.com/api/v3/stock/actives?apikey=4f2b01132ec60b46eaa5a5916775d383")
    api_sector = requests.get(
        "https://financialmodelingprep.com/api/v3/stock/sectors-performance?apikey=4f2b01132ec60b46eaa5a5916775d383")

    try:
        gainer = json.loads(api_gainer.content)
        loser = json.loads(api_loser.content)
        active = json.loads(api_active.content)
        sector = json.loads(api_sector.content)
    except Exception as e:
        api = 'Error'

    gainer = gainer['mostGainerStock']
    loser = loser['mostLoserStock']
    active = active['mostActiveStock']
    sector = sector['sectorPerformance']

    sector_n = []
    count = 0

    for items in sector:
        if count < 10:
            sector_n.append(items)
            count = count + 1
        else:
            break

    return render(request, "index.html", {
        'api': '',
        'gainer_list': gainer,
        'loser_list': loser,
        'active_list': active,
        'sector_list': sector_n,
    })


# ABOUT PAGE
def about(request):
    return render(request, "about.html", {})


# PORTFOLIO PAGE
def my_stocks(request):
    import requests
    import json

    # ---------------Yahoo API Test-------------------------
    import datetime as dt
    import pandas as pd
    import pandas_datareader.data as web
    start = dt.datetime(2019, 1, 1)
    end = dt.datetime.now()

    df = web.DataReader('TSLA', 'yahoo', start, end)
    df = df['Close'][-1]
    # ------------------------------------------------------

    if request.method == 'POST':
        form = StockForm(request.POST or None)

        if form.is_valid():
            form.save()
            messages.success(request, ('You add the Stock to your Portfolio'))
            return redirect('my_stocks')

    else:
        ticker = Stock.objects.all()
        output = []
        for ticker_item in ticker:
            api_request = requests.get("https://cloud.iexapis.com/stable/stock/" + str(
                ticker_item) + "/quote?token=pk_b613df2d4a924702ae1e2a134c2bbaba")
            try:
                api = json.loads(api_request.content)
                output.append(api)
            except Exception as e:
                api = 'Error'

        return render(request, "my_stocks.html", {
            'ticker': ticker,
            'output': output,
            'df': df,
        })


# DELETE FUNCTION
def delete(request, stock_id):
    item = Stock.objects.get(pk=stock_id)
    item.delete()
    messages.success(request, ('You deleted the Stock from your Portfolio'))
    return redirect('my_stocks')


def stock_s(request):
    query = request.GET.get('q')

    stock_id = query

    import requests
    import json

    api_request = requests.get(
        "https://cloud.iexapis.com/stable/stock/" + stock_id + "/quote?token=pk_b613df2d4a924702ae1e2a134c2bbaba")
    r = requests.get('https://finnhub.io/api/v1/stock/profile?symbol=' + stock_id + '&token=bpj80ufrh5rbrf4nci1g')

    try:
        api = json.loads(api_request.content)
        stock_name = api['companyName'].split(',')[0]
        stock_name = stock_name.split()[0]
        news_request = requests.get(
            "http://newsapi.org/v2/top-headlines?q=" + stock_name + "&apiKey=166d39cbdc1e4442b00b48ec3880f9d6")
        news = json.loads(news_request.content)
        info = json.loads(r.content)
    except Exception as e:
        api = 'Error'

    news = news['articles']

    articles = []
    amount_art = 4;
    count = 0;

    for items in news:
        if count < amount_art:
            articles.append(items)
            count = count + 1

    return render(request, "stock.html", {
        'api': api,
        'news': articles,
        'info': info,
    })
