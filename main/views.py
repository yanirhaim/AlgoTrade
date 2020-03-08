from django.shortcuts import render, redirect
from .models import Stock
from .forms import StockForm
from django.contrib import messages

def stock (request, stock_id):
    import requests
    import json

    api_request = requests.get("https://cloud.iexapis.com/stable/stock/" + stock_id + "/quote?token=pk_b613df2d4a924702ae1e2a134c2bbaba")

    try:
        api = json.loads(api_request.content)
        stock_name = api['companyName'].split(',')[0]
        stock_name = stock_name.split()[0]
        news_request = requests.get("http://newsapi.org/v2/top-headlines?q=" + stock_name + "&apiKey=166d39cbdc1e4442b00b48ec3880f9d6")
        news = json.loads(news_request.content)        
    except Exception as e:
        api = 'Error'

    news = news['articles']

    articles = [] 
    amount_art = 5;
    count = 0;

    for items in news:
        if count < amount_art:
            articles.append(items)
            count = count + 1


    return render(request, "stock.html", {
        'api':api,
        'news':articles,
    })


#MAIN PAGE - AND STOCK SEARCH PAGE
def index(request):
    import requests
    import json

    if request.method == 'POST':
        ticker = request.POST['ticker']
        api_request = requests.get("https://cloud.iexapis.com/stable/stock/" + ticker + "/quote?token=pk_b613df2d4a924702ae1e2a134c2bbaba")
        try:
            api = json.loads(api_request.content)
        except Exception as e:
            api = 'Error'
        
        return render(request,"stock.html",{
            'api':api,
        })

    else:

        api_requestm = requests.get("https://financialmodelingprep.com/api/v3/stock/gainers")
        try:
            api = json.loads(api_requestm.content)
        except Exception as e:
            api = 'Error'
            
        valueables = []
        count = 0
        for item in api['mostGainerStock']:
            if count < 10: #quantity of gainer stocks you want
                valueables.append(item)
                count += 1
            else:
                break

        return render(request,"index.html",{
            'api':'',
            'valueables': valueables,
        })

#ABOUT PAGE
def about(request):
    return render(request, "about.html", {})

#PORTOFOLIO PAGE
def my_stocks(request):
    import requests
    import json

    #---------------Yahoo API Test-------------------------
    import datetime as dt
    import pandas as pd
    import pandas_datareader.data as web
    start = dt.datetime(2019,1,1)
    end = dt.datetime.now()

    df = web.DataReader('TSLA', 'yahoo', start, end)
    df = df['Close'][-1]
    #------------------------------------------------------

    if request.method =='POST':
        form = StockForm(request.POST or None)

        if form.is_valid():
            form.save()
            messages.success(request, ('You add the Stock to your Portfolio'))
            return redirect('my_stocks')

    else:
        ticker = Stock.objects.all()
        output=[]
        for ticker_item in ticker:
            api_request = requests.get("https://cloud.iexapis.com/stable/stock/" + str(ticker_item) + "/quote?token=pk_b613df2d4a924702ae1e2a134c2bbaba")
            try:
                api = json.loads(api_request.content)
                output.append(api)
            except Exception as e:
                api = 'Error'

        return render(request, "my_stocks.html", {
            'ticker':ticker,
            'output':output,
            'df': df,
        })

#DELETE FUNCTION
def delete(request, stock_id):
    item = Stock.objects.get(pk=stock_id)
    item.delete()
    messages.success(request, ('You deleted the Stock from your Portfolio'))
    return redirect('my_stocks')
