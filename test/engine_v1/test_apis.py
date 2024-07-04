from engine_v1.apis import call_py_name_and_paras, register_api, api_infos
# change workdir to ..
import os; os.chdir("../../src")

for api_info in api_infos:
    register_api(api_info)

res = call_py_name_and_paras("通过交易金额查询", ["100.50"])
print(res)  # {'order_links': ['/orders/ORD123']}

res = call_py_name_and_paras("通过订单编号查询", ["ORD123"])
print(res)  # {'details': 'Order details for ORD123'}