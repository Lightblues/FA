from fa_server.typings.typings_multi import MultiPostControlResponse


def test_multi_post_control_response():
    res = MultiPostControlResponse(
        success=True,
        msg=None,  # None or Message
    )
    print(res)


test_multi_post_control_response()
