"""
Example 02: 条件分支 - 智能客服路由

实现一个智能客服系统，能够自动识别用户问题的类型，并将问题路由到相应的专业团队处理。
"""

import os
import uuid
from datetime import datetime
from typing import Literal, TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

# 加载环境变量
load_dotenv()

# 定义状态类型
class CustomerServiceState(TypedDict):
    """智能客服系统状态定义"""
    messages: list
    question_id: str
    user_question: str
    question_type: Literal["technical", "sales", "complaint"] | None
    urgency_level: Literal["low", "medium", "high"] | None
    handler: str | None
    response: str | None
    quality_score: float | None


# 初始化模型
# 初始化 LLM
model_name = os.getenv("MODEL_NAME", "deepseek-chat")
model = ChatOpenAI(
    model=model_name,
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPEAI_BASE_URL"),
    temperature=0.7,
)


def receive_question(state: CustomerServiceState) -> CustomerServiceState:
    """接收用户问题并生成问题ID"""
    # 获取用户输入（假设从 messages 中获取最后一个用户消息）
    user_message = state["messages"][-1]["content"]
    
    # 生成问题ID和时间戳
    question_id = f"Q{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:3].upper()}"
    
    return {
        **state,
        "question_id": question_id,
        "user_question": user_message,
        "question_type": None,
        "urgency_level": None,
        "handler": None,
        "response": None,
        "quality_score": None
    }


def classify_question(state: CustomerServiceState) -> CustomerServiceState:
    """智能分类用户问题"""
    user_question = state["user_question"]
    
    # 使用 LLM 进行问题分类
    classification_prompt = f"""
    请分析以下用户问题，判断其属于哪种类型：
    - 技术问题（technical）：产品使用、故障报修、功能咨询
    - 销售问题（sales）：价格咨询、产品对比、购买流程  
    - 投诉问题（complaint）：服务不满、退款申请、质量问题
    
    同时评估问题的紧急程度：
    - 低（low）：一般咨询、非紧急问题
    - 中（medium）：需要尽快处理的问题  
    - 高（high）：严重影响使用、紧急故障、重大投诉
    
    用户问题：{user_question}
    
    请以以下格式回复：
    类型：[technical/sales/complaint]
    紧急程度：[low/medium/high]
    """
    
    response = model.invoke([{"role": "user", "content": classification_prompt}])
    result = response.content.strip()
    
    # 解析结果
    question_type = None
    urgency_level = None
    
    lines = result.split('\n')
    for line in lines:
        if line.startswith('类型：'):
            type_str = line.replace('类型：', '').strip().lower()
            if type_str in ['technical', 'sales', 'complaint']:
                question_type = type_str
        elif line.startswith('紧急程度：'):
            urgency_str = line.replace('紧急程度：', '').strip().lower()
            if urgency_str in ['low', 'medium', 'high']:
                urgency_level = urgency_str
    
    # 设置默认值
    if not question_type:
        question_type = "technical"  # 默认技术问题
    if not urgency_level:
        urgency_level = "medium"  # 默认中等紧急
    
    return {
        **state,
        "question_type": question_type,
        "urgency_level": urgency_level
    }


def route_decision(state: CustomerServiceState) -> str:
    """路由决策函数，决定下一个处理节点"""
    question_type = state["question_type"]
    
    # 根据问题类型路由到不同的处理节点
    route_mapping = {
        "technical": "technical_support",
        "sales": "sales_consultant", 
        "complaint": "customer_relations"
    }
    
    return route_mapping.get(question_type, "technical_support")


def technical_support(state: CustomerServiceState) -> CustomerServiceState:
    """技术支持团队处理"""
    user_question = state["user_question"]
    
    response_prompt = f"""
    你是一名专业的技术支持工程师。请针对以下技术问题提供专业、详细的解决方案：
    
    用户问题：{user_question}
    
    请提供：
    1. 问题分析
    2. 具体的解决步骤
    3. 预防措施建议
    4. 联系方式（如果需要进一步协助）
    
    回复要专业、清晰、有帮助。
    """
    
    response = model.invoke([{"role": "user", "content": response_prompt}])
    
    return {
        **state,
        "handler": "技术支持团队",
        "response": response.content
    }


def sales_consultant(state: CustomerServiceState) -> CustomerServiceState:
    """销售顾问团队处理"""
    user_question = state["user_question"]
    
    response_prompt = f"""
    你是一名专业的销售顾问。请针对以下销售咨询提供专业、热情的服务：
    
    用户问题：{user_question}
    
    请提供：
    1. 产品信息介绍
    2. 价格方案说明
    3. 优惠活动信息
    4. 购买流程指导
    
    回复要热情、专业、有说服力。
    """
    
    response = model.invoke([{"role": "user", "content": response_prompt}])
    
    return {
        **state,
        "handler": "销售顾问团队", 
        "response": response.content
    }


