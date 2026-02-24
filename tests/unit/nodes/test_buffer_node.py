from pydag.agents.AgentConfig import AgentConfig
from pydag.nodes.BufferNode import BufferNode


def test_000():
    
    s = "".join(filter(str.isupper, BufferNode.cname())) + f"-{AgentConfig.FEATURE}" + "-{i}"
    print(s)
    
    ss = s.format(i = 1)
    
    print(ss)