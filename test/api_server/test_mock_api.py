"""
Test mock API endpoints for customs policies and tips
"""

import json

import requests


BASE_URL = "http://localhost:8000"


def test_check_destination_customs_policy():
    """测试目的地清关政策查询接口

    {
        "status": 200,
        "message": "成功",
        "data": "日本清关政策：1. 禁止运输易燃易爆物品 2. 食品需要FDA认证 3. 电子产品需要FCC认证",
        "success": true
    }
    """
    print("\n=== 测试目的地清关政策查询 ===")

    # 准备请求数据
    data = {"countryCode": "US"}

    # 发送请求
    response = requests.post(f"{BASE_URL}/api/wiplus/base/large-model/serviceTips", json=data)

    # 打印响应
    print("Request:", json.dumps(data, ensure_ascii=False, indent=2))
    print("Response:", json.dumps(response.json(), ensure_ascii=False, indent=2))

    # 验证响应格式
    assert response.status_code == 200
    assert "status" in response.json()
    assert "message" in response.json()
    assert "data" in response.json()
    assert "success" in response.json()


def test_destination_customs_tips():
    """测试物品目的地清关提示接口

    {
        "status": 200,
        "message": "查询失败",
        "data": "仅支持单个物品查询",
        "success": true
    }
    {
        "status": 200,
        "message": "查询成功",
        "data": "支持清关",
        "success": true
    }
    """
    print("\n=== 测试物品目的地清关提示 ===")

    # 准备请求数据
    data = {"countryCode": "US", "goodsName": "电子产品"}

    # 发送请求
    response = requests.post(f"{BASE_URL}/api/wiplus/base/large-model/itemsCustomsTips", json=data)

    # 打印响应
    print("Request:", json.dumps(data, ensure_ascii=False, indent=2))
    print("Response:", json.dumps(response.json(), ensure_ascii=False, indent=2))

    # 验证响应格式
    assert response.status_code == 200
    assert "status" in response.json()
    assert "message" in response.json()
    assert "data" in response.json()
    assert "success" in response.json()


if __name__ == "__main__":
    try:
        test_check_destination_customs_policy()
        test_destination_customs_tips()
        print("\n所有测试通过!")
    except Exception as e:
        print(f"\n测试失败: {str(e)}")
