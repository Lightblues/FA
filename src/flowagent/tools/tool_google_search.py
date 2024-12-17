""" 
from @ian /cq8/ianxxu/chatchat/_TaskPlan/UI/v2.1/tools/google_search.py
"""
from loguru import logger
from langchain_community.utilities import GoogleSerperAPIWrapper
import os; apikey = os.getenv("SERPER_API_KEY", "xxx")
if apikey == "xxx": logger.warning("SERPER_API_KEY is not set")
from .register import register_tool

google_serper = GoogleSerperAPIWrapper(
    k=10,
    gl='cn',
    hl='zh-cn',
    page=3,
    type="search", # ["news", "search", "places", "images"]
    serper_api_key=apikey
)

google_serper_news = GoogleSerperAPIWrapper(
    k=10,
    gl='cn',
    hl='zh-cn',
    page=3,
    type="news", # ["news", "search", "places", "images"]
    serper_api_key=apikey
)

google_serper_images = GoogleSerperAPIWrapper(
    k=10,
    gl='cn',
    hl='zh-cn',
    page=1,
    type="images", # ["news", "search", "places", "images"]
    serper_api_key=apikey
)

def _parse_results(
    results, use_answerBox:bool=False, 
    keep_topk:int=10, 
    search_type="search", return_links=False
) -> str:
    result_key_for_type = {
        "news": "news",
        "places": "places",
        "images": "images",
        "search": "organic",
    }
    snippets = []

    if use_answerBox:
        if results.get("answerBox"):
            answer_box = results.get("answerBox", {})
            if answer_box.get("answer"):
                return answer_box.get("answer")
            elif answer_box.get("snippet"):
                return answer_box.get("snippet").replace("\n", " ")
            elif answer_box.get("snippetHighlighted"):
                return answer_box.get("snippetHighlighted")

        if results.get("knowledgeGraph"):
            kg = results.get("knowledgeGraph", {})
            title = kg.get("title")
            entity_type = kg.get("type")
            if entity_type:
                snippets.append(f"{title}: {entity_type}.")
            description = kg.get("description")
            if description:
                snippets.append(description)
            for attribute, value in kg.get("attributes", {}).items():
                snippets.append(f"{title} {attribute}: {value}.")
    for result in results[result_key_for_type[search_type]][:keep_topk]:
        if search_type == 'search':
            if "snippet" in result:
                snippets.append(result["snippet"])
            for attribute, value in result.get("attributes", {}).items():
                snippets.append(f"{attribute}: {value}.")
            if len(snippets) == 0:
                return ["No good Google Search Result was found"]
        elif search_type == "news":
            if "title" in result and result['title']:
                snippets.append(f"{result['title']},来源:{result['source']},发布时间:{result['date']},链接:{result['link']}")
            else:
                continue
        elif search_type == "images":
            if return_links:
                snippets.append(result['imageUrl'])
            else:
                snippets.append(f"{result['title']},图片链接:{result['imageUrl']}")
            if len(snippets) >= keep_topk:
                break
    
    if search_type == 'search':
        ret = " ".join(snippets)
    elif search_type == "news":
        ret = '\n'.join(snippets)
    elif search_type == "images":
        if return_links:
            ret = snippets
        else:
            ret = '\n'.join(snippets)
    return ret


@register_tool()
def web_search(query: str, use_answerBox:bool=True, keep_topk:int=10) -> str:
    """Use Google Serper to search web

    Args:
        query (str): search query
        use_answerBox (bool, optional): whether to use answerBox of returned results. 
        keep_topk (int, optional): keep top k results.

    Returns:
        str: the search results
    """
    try:
        answer = google_serper.results(query)
        return _parse_results(answer, use_answerBox, keep_topk, google_serper.type)
    except Exception as e:
        return str(e)

@register_tool()
def news_search(query: str, keep_topk:bool=10) -> str:
    try:
        answer = google_serper_news.results(query)
        return _parse_results(results=answer, keep_topk=keep_topk, search_type=google_serper_news.type)
    except Exception as e:
        return str(e)

@register_tool()
def images_search(query, keep_topk:int=10, return_links:bool=False):
    try:
        answer = google_serper_images.results(query)
        return _parse_results(results=answer, keep_topk=keep_topk, search_type=google_serper_images.type, return_links=return_links)
    except Exception as e:
        return str(e)




