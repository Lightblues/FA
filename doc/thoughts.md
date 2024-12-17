## Questions

1. 关于PDL语法的思考 (from WikiHow)
    版本v2: 其中的组件定义包括 SLOT, API, ANSWER
    wikihow: 发现其中很多页面中包括了多个子流程, 同时它不是API, 而是需要返回给用户的信息
        -- 可以放进 ANSWER 中吗? 还是新定义一种组件类别 INSTRUCT?
        -- more, 在PDL中定义子函数, 乃至PDL之间的关联 (跳转关系)
2. 回复&API调用 之间的冲突问题
    在预测 action=ANSWER 时, 应该继续调用API (或者多个API一次执行的过程中反馈中间结果); 而在目前框架下会断掉
        -- 解决方案1: 输出结构中增加一个 END flag. 可以想见需要解决的, 是防止死循环
    这一问题的解决是否可作为一个亮点?



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


## 标注&评估

LLM & Human 标注

1. LLM
    1. SOTA模型的整体能力肯定是OK的, 关键在于如何激活;
    2. 输出格式规范还是很重要的! YAML or JSON
2. 人工
    1. 沟通/对齐 标注需求!
3. 两类评估方案之间的对齐
    1. 如何验证两者之间的一致性? 分数分布, 错误类别分布... (结合可视化)
    2. 进一步的, 需要在一开始就定义好明确的错误类别 (exclusive & 全面)
    3. case by case 的分析!

交互/操作逻辑

1. 两种交互形式: dataframe & excel
    1. 两者各自有一定的优势的问题.
    2. 通过 pandas 来操作: 格式更规范, 但是对于数据的理解 (阅读) 有限
    3. 通过腾讯文档等类 Excel 操作: 数据筛选, 便于阅读
2. 两种格式的转换: 需要统一的后台数据格式定义
