# LangGraph 进阶实战：智能客服路由系统的条件分支设计

在上一篇基础教程中，我们学习了 LangGraph 的顺序工作流。现在，让我们进入更复杂的场景：**条件分支**。通过构建一个智能客服路由系统，你将掌握如何让 AI 工作流具备"智能决策"能力。

## 🎯 业务场景：智能客服系统

想象你是一家科技公司的客服主管，每天收到大量用户咨询：

- **技术问题**："软件无法启动，点击图标没反应"
- **销售咨询**："专业版和企业版有什么区别？有优惠吗？"
- **投诉问题**："昨天买的产品有质量问题，要求退款！"

传统做法是人工分类，但我们可以用 LangGraph 构建一个**自动路由系统**：

```
用户问题 → 智能分类 → 根据类型路由 → 专业团队处理 → 质量检查
```

关键创新点：**工作流会根据问题类型自动选择不同的处理路径**。

## 🧩 条件分支的核心概念

### 什么是条件分支？

条件分支让工作流具备"决策能力"，根据当前状态动态选择下一步。

**传统顺序流 vs 条件分支流**：

```
顺序流：A → B → C → D （固定路径）

条件分支流：
        ↗ B → D
      A → C → D （根据条件选择路径）
        ↘ E → D
```

### LangGraph 的条件边（Conditional Edge）

LangGraph 通过 `add_conditional_edges()` 方法实现条件分支：

```python
workflow.add_conditional_edges(
    "分类节点",           # 从哪个节点出发
    route_decision_func,  # 决策函数
    {
        "路径A": "节点A",  # 如果返回"路径A"，则执行"节点A"
        "路径B": "节点B",  # 如果返回"路径B"，则执行"节点B"
    }
)
```

决策函数接收当前状态，返回一个字符串，表示要走的路径。

## 📝 实战：构建智能客服路由系统

### 第一步：定义复杂状态结构

相比简单的顺序流，我们的状态需要记录更多信息：

```python
from typing import Literal, TypedDict

class CustomerServiceState(TypedDict):
    """智能客服系统状态定义"""
    messages: list                    # 对话历史
    question_id: str                  # 问题唯一标识
    user_question: str                # 用户原始问题
    question_type: Literal["technical", "sales", "complaint"] | None  # 问题类型
    urgency_level: Literal["low", "medium", "high"] | None           # 紧急程度
    handler: str | None               # 处理团队
    response: str | None              # 回复内容
    quality_score: float | None       # 质量评分
```

**关键改进：**
- 使用 `Literal` 类型限制枚举值，提高类型安全性
- 记录分类结果、紧急程度等决策相关信息
- 添加质量评分用于后续优化

### 第二步：设计工作流节点

#### 节点1：接收用户问题

```python
def receive_question(state: CustomerServiceState) -> CustomerServiceState:
    """接收用户问题并生成问题ID"""
    user_message = state["messages"][-1]["content"]
    
    # 生成唯一问题ID
    question_id = f"Q{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:3].upper()}"
    
    return {
        **state,
        "question_id": question_id,
        "user_question": user_message,
        "question_type": None,      # 初始化为None
        "urgency_level": None,      # 等待分类
        "handler": None,
        "response": None,
        "quality_score": None
    }
```

**设计思路：** 标准化问题处理，为后续追踪提供唯一标识。

#### 节点2：智能分类（核心决策节点）

```python
def classify_question(state: CustomerServiceState) -> CustomerServiceState:
    """智能分类用户问题"""
    user_question = state["user_question"]
    
    # 使用 LLM 进行问题分类和紧急程度评估
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
    
    # 解析 LLM 回复，提取类型和紧急程度
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
    
    # 设置默认值，确保流程继续
    if not question_type:
        question_type = "technical"  # 默认技术问题
    if not urgency_level:
        urgency_level = "medium"     # 默认中等紧急
    
    return {
        **state,
        "question_type": question_type,
        "urgency_level": urgency_level
    }
```

