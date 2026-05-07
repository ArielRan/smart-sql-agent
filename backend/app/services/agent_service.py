from app.core.llm import llm

history = []

def chat(question: str):
    prompt = f'''
你是 MySQL 数据分析助手，只输出 SQL。

用户问题:
{question}
'''

    response = llm.invoke(prompt)

    sql = response.content

    result = {
        "question": question,
        "sql": sql,
        "data": []
    }

    history.append({
        "question": question,
        "sql": sql
    })

    return result