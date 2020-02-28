from django.shortcuts import render, redirect
from .models import Stock
from .forms import StockForm
from django.contrib import messages

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
        return render(request,"stock.html",{'api':api})

    else:
        return render(request,"index.html",{'api':''})

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
