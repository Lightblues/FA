## API

1. API 的要求: 格式, 数据 (真实性, 多种条件覆盖)
2. 不同的实现方案: (一些难点是共通的)
    1. 代码实现 -- 难点在于如何覆盖query的多样性? 加随机策略? 
    2. LLM 模拟
3. 用文字还描述一个 API: 
    1. name, description, url
    2. input/output parameters
        1. type, name, description, required
    3. data 规范

需求
1. 修正已有 API
    1. 修改API名字? e.g. `智能接口2` -> `查询商品邮寄信息`
    2. 补充可选项信息 / desc
2. 实现/优化 基于LLM的API后端 
