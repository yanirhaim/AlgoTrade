from django.shortcuts import render, redirect
from .models import Stock
from .forms import StockForm
from django.contrib import messages
import numpy as np
import datetime as datetime
import requests
import json
import pandas as pd

def stock(request, stock_id):

    df = get_stock(stock_id)
    print(df)

    stock_data = requests.get(
        'https://fmpcloud.io/api/v3/company/profile/' + stock_id + '?apikey=4f2b01132ec60b46eaa5a5916775d383')

    try:
        stock_data = json.loads(stock_data.content)

    except Exception as e:
        api = 'Error'

    return render(request, "stock.html", {
        'stock': stock_data,
        'df': df,
    })


# MAIN PAGE
def index(request):
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

    # Get data to analyze
    df = get_stock(stock_id)
    rsi_st = rsi_status(df, 14)
    rsi_perce = rsi_percent(df, 14)
    sma = sma_status(df)

    stock_data = requests.get(
        'https://fmpcloud.io/api/v3/company/profile/' + stock_id + '?apikey=4f2b01132ec60b46eaa5a5916775d383')

    try:
        stock_data = json.loads(stock_data.content)

    except Exception as e:
        api = 'Error'

    return render(request, "stock.html", {
        'stock': stock_data,
        'rsi_status': rsi_st,
        'rsi_percent': rsi_perce,
        'sma_status': sma,
    })

# Indicators
current_d = datetime.datetime.today().strftime('%Y-%m-%d')

def rsi_status(df, period):
    period = period  # Value of the RSI period

    # Creating a function where it will store the value of change per day, but just the ones that are increasing on a df
    def upward_c(close_p):
        mask = (close_p - close_p.shift(1)) > 0  # Condition for looking just increasing change per day
        v1 = close_p - close_p.shift(1)  # In case it is increasing it will store this value
        v2 = 0  # In case it is not increasing it will store this value
        df['Upward change'] = np.where(mask, v1, v2)  # Assigning the condition to the df, to assign the values

    upward_c(df['Close'])  # Calling the function with the Close Values

    # Creating a function where it will store the value of change per day, but just the ones that are decreasing on a df
    def downward_c(close_p):
        mask = (close_p - close_p.shift(1)) < 0  # Condition for looking just decreasing change per day
        v1 = (close_p - close_p.shift(1)) * -1  # In case it is decreasing it will store this value
        v2 = 0  # In case it is not decreasing it will store this value
        df['Downward change'] = np.where(mask, v1, v2)  # Assigning the condition to the df, to assign the values

    downward_c(df['Close'])  # Calling the function with the Close Values

    # Creating a function where it return an average change in relationship with the period, returning a list of values
    def av_m(change):
        x = 1
        y = 0
        f_value = 0
        avm = []
        while y != period:
            avm.append(np.nan)
            y += 1
        while x != period + 1:
            f_value += change[x]
            x += 1
        f_value = f_value / period
        avm.append(f_value)
        for up_ch in change[period + 1:]:
            avm.append(((f_value * (period - 1)) + up_ch) / period)
            f_value = ((f_value * (period - 1)) + up_ch) / period
        return avm

    df['Average UM'] = av_m(df['Upward change'])  # Getting the average upward movement values and storing them on a df
    df['Average DM'] = av_m(df['Downward change'])  # Getting the average downward movement values and storing them on a
                                                    # df

    df['RS'] = df['Average UM'] / df['Average DM']  # Getting the Relative Strength, and storing the values on a df

    # Function to obtain the Relative Strength index from the RS values, and returning a list.
    def rsi(rs):
        x = 0
        rsi_l = []
        while x != period:
            rsi_l.append(np.nan)
            x += 1
        for val in rs[period:]:
            rsi_l.append(100 - (100 / (val + 1)))

        return rsi_l

    df['RSI'] = rsi(df['RS'])  # Storing the list of values of the RSI on a df

    # The next part is to create a function wich allow as to know if whats the status of the stock, for this we would
    # define like this:
    # 10 means Overbought
    # 11 means UpwardTrend
    # 20 means Oversold
    # 22 means DownwardTrend
    # 90 for value we are not going to work (Nan)

    def status(value):
        # Creating a df with the RSI with a condition
        mask = (value > 70)  # Condition where it only works with the values greater than 70
        v1 = 10  # If the value is greter than 70, the value changes to 10
        v2 = value  # If not, it will remain the same
        df['Status'] = np.where(mask, v1, v2)  # Creates the df with the conditions

        # Function to delete all the Nan values from the df, wich has a relationship with the period
        x = 0
        while x != period:
            df['Status'][x] = 90
            x += 1

        # For loop to find the values that are below 30 and assign them a value of 20, in case they aren't, it will
        # remain the same
        x = 0
        for item in df['Status']:
            if item == 10:
                df['Status'][x] = item
                x += 1
            elif item < 30:
                df['Status'][x] = 20
                x += 1
            else:
                df['Status'][x] = item
                x += 1

        # For loop to find the trend of the values that are between 70 and 30
        # The For loop works like this, if the current value is 0, 10 or 20 it will remain the same
        # If the values are between, this are the conditions:
        # If the value is not 10, but the previous value was 10, then we assign that value with 22, which means downward
        # If the value is not 10, but the previous value was 22, then we assign that value with 22, which means it
        # continuous the downward
        # If the value is not 20, but the previous value was 20, then we assign that value with 11, which means
        # upward trend
        # If the value is not 20, but the previous value was 11, then we assign that value with 11, which means it
        # continuous the upward
        # In case the non of the conditions works, then we would assign the variable with 90
        x = 0
        for item in df['Status']:
            if item == 90:
                df['Status'][x] = 90
                x += 1
            elif item == 10:
                df['Status'][x] = item
                x += 1
            elif item == 20:
                df['Status'][x] = item
                x += 1
            elif (item != 10) & (df['Status'][x - 1] == 10):
                df['Status'][x] = 22
                x += 1
            elif (item != 10) & (df['Status'][x - 1] == 22):
                df['Status'][x] = 22
                x += 1
            elif (item != 20) & (df['Status'][x - 1] == 20):
                df['Status'][x] = 11
                x += 1
            elif (item != 20) & (df['Status'][x - 1] == 11):
                df['Status'][x] = 11
                x += 1
            else:
                df['Status'][x] = 90
                x += 1

    status(df['RSI'])  # Calling the function to get the status

    # We create a variable call status, where we plug the last value of the status df, and see what does it mean
    if df['Status'][-1] == 10:
        status = "Overbought"
    elif df['Status'][-1] == 20:
        status = "Oversold"
    elif df['Status'][-1] == 11:
        status = "In the middle of an UPWARD TREND"
    elif df['Status'][-1] == 22:
        status = "In the middle of a DOWNWARD TREND"
    else:
        status = "IDK"

    return status
