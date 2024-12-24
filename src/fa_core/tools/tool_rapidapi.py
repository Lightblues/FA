"""
from @ian /cq8/ianxxu/chatchat/_TaskPlan/UI/v2.7_demo/tools/arxiv_tool.py

RapidAPI
    Collection of Free APIs: https://rapidapi.com/collection/list-of-free-apis
"""

import requests, os
from typing import List, Dict, Optional, Union, Any
from enum import Enum
from .register import register_tool

_rapid_api_key = os.getenv("RAPID_API_KEY", "")


class MethodEnum(Enum):
    GET = "GET"
    POST = "POST"


def query_rapidapi(url: str, querystring: Dict, headers_or_host: Union[Dict, str], method: MethodEnum = MethodEnum.GET) -> Any:
    """Standard function to query RapidAPI.
    NOTE:
    - set method to MethodEnum.POST if the API requires POST request.

    - TODO: the payload parameter?
    """
    if isinstance(headers_or_host, str):
        headers_or_host = {"X-RapidAPI-Key": _rapid_api_key, "X-RapidAPI-Host": headers_or_host}
    try:
        if method == MethodEnum.GET:
            response = requests.get(url, headers=headers_or_host, params=querystring).json()
        elif method == MethodEnum.POST:
            response = requests.post(url, headers=headers_or_host, params=querystring).json()
        else:
            raise ValueError(f"Invalid method: {method}")
    except Exception as e:
        return f"Error occurred during the API call: {e}"
    return response


# https://rapidapi.com/dfskGT/api/arxiv-json/
# FIXME: the API does not work anymore! should be replaced by official API: https://arxiv.org/help/api/user-manual
@register_tool()
def search_arxiv_paper(
    author: Optional[str] = "", keywords: Optional[str] = "", sort_by: Optional[str] = "lastUpdatedDate", max_results: Optional[int] = 5
) -> List[Dict]:
    """Search papers on arxiv by authors or keywords. (arxiv is an open-access preprint repository for scientific research.)

    Args:
        author (str, optional): the author of the paper. Defaults to "".
        keywords (str, optional): the keywords of the paper. Defaults to "".
        sort_by (str, optional): the sort order of the paper, available options: ["relevance", "lastUpdatedDate", "submittedDate"]. Defaults to "lastUpdatedDate".
        max_results (int, optional): the max number of results to return. Defaults to 5.

    Returns:
        List[Dict]: the list of papers.
    """
    if not author and not keywords:
        return "Please provide author or keywords."
    if not sort_by:
        sort_by = "lastUpdatedDate"
    if sort_by not in ["relevance", "lastUpdatedDate", "submittedDate"]:
        return "param 'sort_by' must be one of ['relevance', 'lastUpdatedDate', 'submittedDate']"

    url = "https://arxiv-json.p.rapidapi.com/papers"
    host = "arxiv-json.p.rapidapi.com"
    querystring = {
        "authors": author if author else "",
        "keywords": keywords if keywords else "",
        "sort_by": sort_by,
        "sort_order": "descending",
        "start": "0",
        "max_results": str(max_results),
    }
    return query_rapidapi(url, querystring, host)


# https://rapidapi.com/weatherapi/api/weatherapi-com/
# offical: https://www.weatherapi.com/docs/#apis-forecast
# TODO: the returned information is too much, need to be filtered!!!
@register_tool()
def get_weather_forecast(city: str, days: int = 1) -> Dict:
    """Get weather forecast by city name.

    Args:
        city (str): the city name.
        days (int, optional): the number of days to forecast. Defaults to 3.

    Returns:
        Dict: the weather forecast.
    """
    url = "https://weatherapi-com.p.rapidapi.com/forecast.json"
    querystring = {"q": city, "days": str(days), "lang": "zh"}
    host = "weatherapi-com.p.rapidapi.com"
    return query_rapidapi(url, querystring, host)


# https://rapidapi.com/apidojo/api/yh-finance
# case: https://blog.chatbotslife.com/how-i-created-a-bot-that-texts-me-a-personalized-morning-rundown-each-day-without-code-e8ea4623466d
@register_tool()
def get_stock_fundamentals(symbol: str, region: str = "US", modules: str = "assetProfile,summaryProfile,fundProfile") -> Dict:
    """Get stock fundamentals by symbol.

    Args:
        symbol (str): the stock symbol.
        region (str, optional): the region of the stock. Defaults to "US".
        modules (str, optional): the modules to return. Defaults to "assetProfile,summaryProfile,fundProfile".

    Returns:
        Dict: the stock fundamentals.
    """
    url = "https://yh-finance.p.rapidapi.com/stock/get-fundamentals"
    querystring = {
        "symbol": symbol,
        "region": region,  # US|BR|AU|CA|FR|DE|HK|IN|IT|ES|GB|SG
        "lang": "en-US",  # en-US|pt-BR|en-AU|en-CA|fr-FR|de-DE|zh-Hant-HK|en-IN|it-IT|es-ES|en-GB|en-SG
        "modules": modules,  # assetComponents,assetProfile,balanceSheetHistory,balanceSheetHistoryQuarterly,calendarEvents,cashflowStatementHistory,cashflowStatementHistoryQuarterly,components,defaultKeyStatistics,earnings,earningsHistory,earningsTrend,equityPerformance,esgScores,financialData,financialsTemplate,fundOwnership,fundPerformance,fundProfile,futuresChain,incomeStatementHistory,incomeStatementHistoryQuarterly,indexTrend,industryTrend,insiderHolders,insiderTransactions,institutionOwnership,majorDirectHolders,majorHoldersBreakdown,netSharePurchaseActivity,recommendationTrend,secFilings,sectorTrend,summaryDetail,summaryProfile,topHoldings,upgradeDowngradeHistory,pageViews,financialsTemplate,quoteUnadjustedPerformanceOverview
    }
    host = "yh-finance.p.rapidapi.com"
    return query_rapidapi(url, querystring, host)


@register_tool()
def get_stock_news(symbol: str, region: str = "US", count: int = 5) -> Dict:
    """Get stock news by symbol.

    Args:
        symbol (str): the stock symbol.
        region (str, optional): the region of the stock. Defaults to "US".
        count (int, optional): the number of news to return. Defaults to 5.

    Returns:
        Dict: the stock news.
    """
    url = "https://yh-finance.p.rapidapi.com/news/v2/list"
    querystring = {"region": region, "snippetCount": str(count), "s": symbol}
    host = "yh-finance.p.rapidapi.com"
    return query_rapidapi(url, querystring, host, method=MethodEnum.POST)
