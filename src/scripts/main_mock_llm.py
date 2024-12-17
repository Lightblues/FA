"""@241204 @Cursor
Mock the response from OpenAI API, for testing

Usage::

    uvicorn main_mock_llm:app --host 0.0.0.0 --port 8000

    python test/backend/test_mock_llm.py
"""

import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessage,
)
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_chunk import (
    Choice as ChunkChoice,
)


app = FastAPI()


async def generate_stream_response(content: str, model: str):
    # 将响应内容按字符切分，模拟流式输出
    for char in content:
        chunk = ChatCompletionChunk(
            id="mock-response",
            model=model,
            object="chat.completion.chunk",
            created=1234567890,
            choices=[
                ChunkChoice(
                    delta={"role": "assistant", "content": char},
                    finish_reason=None,
                    index=0,
                )
            ],
        )
        # 必须按照 SSE 格式发送数据
        yield f"data: {chunk.model_dump_json()}\n\n"
        await asyncio.sleep(0.05)  # 添加一些延迟使流式效果更明显

    # 发送结束标记
    final_chunk = ChatCompletionChunk(
        id="mock-response",
        model=model,
        object="chat.completion.chunk",
        created=1234567890,
        choices=[
            ChunkChoice(
                delta={},
                finish_reason="stop",
                index=0,
            )
        ],
    )
    yield f"data: {final_chunk.model_dump_json()}\n\n"
    yield "data: [DONE]\n\n"


@app.post("/v1/chat/completions")
async def chat_completions(request: dict):  # 直接使用 dict 接收请求
    # 打印收到的消息
    print("\n=== 收到新请求 ===")
    print("模型:", request["model"])
    for msg in request["messages"]:
        print(f"{msg['role']}: {msg['content']}")

    # 等待用户在命令行输入响应
    print("\n请输入回复 (输入完成后按回车):")
    response_content = input()

    # 如果是流式请求
    if request.get("stream", False):
        return StreamingResponse(
            generate_stream_response(response_content, request["model"]),
            media_type="text/event-stream",
        )

    # 非流式请求
    response = ChatCompletion(
        id="mock-response",
        model=request["model"],
        object="chat.completion",
        created=1234567890,
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content=response_content,
                    role="assistant",
                ),
            )
        ],
        usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    )

    return response


if __name__ == "__main__":
    print("模拟 OpenAI API 服务器已启动在 http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