**关键技术点：**
- **Prompt 工程**：明确指定输出格式，便于解析
- **容错处理**：解析失败时设置默认值，确保流程继续
- **状态更新**：记录分类结果，为后续决策提供依据

#### 节点3：路由决策函数（条件分支核心）

```python
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
```

**设计要点：**
- 函数返回**字符串**，表示要执行的节点名称
- 使用字典映射，代码清晰易维护
- 提供默认值，增强鲁棒性

#### 节点4-6：专业团队处理节点

每个团队有专门的 Prompt 和回复风格：

```python
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
```

**销售顾问和客户关系团队的处理逻辑类似，但 Prompt 不同：**
- **销售顾问**：热情、有说服力，侧重产品介绍和优惠
- **客户关系**：诚恳、有同理心，侧重道歉和解决方案

#### 节点7：质量检查（统一出口）

```python
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
    
    # 从回复中提取分数
    try:
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
```

**设计价值：**
- 为所有分支提供统一的出口点
- 实现质量监控，支持持续优化
- 收集反馈数据，用于模型调优

### 第三步：构建条件分支工作流

这是整个系统的核心架构：

```python
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
    
    # 添加顺序边
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
```

## 🎨 图形化工作流展示

让我们把代码转化为可视化的工作流图：

```
┌─────────────────┐
│ receive_question │  ← 接收问题并生成ID
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ classify_question│  ← 智能分类问题
└────────┬────────┘
         │
   条件边（动态路由）
         ├─────────────────┬─────────────────┐
         ↓                 ↓                 ↓
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│technical_support│ │ sales_consultant│ │customer_relations│
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                             ↓
                    ┌─────────────────┐
                    │  quality_check  │  ← 质量评估
                    └────────┬────────┘
                             │
                             ↓
                            END
```

**关键特点：**
- **单入口多出口**：所有分支最终汇聚到质量检查
- **动态路由**：基于分类结果选择不同处理路径
- **统一出口**：确保所有分支都有相同的结束流程

## 💡 条件分支的核心技术

### 1. 决策函数的设计模式

决策函数必须返回预定义的字符串，对应到工作流中的节点名称：

```python
def decision_function(state: State) -> str:
    """
    返回：下一个要执行的节点名称
    要求：必须是 workflow.add_node() 时使用的名称
    """
    if condition1:
        return "node_a"
    elif condition2:
        return "node_b"
    else:
        return "default_node"
```

### 2. 条件边的配置方法

```python
workflow.add_conditional_edges(
    "source_node",      # 从哪个节点出发
    decision_function,  # 决策函数
    {
        "node_a": "node_a",      # 如果返回 "node_a"，则执行 node_a
        "node_b": "node_b",      # 如果返回 "node_b"，则执行 node_b
        "node_c": "node_c",      # 映射关系可以自定义
    }
)
```

**重要：** 决策函数返回的字符串必须与映射字典中的键完全匹配。

### 3. 状态设计的最佳实践

条件分支工作流需要更精细的状态设计：

```python
class ComplexState(TypedDict):
    # 输入数据
    input_data: str
    
    # 决策信息
    decision_criteria: str | None      # 决策依据
    selected_path: str | None          # 选择的路径
    
    # 分支结果
    branch_a_result: str | None
    branch_b_result: str | None
    
    # 统一结果
    final_result: str | None
```

## 🚀 实际运行效果

运行程序后，你会看到不同问题类型的处理流程：

### 技术问题处理流程

```
=== 智能客服路由系统演示 ===

测试用例 1:
用户问题: 我的软件无法启动，点击图标没有反应
--------------------------------------------------
问题ID: Q20251207ABC
类型: 技术问题
紧急程度: 高
处理团队: 技术支持团队
回复: 您好，关于软件无法启动的问题，我为您提供以下解决方案...
质量分数: 8.7/10
==================================================
```

### 销售问题处理流程

