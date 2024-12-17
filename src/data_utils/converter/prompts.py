"""
输入: Graph (条件判断)
输出: Python 形式的流程描述

old API: (p1, p2) -> (o1)
post_process: (o1) -> (o2)
new API: (p1, p2) -> (o1, o2)
new API: (p1, p2) -> (o2)
"""

template_procudure = """
<任务>
1. 对于一个图结构的工作流, 请你将其核心流程转为 Procedure 的形式.
2. Procedure 语法: 整体上采用 Python/伪代码 的形式, 其中,
    通过 `[变量] = API.API_NAME([参数])` 的形式调用 API;
    通过 `ANSWER.ANSWER_NAME()` 的形式调用 ANSWER.
3. 仅支持 API 和 ANSWER 两类节点, 节点名称需要和已有的名称完全一致.
</任务>

<示例>
相关信息:
```yaml
Name: 新闻查询
Desc: 根据特定需求查询新闻
SLOTs:
- name: news_location
  desc: 新闻发生地
- name: news_type
  desc: 新闻类型
- name: news_time
  desc: 新闻时间
APIs:
- name: check_location
  request: [news_location]
  response: [是否支持]
- name: query_news
  request: [news_location, news_type, news_time]
  response: [新闻列表]
ANSWERs:
- name: 获取新闻成功
  desc: 查询成功，返回查询到的新闻列表
- name: 获取新闻失败
  desc: 查询失败，转为播报当日头条新闻
- name: 其他自由回复问题
- name: 请用户提供必要信息
```
核心 Procedure:
```python
while True:
    [news_location] = ANSWER.请用户提供必要信息()
    if API.check_location([news_location]) == True:
        break
[news_type, news_time] = ANSWER.请用户提供必要信息()
[news_list] = API.query_news([news_location, news_type, news_time])
if news_list is not None:
    ANSWER.获取新闻成功()
else:
    ANSWER.获取新闻失败()
```
</示例>

<输入>
基础信息:
```
{meta}
```
API参数信息:
```
{params}
```
相关节点:
```
{nodes}
```
节点连边:
```
{edges}
```
</输入>

下面, 请基于输入的信息, 直接给出转换后的流程表述 Procedure:
""".strip()
