from flowagent.tools.tool_hunyuan_search import hunyuan_search, hunyuan_search_full

def test_hunyuan():
    query = "上海 天气"
    answer = hunyuan_search(query)
    for ch in answer:
        print(ch, end='', flush=True)
    print()

test_hunyuan()