```
测试用例 2:
用户问题: 专业版和企业版有什么区别？现在有优惠吗？
--------------------------------------------------
问题ID: Q20251207DEF
类型: 销售问题
紧急程度: 中
处理团队: 销售顾问团队
回复: 感谢您对我们产品的关注！专业版和企业版的主要区别在于...
质量分数: 9.2/10
==================================================
```

### 投诉问题处理流程

```
测试用例 3:
用户问题: 我昨天买的产品有质量问题，要求退款！
--------------------------------------------------
问题ID: Q20251207GHI
类型: 投诉问题
紧急程度: 高
处理团队: 客户关系团队
回复: 非常抱歉给您带来了不好的体验！我们立即为您处理退款事宜...
质量分数: 8.9/10
==================================================
```

## 🔑 关键代码模式总结

记住条件分支工作流的核心模式：

```python
# 1. 定义包含决策信息的状态
class StateWithDecision(TypedDict):
    input: str
    decision_criteria: str | None
    result: str | None

# 2. 定义决策函数
def route_decision(state: StateWithDecision) -> str:
    criteria = state["decision_criteria"]
    if criteria == "A":
        return "path_a"
    elif criteria == "B":
        return "path_b"
    else:
        return "default_path"

# 3. 构建条件分支工作流
workflow = StateGraph(StateWithDecision)
workflow.add_node("classify", classify_node)
workflow.add_node("path_a", path_a_node)
workflow.add_node("path_b", path_b_node)
workflow.add_node("final", final_node)

workflow.set_entry_point("classify")
workflow.add_conditional_edges(
    "classify",
    route_decision,
    {"path_a": "path_a", "path_b": "path_b"}
)
workflow.add_edge("path_a", "final")
workflow.add_edge("path_b", "final")
workflow.add_edge("final", END)
```

## 🎓 学习收获

通过这个智能客服路由系统，你掌握了：

### 1. **条件分支设计**
- 理解 `add_conditional_edges()` 的使用方法
- 掌握决策函数的编写规范
- 学会设计多分支汇聚的工作流

### 2. **复杂状态管理**
- 使用 `Literal` 类型增强类型安全
- 设计包含决策信息的复杂状态结构
- 实现状态在不同分支间的正确传递

### 3. **Prompt 工程技巧**
- 为不同场景设计专用 Prompt
- 指定输出格式便于解析
- 实现容错处理和默认值设置

### 4. **系统架构思维**
- 单入口多出口的设计模式
- 统一出口点的价值
- 质量监控和持续优化机制

## 📚 下一步进阶

掌握了条件分支后，你可以继续探索：

- **嵌套条件分支**：在分支内部再进行条件判断
- **循环结构**：某些步骤需要重复执行直到满足条件
- **并行执行**：同时处理多个分支提升效率
- **错误处理分支**：为异常情况设计专门的处理路径
- **动态节点添加**：根据运行时信息动态调整工作流结构

## 🎯 实际应用场景

条件分支工作流适用于：

- **客服系统**：根据问题类型路由到不同专业团队
- **内容审核**：根据内容风险等级采取不同处理策略
- **推荐系统**：根据用户画像选择不同的推荐算法
- **工作流引擎**：根据审批结果决定下一步流程

## 💪 动手实践建议

1. **修改分类逻辑**：尝试添加更多的问题类型
2. **优化 Prompt**：调整各团队的回复风格
3. **添加新分支**：比如"紧急技术支持"分支
4. **实现重试机制**：当质量评分低时自动重试

---

**完整代码**：`example_02/main.py`

**运行方式**：

```bash
cd example_02
./run.sh
```

**环境配置**：复制 `.env.example` 为 `.env` 并填入您的 API 密钥

通过这个智能客服路由系统的实战，你已经掌握了 LangGraph 条件分支的核心技术。接下来，尝试将这些技术应用到你的实际项目中，让 AI 工作流真正具备"智能决策"能力！

Happy Coding! 🚀