def customer_relations(state: CustomerServiceState) -> CustomerServiceState:
    """客户关系团队处理"""
    user_question = state["user_question"]
    
    response_prompt = f"""
    你是一名专业的客户关系专员。请针对以下投诉问题提供专业、诚恳的解决方案：
    
    用户问题：{user_question}
    
    请提供：
    1. 诚恳的道歉
    2. 问题解决方案
    3. 补偿措施（如适用）
    4. 改进承诺
    
    回复要诚恳、专业、有同理心。
    """
    
    response = model.invoke([{"role": "user", "content": response_prompt}])
    
    return {
        **state,
        "handler": "客户关系团队",
        "response": response.content
    }


def quality_check(state: CustomerServiceState) -> CustomerServiceState:
    """质量检查节点"""
    user_question = state["user_question"]
    response = state["response"]
    question_type = state["question_type"]
    
    # 使用 LLM 评估回复质量
    quality_prompt = f"""
    请评估以下客服回复的质量：
    
    问题类型：{question_type}
    用户问题：{user_question}
    客服回复：{response}
    
    请从以下维度评分（满分10分）：
    - 相关性：回复是否针对问题
    - 专业性：是否符合专业标准
    - 完整性：是否覆盖问题要点
    - 语气：是否恰当友好
    
    请给出一个综合评分（0-10分，可带小数）：
    """
    
    quality_response = model.invoke([{"role": "user", "content": quality_prompt}])
    
    # 尝试从回复中提取分数
    try:
        # 简单的分数提取逻辑
        content = quality_response.content
        for word in content.split():
            try:
                score = float(word)
                if 0 <= score <= 10:
                    quality_score = score
                    break
            except ValueError:
                continue
        else:
            quality_score = 8.5  # 默认分数
    except:
        quality_score = 8.5
    
    return {
        **state,
        "quality_score": quality_score
    }


def create_customer_service_workflow():
    """创建智能客服工作流"""
    
    # 创建状态图
    workflow = StateGraph(CustomerServiceState)
    
    # 添加节点
    workflow.add_node("receive_question", receive_question)
    workflow.add_node("classify_question", classify_question)
    workflow.add_node("technical_support", technical_support)
    workflow.add_node("sales_consultant", sales_consultant)
    workflow.add_node("customer_relations", customer_relations)
    workflow.add_node("quality_check", quality_check)
    
    # 设置入口点
    workflow.set_entry_point("receive_question")
    
    # 添加边
    workflow.add_edge("receive_question", "classify_question")
    
    # 添加条件边（路由决策）
    workflow.add_conditional_edges(
        "classify_question",
        route_decision,
        {
            "technical_support": "technical_support",
            "sales_consultant": "sales_consultant", 
            "customer_relations": "customer_relations"
        }
    )
    
    # 所有处理节点都连接到质量检查
    workflow.add_edge("technical_support", "quality_check")
    workflow.add_edge("sales_consultant", "quality_check")
    workflow.add_edge("customer_relations", "quality_check")
    
    # 质量检查后结束
    workflow.add_edge("quality_check", END)
    
    return workflow.compile()


def main():
    """主函数 - 演示智能客服系统"""
    
    # 检查环境变量
    if not os.getenv("OPENAI_API_KEY"):
        print("错误：请设置 OPENAI_API_KEY 环境变量")
        print("请将 .env.example 复制为 .env 并填入您的 API 密钥")
        return
    
    # 创建工作流
    workflow = create_customer_service_workflow()
    
    # 测试用例
    test_cases = [
        "我的软件无法启动，点击图标没有反应",  # 技术问题
        "专业版和企业版有什么区别？现在有优惠吗？",  # 销售问题
        "我昨天买的产品有质量问题，要求退款！"  # 投诉问题
    ]
    
    print("=== 智能客服路由系统演示 ===\n")
    
    for i, user_question in enumerate(test_cases, 1):
        print(f"测试用例 {i}:")
        print(f"用户问题: {user_question}")
        print("-" * 50)
        
        # 初始化状态
        initial_state = {
            "messages": [{"role": "user", "content": user_question}],
            "question_id": "",
            "user_question": "",
            "question_type": None,
            "urgency_level": None,
            "handler": None,
            "response": None,
            "quality_score": None
        }
        
        # 执行工作流
        try:
            result = workflow.invoke(initial_state)
            
            # 输出结果
            print(f"问题ID: {result['question_id']}")
            print(f"类型: {'技术问题' if result['question_type'] == 'technical' else '销售问题' if result['question_type'] == 'sales' else '投诉问题'}")
            print(f"紧急程度: {'低' if result['urgency_level'] == 'low' else '中' if result['urgency_level'] == 'medium' else '高'}")
            print(f"处理团队: {result['handler']}")
            print(f"回复: {result['response'][:200]}..." if len(result['response']) > 200 else f"回复: {result['response']}")
            print(f"质量分数: {result['quality_score']:.1f}/10")
            
        except Exception as e:
            print(f"处理过程中出现错误: {e}")
        
        print("=" * 50)
        print()


if __name__ == "__main__":
    main()