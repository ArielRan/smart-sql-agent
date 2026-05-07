import re
import json
from sqlalchemy import text
from app.core.llm import llm
from app.core.database import SessionLocal
from fastapi import HTTPException

history = []


def get_schema() -> str:
    """Get table schema from MySQL for LLM context."""
    db = SessionLocal()
    try:
        tables = db.execute(
            text("SHOW TABLES")
        ).fetchall()

        schema_parts = []
        for row in tables:
            table_name = row[0]
            columns = db.execute(
                text(f"SHOW COLUMNS FROM `{table_name}`")
            ).fetchall()
            col_info = ", ".join(
                f"{c[0]} {c[1]}" for c in columns
            )
            schema_parts.append(f"  {table_name}({col_info})")

        return "\n".join(schema_parts) if schema_parts else "(empty database)"
    finally:
        db.close()


def clean_sql(raw_sql: str) -> str:
    """Remove markdown code fences from LLM output."""
    match = re.search(
        r"```(?:sql)?\s*\n?(.*?)\n?```", raw_sql, re.DOTALL | re.IGNORECASE
    )
    if match:
        return match.group(1).strip()
    return raw_sql.strip()


def execute_sql(sql: str) -> list[dict]:
    """Execute SQL and return results as list of dicts."""
    db = SessionLocal()
    try:
        result = db.execute(text(sql))
        rows = result.fetchall()
        columns = list(result.keys())
        return [dict(zip(columns, row)) for row in rows]
    finally:
        db.close()


def chat(question: str):
    schema = get_schema()

    # Step 1: 生成 SQL
    sql_prompt = f"""
你是 MySQL 数据分析助手。根据表结构信息生成正确的 SQL 查询语句，只输出 SQL。

表结构:
{schema}

用户问题:
{question}
"""

    try:
        response = llm.invoke(sql_prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM 调用失败: {str(e)}")

    sql = clean_sql(response.content)

    # Step 2: 执行 SQL
    try:
        data = execute_sql(sql)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SQL 执行失败: {str(e)}")

    # Step 3: 用 LLM 生成自然语言回复，判断展示形式
    data_sample = data[:10] if len(data) > 10 else data
    answer_prompt = f"""
用户提问: {question}
执行的SQL: {sql}
查询结果(共{len(data)}条，展示前{len(data_sample)}条): {json.dumps(data_sample, ensure_ascii=False)}

请根据查询结果用自然语言回复用户。注意:
1. 回复要生动、友好，直接告诉用户答案
2. 不要输出SQL，只输出用户能看懂的自然语言
3. 从结果中提取关键信息答复

同时判断展示形式，输出一个JSON对象:
{{"answer": "自然语言回复内容", "display_type": "text或table"}}
- 如果结果是列表/多行数据适合用表格展示，display_type 用 "table"
- 如果是单个统计数字/简单答案，display_type 用 "text"

只输出JSON，不要有其他文字。
"""

    try:
        answer_response = llm.invoke(answer_prompt)
        answer_json = json.loads(clean_sql(answer_response.content))
    except Exception:
        # 如果 LLM 返回的不合规，降级处理
        answer_json = {
            "answer": f"查询完成，共返回 {len(data)} 条记录",
            "display_type": "table" if len(data) > 1 else "text",
        }

    columns = list(data[0].keys()) if data else []

    result = {
        "question": question,
        "sql": sql,
        "answer": answer_json["answer"],
        "display_type": answer_json["display_type"],
        "columns": columns,
        "data": data,
    }

    history.append({"question": question, "sql": sql})

    return result
