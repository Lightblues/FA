from fa_server.routers.session_context_multi import create_session_context_multi
from fa_core.common import Config
from fa_server.common.shared import SharedResources


def test_session_context_multi():
    cfg = Config.from_yaml("cli_multi.yaml")
    SharedResources.initialize(cfg)

    session_context = create_session_context_multi("test", cfg)
    # print(session_context)

    workflow_name = "114挂号"
    session_context.init_workflow_agent(workflow_name)
    session_context.curr_status = workflow_name
    print(session_context.workflow_agent)


if __name__ == "__main__":
    test_session_context_multi()