def rsi_percent(df, period):
    period = period  # Value of the RSI period

    # Creating a function where it will store the value of change per day, but just the ones that are increasing on a df
    def upward_c(close_p):
        mask = (close_p - close_p.shift(1)) > 0  # Condition for looking just increasing change per day
        v1 = close_p - close_p.shift(1)  # In case it is increasing it will store this value
        v2 = 0  # In case it is not increasing it will store this value
        df['Upward change'] = np.where(mask, v1, v2)  # Assigning the condition to the df, to assign the values

    upward_c(df['Close'])  # Calling the function with the Close Values

    # Creating a function where it will store the value of change per day, but just the ones that are decreasing on a df
    def downward_c(close_p):
        mask = (close_p - close_p.shift(1)) < 0  # Condition for looking just decreasing change per day
        v1 = (close_p - close_p.shift(1)) * -1  # In case it is decreasing it will store this value
        v2 = 0  # In case it is not decreasing it will store this value
        df['Downward change'] = np.where(mask, v1, v2)  # Assigning the condition to the df, to assign the values

    downward_c(df['Close'])  # Calling the function with the Close Values

    # Creating a function where it return an average change in relationship with the period, returning a list of values
    def av_m(change):
        x = 1
        y = 0
        f_value = 0
        avm = []
        while y != period:
            avm.append(np.nan)
            y += 1
        while x != period + 1:
            f_value += change[x]
            x += 1
        f_value = f_value / period
        avm.append(f_value)
        for up_ch in change[period + 1:]:
            avm.append(((f_value * (period - 1)) + up_ch) / period)
            f_value = ((f_value * (period - 1)) + up_ch) / period
        return avm

    df['Average UM'] = av_m(df['Upward change'])  # Getting the average upward movement values and storing them on a df
    df['Average DM'] = av_m(df['Downward change'])  # Getting the average downward movement values and storing them on a
                                                    # df

    df['RS'] = df['Average UM'] / df['Average DM']  # Getting the Relative Strength, and storing the values on a df

    # Function to obtain the Relative Strength index from the RS values, and returning a list.
    def rsi(rs):
        x = 0
        rsi_l = []
        while x != period:
            rsi_l.append(np.nan)
            x += 1
        for val in rs[period:]:
            rsi_l.append(100 - (100 / (val + 1)))

        return rsi_l

    df['RSI'] = rsi(df['RS'])  # Storing the list of values of the RSI on a df

    def b_percentage(value):
        percentage = []
        for item in df['RSI']:
            if item > 70:
                percentage.append(100)
            elif item < 30:
                percentage.append(0)
            else:
                value = ((item-30)*10)/4
                percentage.append(100 - round(float(value),2))
        return percentage

    return b_percentage(df['RSI'])[-1] # Calling the function to get the percentage for buying
def get_stock(ticker, start_date='2015-01-01', end_date=current_d):
	data = requests.get("https://fmpcloud.io/api/v3/historical-price-full/" + ticker + "?from=" + start_date + "&to=" + end_date + "2&apikey=demo")
	data = json.loads(data.content)
	data = data['historical']

	dates = []  # List where we are going to save the dates values
	close = []  # List where we are going to save the close values
	adjClose = []

	# ForLoop for saving the data into the lists
	for item in data:
	    dates.append(pd.to_datetime(item['date']))  # getting the date as a pandas time-series
	    close.append(float(item['close']))  # getting the close price as a float
	    adjClose.append(float(item['adjClose']))  # getting the close price as a float

	# Reversing the content of the list, because we don't want the last close as our first value
	close.reverse()
	dates.reverse()
	adjClose.reverse()

	# Creating a pandas DataFrame with the values
	df = pd.DataFrame(list(zip(close, adjClose)), index=dates, columns=['Close', 'adjClose'])

	return df
def sma_status(df, ma1=50, ma2=200):
    df['{} Daily - SMA'.format(ma1)] = df['Close'].rolling(window=ma1).mean()  # moving average 6
    df['{} Daily - SMA'.format(ma2)] = df['Close'].rolling(window=ma2).mean()  # moving average 12
    df['Position'] = df['50 Daily - SMA'] > df['200 Daily - SMA']  # look the position between the SMA50 and SMA20

    cut_up = (df['Position'].shift(1) == False) & (df['Position'] == True)  # Places where the SMAs cut UP
    cut_down = (df['Position'].shift(1) == True) & (df['Position'] == False)  # Places where the SMAs cut DOWN

    if df['Position'][-1]:
        status = "UPWARD TREND"
    else:
        status = "DOWNWARD TREND"

    return status