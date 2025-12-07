"""
Example 01: 简单的顺序工作流 - 文章生成器

这个例子展示了如何使用 LangGraph 创建一个顺序执行的工作流。
系统会依次执行：标题输入 -> 大纲生成 -> 正文撰写 -> 内容润色
"""

import os
import time
from typing import TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

# 加载环境变量
load_dotenv()

# 初始化 LLM
model_name = os.getenv("MODEL_NAME", "deepseek-chat")

llm = ChatOpenAI(
    model=model_name,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPEAI_BASE_URL"),
    temperature=0.7,
)


# 定义状态结构
class ArticleState(TypedDict):
    """文章生成的状态定义"""
    title: str              # 文章标题
    outline: str            # 文章大纲
    content: str            # 正文内容
    polished_content: str   # 润色后的内容
    current_step: str       # 当前步骤


# 步骤1：标题输入和确认
def input_title(state: ArticleState) -> ArticleState:
    """
    接收并确认文章标题
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态
    """
    print("\n=== 第1步：标题确认 ===")
    title = state.get("title", "")
    
    if not title:
        raise ValueError("标题不能为空")
    
    print(f"标题: {title}")
    
    return {
        **state,
        "current_step": "title_confirmed"
    }


# 步骤2：生成文章大纲
def generate_outline(state: ArticleState) -> ArticleState:
    """
    基于标题生成文章大纲
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态，包含大纲
    """
    print("\n=== 第2步：大纲生成 ===")
    title = state["title"]
    
    # 构建提示词
    prompt = f"""请为以下标题生成一个文章大纲：

标题：{title}

要求：
1. 包含3-5个主要章节
2. 每个章节有简短的描述
3. 逻辑清晰，结构合理

请直接输出大纲内容，不需要额外说明。"""
    
    # 调用 LLM 生成大纲
    response = llm.invoke(prompt)
    outline = response.content
    
    print(outline)
    
    return {
        **state,
        "outline": outline,
        "current_step": "outline_generated"
    }


# 步骤3：撰写正文
def write_content(state: ArticleState) -> ArticleState:
    """
    根据大纲撰写完整文章
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态，包含正文
    """
    print("\n=== 第3步：正文撰写 ===")
    title = state["title"]
    outline = state["outline"]
    
    # 构建提示词
    prompt = f"""请根据以下标题和大纲，撰写一篇完整的文章：

标题：{title}

大纲：
{outline}

要求：
1. 每个章节应有2-3段内容
2. 总字数约500-800字
3. 内容充实，逻辑连贯
4. 语言流畅自然

请直接输出文章内容，不需要额外说明。"""
    
    # 调用 LLM 撰写正文
    response = llm.invoke(prompt)
    content = response.content
    
    print(content)
    
    return {
        **state,
        "content": content,
        "current_step": "content_written"
    }


# 步骤4：内容润色
def polish_content(state: ArticleState) -> ArticleState:
    """
    优化和润色文章内容
    
    Args:
        state: 当前状态
        
    Returns:
        更新后的状态，包含润色后的内容
    """
    print("\n=== 第4步：内容润色 ===")
    content = state["content"]
    
    # 构建提示词
    prompt = f"""请对以下文章内容进行润色和优化：

{content}

要求：
1. 优化语言表达，使其更加流畅
2. 检查语法和逻辑连贯性
3. 提升文章的可读性和专业性
4. 保持原文的核心观点和结构

请直接输出润色后的文章，不需要额外说明。"""
    
    # 调用 LLM 润色内容
    response = llm.invoke(prompt)
    polished_content = response.content
    
    print(polished_content)
    
    return {
        **state,
        "polished_content": polished_content,
        "current_step": "content_polished"
    }


# 构建工作流图
def create_article_workflow():
    """
    创建文章生成工作流
    
    Returns:
        编译后的工作流图
    """
    # 创建状态图
    workflow = StateGraph(ArticleState)
    
    # 添加节点
    workflow.add_node("input_title", input_title)
    workflow.add_node("generate_outline", generate_outline)
    workflow.add_node("write_content", write_content)
    workflow.add_node("polish_content", polish_content)
    
    # 设置入口点
    workflow.set_entry_point("input_title")
    
    # 添加边，定义执行顺序
    workflow.add_edge("input_title", "generate_outline")
    workflow.add_edge("generate_outline", "write_content")
    workflow.add_edge("write_content", "polish_content")
    workflow.add_edge("polish_content", END)
    
    # 编译图
    return workflow.compile()


# 主函数
def main():
    """主函数：运行文章生成流程"""
    print("=" * 60)
    print("文章生成器 - 简单顺序工作流示例")
    print("=" * 60)
    
    # 创建工作流
    app = create_article_workflow()
    
    # 准备初始状态
    initial_state = {
        "title": "人工智能在医疗领域的应用",
        "outline": "",
        "content": "",
        "polished_content": "",
        "current_step": "initial"
    }
    
    # 记录开始时间
    start_time = time.time()
    
    # 执行工作流
    final_state = app.invoke(initial_state)
    
    # 记录结束时间
    end_time = time.time()
    
    # 输出最终结果
    print("\n" + "=" * 60)
    print("✅ 文章生成完成！")
    print("=" * 60)
    print(f"\n【最终文章】\n")
    print(final_state["polished_content"])
    print("\n" + "=" * 60)
    print(f"总耗时: {end_time - start_time:.2f}秒")
    print("=" * 60)


if __name__ == "__main__":
    main()
