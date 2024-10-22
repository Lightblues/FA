""" 
from 对话接口 https://cloud.tencent.com/document/product/1759/105561
"""

from tencentcloud.common.common_client import CommonClient
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
import os, uuid

_service = "lke"
_api_version = "2023-11-30"


def get_token(secret, profile, region, params):  # region是字符串，其他都是dict
    # print(f"profile:{profile}, region:{region}, params:{params}")
    try:
        # cred = credential.Credential(
        #     os.environ.get("TENCENTCLOUD_SECRET_ID"),
        #     os.environ.get("TENCENTCLOUD_SECRET_KEY"))
        secret_id = secret["secret_id"] if "secret_id" in secret else ""
        secret_key = secret["secret_key"] if "secret_key" in secret else ""
        cred = credential.Credential(secret_id, secret_key)
        http_profile = HttpProfile()
        domain = profile["domain"] if "domain" in profile else ""
        scheme = profile["scheme"] if "scheme" in profile else "https"
        method = profile["method"] if "method" in profile else "POST"

        http_profile.rootDomain = domain
        http_profile.scheme = scheme
        http_profile.reqMethod = method
        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile

        # 实例化要请求的common client对象，clientProfile是可选的。
        common_client = CommonClient(_service, _api_version, cred, region, profile=client_profile)
        # 接口参数作为json字典传入，得到的输出也是json字典，请求失败将抛出异常，headers为可选参数
        resp = common_client.call_json("GetWsToken", params)
        # print("resp", resp)
        token = ""
        if ("Response" in resp) and ("Token" in resp["Response"]):
            token = resp["Response"]["Token"]
        # print("token", token)
        return token
    except TencentCloudSDKException as err:
        print(err)
        return ""

def get_session_id():
    # 生成一个 UUID
    new_uuid = uuid.uuid4()
    # 将 UUID 转换为字符串
    session_id = str(new_uuid)
    return session_id


def get_request_id():  # 生成的request_id有48位
    # 生成 24 个字节的随机数据
    random_bytes = os.urandom(24)

    # 将随机数据转换为十六进制字符串
    request_id = random_bytes.hex()
    return request_id
