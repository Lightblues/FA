from .client_single import SingleAgentMixin
from .client_multi import MultiAgentMixin


class FrontendClient(SingleAgentMixin, MultiAgentMixin):
    """Complete frontend client with both single and multi agent capabilities"""
    pass
