from .client_single import SingleAgentMixin
from .client_multi import MultiAgentMixin
from .client_tool import ToolAgentMixin
from flowagent.data import Config

class FrontendClient(SingleAgentMixin, MultiAgentMixin, ToolAgentMixin):
    """Complete frontend client with both single and multi agent capabilities"""
    pass

