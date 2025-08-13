from langchain.agents import AgentType, initialize_agent, Tool
from langchain.llms import OpenAI
from langchain.utilities import WikipediaAPIWrapper, SerpAPIWrapper
from langchain.graphs import LangGraph, Node, Edge
from transformers import AutoModelForCausalLM, AutoTokenizer
# 初始化工具
search = SerpAPIWrapper()
wikipedia = WikipediaAPIWrapper()
llm = OpenAI(temperature=0)

tools = [
    Tool(
        name="Search",
        func=search.run,
        description="用于回答当前事件或事实性问题"
    ),
    Tool(
        name="Wikipedia",
        func=wikipedia.run,
        description="用于查询历史或科学知识"
    )
]

# 创建智能体
agent = initialize_agent(
    tools, 
    llm, 
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  # 最通用的代理类型
    verbose=True  # 打印详细过程
)

# 运行
response = agent.run("2023年诺贝尔物理学奖得主是谁？他们的主要贡献是什么？")
print(response)
