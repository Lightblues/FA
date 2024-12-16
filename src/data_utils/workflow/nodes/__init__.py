from .base_node import NodeTypeRegistry, WorkflowNodeBase
from .node_data.tool_node_data import ToolNodeData
from .node_data.answer_node_data import AnswerNodeData
from .node_data.llm_node_data import LLMNodeData
from .node_data.logic_evaluator_node_data import LogicEvaluatorNodeData
from .node_data.parameter_extractor_node_data import ParameterExtractorNodeData

NodeTypeRegistry.register("TOOL", ToolNodeData)
NodeTypeRegistry.register("ANSWER", AnswerNodeData)
NodeTypeRegistry.register("LLM", LLMNodeData)
NodeTypeRegistry.register("LOGIC_EVALUATOR", LogicEvaluatorNodeData)
NodeTypeRegistry.register("PARAMETER_EXTRACTOR", ParameterExtractorNodeData)