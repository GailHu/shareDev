# insall
# !pip install langchain langchain-openai python-dotenv

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate

# 基于字符串的提示
prompt = PromptTemplate.from_template("首都是{country}?")
filled_prompt = prompt.format(country="德国")
print(filled_prompt)

# 基于聊天的提示
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一位得力的助手。"),
    ("human", "{input}")
])
chat_filled = chat_prompt.invoke({"input": "将“你好”翻译成法语。"})
print(chat_filled.to_messages())