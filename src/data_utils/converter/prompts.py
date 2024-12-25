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
2. Procedure 语法:
    2.1 整体上采用 Python/伪代码 的形式, 其中包括 API 和 ANSWER 两类特殊函数;
    2.2 通过 `[变量] = API.NAME([参数])` 的形式调用 API;
    2.3 通过 `ANSWER.NAME()` 的形式调用 ANSWER.
3. 转换规则:
    3.1 节点类型: 将原本图结构中 TOOL, LLM, CODE_EXECUTOR 类型的节点转为 API 节点. ANSWER 节点保持不变.
    3.2 节点名称: 用原本图节点中的 `NodeName` 作为 Procedure 中的 API/ANSWER 名称.
    3.3 条件判断: 将原本图结构中 LOGIC_EVALUATOR 类型的节点转为 Python 形式的条件判断.
4. 请给出完整的 Procedure 表述!
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
