import os, requests
from fa_core.tools.tool_rapidapi import get_weather_forecast, get_stock_fundamentals, get_stock_news, search_arxiv_paper


def test_search_arxiv_paper():
    res = search_arxiv_paper(keywords="agent")
    print(res)


def test_get_weather_forecast():
    res = get_weather_forecast(city="Shanghai", days=5)
    print(res)


def test_get_stock_fundamentals():
    res = get_stock_fundamentals(symbol="AMRN")
    print(res)


def test_get_stock_news():
    res = get_stock_news(symbol="AAPL")
    print(res)


def test_twitter():
    url = "https://twitter135.p.rapidapi.com/v1.1/Trends/"
    host = "twitter135.p.rapidapi.com"
    querystring = {"location_id": "-7608764736147602991", "count": "20"}

    headers = {"x-rapidapi-key": os.getenv("RAPID_API_KEY"), "x-rapidapi-host": host}

    response = requests.get(url, headers=headers, params=querystring)
    print(response.json())
    print()


# test_twitter()
# test_search_arxiv_paper()
# test_get_weather_forecast()
# test_get_stock_fundamentals()
test_get_stock_news()
