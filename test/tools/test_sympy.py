from fa_core.tools import calculator


def test_calculator():
    question = "3+2*2"
    print(calculator(question))
    print(type(calculator(question)))


test_calculator()
