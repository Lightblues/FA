""" @241205 @Cursor
Mock API server that returns manually entered responses
see [test_mock_api.py]

Usage::
    uvicorn main_mock_api:app --host 0.0.0.0 --port 8000
"""
import uvicorn
import json
from fastapi import FastAPI, HTTPException

app = FastAPI()

def get_multiline_input():
    """获取多行输入，直到输入空行为止"""
    print("\n请输入回复 (输入空行结束):")
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    return "\n".join(lines)

@app.post("/{path:path}")
async def handle_all_requests(path: str, request: dict):
    # 打印收到的请求信息
    print("\n=== 收到新请求 ===")
    print(f"Path: /{path}")
    print("Request body:", request)
    
    # 获取多行输入作为响应
    response_content = get_multiline_input()
    
    try:
        # 将输入的JSON字符串解析为Python字典
        response_dict = json.loads(response_content)
        return response_dict
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON input: {str(e)}")

if __name__ == "__main__":
    print("Mock API 服务器已启动在 http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)