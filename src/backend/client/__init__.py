from flowagent.data import Config

from .client_multi import MultiAgentMixin
from .client_single import SingleAgentMixin
from .client_tool import ToolAgentMixin


class FrontendClient(SingleAgentMixin, MultiAgentMixin, ToolAgentMixin):
    """Complete frontend client with both single and multi agent capabilities"""

    pass
