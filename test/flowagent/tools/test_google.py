from flowagent.tools.tool_google_search import images_search, news_search, web_search


def test_web():
    query = "上海 今天 天气"
    answer = web_search(
        query,
        use_answerBox=False,
        keep_topk=10,
        raw=False,
    )
    print(answer)


def test_news():
    query = "上海 新闻 最新"
    answer = news_search(
        query,
        keep_topk=5,
        raw=False,
    )
    print(answer)


def test_image():
    query = "腾讯logo"
    answer = images_search(query, keep_topk=1, raw=False, return_links=False)
    print(answer)
    print(type(answer))


# res = test_web()
res = test_news()
print()
