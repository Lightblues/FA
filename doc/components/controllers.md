

```python
for i in range(max_retry):
    # pre-decision controllers: traverse and use their messages to generate the prompt
    pre_messages = []
    for c in pre_controllers:
        pre_messages.append(c.process())
    prompt = gen_prompt(template, pre_messages, ...)
    # agent generate action
    agent_output = agent.process(prompt, ...)
    # post-decision controllers: traverse and check the agent's action
    if_pass = True
    for c in post_controllers:
        post_result = c.process(bot_output)
        if not post_result:
            if_pass = False
            break
    if if_pass: # break the loop if all post-decision controllers pass
        break
```

### DAG controller
```python
class NodeDependencyController(BaseController):
    def _build_graph(self, pdl:PDL):
        g = PDLGraph()
        for node in pdl.nodes:
            node = PDLNode(name=node["name"], preconditions=node.get("precondition", None))
            g.add_node(node)
        self.graph = g

    def pre_control(self) -> str:
        next_turn_invalid_apis = self.graph.get_invalid_node_names()
        if len(next_turn_invalid_apis) > 0:
            msg = f"APIs {next_turn_invalid_apis} dependency not satisfied: The precondintion API has not been called."
        else:
            msg = ""
        return msg

    def post_check(self, bot_output:BotOutput) -> bool:
        next_node = bot_output.action
        node = self.graph.name2node[next_node]
        if node.precondition:
            for p in node.precondition:
                if not self.graph.name2node[p].is_activated:
                    add_system_message(f"Precondition check failed! {p} not activated for {next_node}!")
                    return False
        node.is_activated = True
        add_system_message(f"Check success! {next_node} activated!")
        return True


class PDLGraph:
    def get_invalid_node_names(self) -> List[str]:
        invalid_nodes = []
        for node in self.name2node.values():
            for precondition in node.precondition:
                if not self.name2node[precondition].is_activated:
                    invalid_nodes.append(node)
                    break
        return [node.name for node in invalid_nodes]
```
