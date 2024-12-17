WORKFLOW_NODE_TYPES = [
    "CODE_EXECUTOR",
    "PARAMETER_EXTRACTOR",
    "LLM",
    "LLM_KNOWLEDGE_QA",
    "LOGIC_EVALUATOR",
    "ANSWER",
    "KNOWLEDGE_RETRIEVER",
    "START",
    "TOOL",
]
WORKFLOW_NODE_PROPERTIES = [
    "NodeID",
    "NodeName",
    "NodeDesc",
    "NodeType",
    "Inputs",
    "Outputs",
    "NextNodeIDs",
    "NodeUI",
]
NODE_TYPE_KEY_MAP = {
    "CODE_EXECUTOR": "CodeExecutorNodeData",  # ['Code', 'Language']
    "PARAMETER_EXTRACTOR": "ParameterExtractorNodeData",  # ['Parameters', 'UserConstraint']
    "LLM": "LLMNodeData",  # ['ModelName', 'Temperature', 'TopP', 'MaxTokens', 'Prompt']
    "LLM_KNOWLEDGE_QA": "LLMKnowledgeQANodeData",  # ['Query', 'ModelName', 'Filter', 'DocIDs', 'DocBizIDs', 'AllQA', 'Labels', 'DocRecallCount', 'DocConfidence', 'QARecallCount', 'QAConfidence']
    "LOGIC_EVALUATOR": "LogicEvaluatorNodeData",  # ['Group']
    "ANSWER": "AnswerNodeData",  # ['Answer']
    "KNOWLEDGE_RETRIEVER": "KnowledgeRetrieverNodeData",  # ['Query', 'Filter', 'DocIDs', 'DocBizIDs', 'AllQA', 'Labels', 'DocRecallCount', 'DocConfidence', 'QARecallCount', 'QAConfidence']
    "START": "StartNodeData",  # []
    "TOOL": "ToolNodeData",  # ['API', 'Header', 'Query', 'Body']
}
