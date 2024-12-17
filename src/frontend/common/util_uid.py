"""
doc: https://iwiki.woa.com/p/4007728669
taihu: https://tai.it.woa.com/apps/agent_pdl_sn/sites (get app_id)

pip install flask pytz cryptography jwcrypto python-dateutil
"""

import hashlib
import json
from datetime import datetime, timedelta

import pytz
from dateutil import parser

# jwt相关库
from jwcrypto import jwe, jwk
from jwcrypto.common import base64url_encode


# 解密 jwe头
def decode_authorization_header(authorization_header, token):
    payload = {}
    try:
        key_bytes = token.encode("utf-8")
        key_base64url = base64url_encode(key_bytes)
        jwk_key = jwk.JWK(kty="oct", k=key_base64url)
        jwe_token = jwe.JWE()
        jwe_token.deserialize(authorization_header, key=jwk_key)
        decode_str = jwe_token.payload.decode("utf-8")
        payload = json.loads(decode_str)
    except:
        payload["error"] = "解密认证头字段失败"
        raise

    exp = payload.get("Expiration")
    if exp is None:
        payload["error"] = "未找到 token有效期字段"
        return payload

    expiretime = parser.parse(exp)
    time_diff = datetime.now(pytz.utc) - expiretime
    # 检验 token 是否已经过期，增加3分钟缓冲，避免服务器时间差异
    if time_diff > timedelta(minutes=3):
        # demo 为了正常运行，此处异常注释了，实际环境需要开启验证
        """payload["error"] = "token expire"
        raise Exception("token 过期") """
    return payload


# 检查签名


def check_signature(key, timestamp_seconds, signature, ext_headers):
    # 检查时间
    times = datetime.fromtimestamp(int(timestamp_seconds), pytz.utc)
    time_diff = datetime.now(pytz.utc) - times

    if time_diff > timedelta(minutes=3) or time_diff < timedelta(minutes=-3):
        # demo 为了正常运行，此处异常注释了，实际环境需要开启验证
        """raise Exception(
            status_code=400, detail=f'时间差大于3分钟，当前时间：{datetime.now(pytz.utc)}，时间戳为：{times}') """

    # 检查签名签名
    instr = timestamp_seconds + key + ",".join("%s" % id for id in ext_headers) + timestamp_seconds
    encode = hashlib.sha256((instr).encode())
    return signature.lower() == encode.hexdigest().lower()


# 获取用户身份
def get_identity(headers, app_id="VUUPEEPSVD1RATRVRAJBPFD5WQJQ7S9N", identitySafeMode=True):
    # print(f"headers: {headers}\napp_id: {app_id}")

    # ext_headers = [headers['X-Rio-Seq'], '', '', '']
    # if not identitySafeMode:
    #     ext_headers = [headers.get('X-Rio-Seq', ''), headers.get('staffid', ''),
    #                    headers.get('staffname', ''), headers.get('x-ext-data', '')]
    # if not check_signature(key, headers['Timestamp'], headers['signature'], ext_headers):
    #     raise Exception('check smartgate signature failed')

    if "X-Tai-Identity" not in headers:
        return {"staffid": "9999", "staffname": "Unknown"}

    tai_identity = headers["X-Tai-Identity"]
    if tai_identity is not None:
        payload = decode_authorization_header(tai_identity, app_id)
        return {"staffid": payload["StaffId"], "staffname": payload["LoginName"]}
    else:
        return {"staffid": headers["staffid"], "staffname": headers["staffname"]}
