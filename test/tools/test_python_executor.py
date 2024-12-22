import os
from tools.tool_python_executor import get_output_files, code_interpreter, DIR_DEFAULT


def python_executor_tool_old(code: str, exec_dir: str = DIR_DEFAULT):
    # NOTE: old version that use langchain_*.PythonREPL

    # from langchain_community.utilities import PythonREPL  # PythonREPL has been deprecated from langchain_community due to being flagged by security scanners. See: https://github.com/langchain-ai/langchain/issues/14345
    from langchain_experimental.utilities.python import PythonREPL

    pwd = os.getcwd()  # save the current directory
    code = code.strip()
    if code.startswith("```python"):
        code = code.split("```python")[1].split("```")[0].strip()
    os.makedirs(exec_dir, exist_ok=True)
    os.chdir(exec_dir)
    python_repl = PythonREPL()
    ret = python_repl.run(code)
    os.chdir(pwd)  # return to the original directory
    return ret.strip(), get_output_files(exec_dir)


code = """
import requests
from PIL import Image
import io

# 加载原始图片
url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Lujiazui_2016.jpg/1200px-Lujiazui_2016.jpg'
response = requests.get(url)
img = Image.open(io.BytesIO(response.content))

# 裁剪图片，取宽度的一半
half_width = img.width // 2
cropped_img = img.crop((half_width, 0, img.width, img.height))

# 保存裁剪后的图片
cropped_img.save('./lujiazui_cropped.jpg', 'JPEG', optimize=True, quality=95)
""".strip()


def test_python_executor(code: str):
    import json, time

    tic = time.time()
    # code = """import matplotlib.pyplot as plt\nplt.plot([1, 2, 3, 4])\nplt.title('标题')\nplt.savefig("test.png")\nprint('done')"""
    # code = """1+1"""
    # code = """import matplotlib.pyplot as plt\nplt.plot([1, 2, 3, 4])\nplt.title('标题')\nplt.savefig("test.png")\nprint('done')"""
    # code = """import datetime;import calendar;current_date = datetime.date.today();future_date = current_date + datetime.timedelta(days=1000);day_of_week = calendar.day_name[future_date.weekday()];print(day_of_week)"""
    # code = """import matplotlib.pyplot as plt\ndata = {\n    'model': ['千问1.5-72B-CHAT', '千问1.5-14B-CHAT'],\n    'Instruct': [97.5, 84.25],\n    'Plan': [80.83, 64.77],\n    'Reason': [58.11, 54.68],\n    'Retrieve': [76.14, 72.35],\n    'Understand': [71.94, 68.88],\n    'Review': [52.77, 44.15],\n    'OVERALL': [72.88, 64.85]\n}\nfor column in data:\n    plt.plot(data['model'], data[column], label=column)\nplt.xlabel('模型')\nplt.ylabel('得分')\nplt.title('模型性能折线图')\nplt.legend()\nplt.show()"""
    # code = """printf(1)"""

    res, files = code_interpreter(code)
    print(res)
    print(files)
    print(f"exec time: {(time.time()-tic):.2f}s")


if __name__ == "__main__":
    # python_executor_tool_old(code)
    test_python_executor(code)
