from api_server import APICalling_Info, Mocker

def test_mocker():
    mocker = Mocker(model_name="gpt-4o")

    from api_server.api_definitions import m002_新闻查询        # NOTE: to register the apis
    query = APICalling_Info(
        name="query_news", kwargs={
            "news_location": "上海", "news_type": "体育", "news_time": "2024-08-30"
        }
    )
    res = mocker.mock_api_response(query)
    print(res)

if __name__ == "__main__":
    test_mocker()
