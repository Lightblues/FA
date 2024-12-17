from sympy import sympify


def calculator(question):
    try:
        return str(float(sympify(question)))
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    # question = "3+2*2"
    question = "2024-06-01 - 1884-07-07"
    print(calculator(question))
    print(type(calculator(question)))
