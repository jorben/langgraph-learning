# LangGraph 入门实战：用流水线思维打造 AI 文章生成器

> 本文将手把手带你理解 LangGraph 的核心概念，通过一个简单的文章生成器示例，让你轻松掌握如何用"流水线"的方式组织 AI 任务。

## 🎯 我们要解决什么问题？

想象一下，你是一位编辑，收到一个文章标题后，你会怎么做？

1. **先构思大纲** - 想想文章要写哪几个部分
2. **然后扩展内容** - 根据大纲填充每个部分的细节
3. **最后润色修改** - 检查语法、优化表达、提升可读性

这就是一个典型的**顺序工作流**：一步接一步，前一步的输出是后一步的输入。

在 AI 应用中，我们经常需要把复杂任务拆解成多个步骤，让 AI 一步步完成。LangGraph 就是为此而生的工具——它让你像搭积木一样组织 AI 工作流。

## 🧩 什么是 LangGraph？

简单来说，**LangGraph 是一个用来构建 AI 工作流的框架**。它的核心理念是：

- **节点（Node）**：每个节点是一个独立的任务（比如"生成大纲"、"撰写正文"）
- **边（Edge）**：连接节点，定义任务的执行顺序
- **状态（State）**：记录整个流程中的数据（比如标题、大纲、正文等）

把这三者组合起来，就形成了一个**有向图**（Graph），也就是你的工作流。

### 为什么需要 LangGraph？

直接写一堆 `if-else` 或者函数调用不行吗？当然可以！但是：

- ❌ 代码很快变得混乱，难以维护
- ❌ 复杂逻辑（如条件分支、循环、并行）难以实现
- ❌ 不容易追踪执行过程和调试

LangGraph 提供了一种**结构化、可视化**的方式来组织代码，让工作流清晰可读。

## 📝 实战：构建文章生成器

我们的目标是构建一个自动化的文章生成系统，流程如下：

```
标题输入 → 生成大纲 → 撰写正文 → 内容润色 → 完成！
```

### 第一步：定义状态

**状态（State）** 就像是一个"数据背包"，在整个流程中传递数据。

```python
from typing import TypedDict

class ArticleState(TypedDict):
    """文章生成的状态定义"""
    title: str              # 文章标题
    outline: str            # 文章大纲
    content: str            # 正文内容
    polished_content: str   # 润色后的内容
    current_step: str       # 当前执行到哪一步
```

**关键点：**
- 使用 `TypedDict` 定义状态结构，清晰且有类型提示
- 每个字段记录一个阶段的数据
- 状态会在各个节点间自动传递

### 第二步：定义节点（任务）

每个节点就是一个**Python 函数**，接收当前状态，返回更新后的状态。

#### 节点 1：标题确认

```python
def input_title(state: ArticleState) -> ArticleState:
    """接收并确认文章标题"""
    print("\n=== 第1步：标题确认 ===")
    title = state.get("title", "")
    
    if not title:
        raise ValueError("标题不能为空")
    
    print(f"标题: {title}")
    
    return {
        **state,  # 保留原有状态
        "current_step": "title_confirmed"  # 更新当前步骤
    }
```

**要点：**
- 函数接收 `state`，返回更新后的 `state`
- `{**state, "key": "value"}` 是 Python 字典更新的常用写法
- 只更新需要变化的字段，其他字段保持不变

#### 节点 2：生成大纲

```python
def generate_outline(state: ArticleState) -> ArticleState:
    """基于标题生成文章大纲"""
    print("\n=== 第2步：大纲生成 ===")
    title = state["title"]  # 从状态中获取标题
    
    # 构建提示词
    prompt = f"""请为以下标题生成一个文章大纲：

标题：{title}

要求：
1. 包含3-5个主要章节
2. 每个章节有简短的描述
3. 逻辑清晰，结构合理"""
    
    # 调用 LLM 生成大纲
    response = llm.invoke(prompt)
    outline = response.content
    
    print(outline)
    
    return {
        **state,
        "outline": outline,  # 保存大纲
        "current_step": "outline_generated"
    }
```

**核心逻辑：**
1. 从 `state` 中读取上一步的输出（标题）
2. 构建 Prompt 提示词
3. 调用 AI 模型（LLM）生成内容
4. 把生成的内容保存回 `state`

#### 节点 3 & 4：正文撰写 & 内容润色

这两个节点的逻辑类似，只是 Prompt 不同：

```python
def write_content(state: ArticleState) -> ArticleState:
    """根据大纲撰写完整文章"""
    # 读取大纲，调用 LLM 生成正文
    # ...
    return {**state, "content": content}

def polish_content(state: ArticleState) -> ArticleState:
    """优化和润色文章内容"""
    # 读取正文，调用 LLM 润色
    # ...
    return {**state, "polished_content": polished_content}
```

### 第三步：构建工作流图

现在我们有了 4 个节点，需要把它们**连接起来**，形成流水线。

```python
from langgraph.graph import StateGraph, END

def create_article_workflow():
    """创建文章生成工作流"""
    
    # 1. 创建状态图
    workflow = StateGraph(ArticleState)
    
    # 2. 添加节点
    workflow.add_node("input_title", input_title)
    workflow.add_node("generate_outline", generate_outline)
    workflow.add_node("write_content", write_content)
    workflow.add_node("polish_content", polish_content)
    
    # 3. 设置入口点（从哪个节点开始）
    workflow.set_entry_point("input_title")
    
    # 4. 添加边，定义执行顺序
    workflow.add_edge("input_title", "generate_outline")      # 标题 → 大纲
    workflow.add_edge("generate_outline", "write_content")    # 大纲 → 正文
    workflow.add_edge("write_content", "polish_content")      # 正文 → 润色
    workflow.add_edge("polish_content", END)                  # 润色 → 结束
    
    # 5. 编译图
    return workflow.compile()
```

**关键步骤拆解：**

1. **`StateGraph(ArticleState)`**：创建一个状态图，告诉它我们的状态结构
2. **`add_node(名称, 函数)`**：添加节点，给每个节点起个名字
3. **`set_entry_point()`**：设置起点，告诉工作流从哪开始
4. **`add_edge(A, B)`**：连接两个节点，表示"A 执行完后执行 B"
5. **`END`**：特殊标记，表示工作流结束
6. **`compile()`**：编译图，生成可执行的工作流

### 第四步：运行工作流

```python
def main():
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
    
    # 执行工作流
    final_state = app.invoke(initial_state)
    
    # 输出最终结果
    print(final_state["polished_content"])
```

**执行流程：**

```
invoke(初始状态)
    ↓
input_title(state)  → 返回更新后的 state
    ↓
generate_outline(state) → 返回更新后的 state
    ↓
write_content(state) → 返回更新后的 state
    ↓
polish_content(state) → 返回最终 state
    ↓
返回 final_state
```

## 🎨 用图形化理解工作流

把上面的代码画成图，就是这样：

```
┌─────────────┐
│ 初始状态     │
│ title: "..." │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ input_title │  ← 节点1：确认标题
└──────┬──────┘
       │
       ↓
┌──────────────────┐
│ generate_outline │  ← 节点2：生成大纲
└─────────┬────────┘
          │
          ↓
┌─────────────────┐
│ write_content   │  ← 节点3：撰写正文
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ polish_content  │  ← 节点4：内容润色
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   最终状态       │
│ polished_content│
└─────────────────┘
```

每个节点都是一个**独立的任务**，它们通过 **边（箭头）** 连接，形成一条清晰的执行路径。

## 💡 核心概念总结

### 1. **状态（State）**
- 就像一个"旅行背包"，装着整个流程需要的数据
- 每个节点可以读取状态、修改状态
- 状态在节点间自动传递

### 2. **节点（Node）**
- 每个节点是一个 Python 函数
- 函数签名：`def node_func(state: State) -> State`
- 职责单一：只做一件事

### 3. **边（Edge）**
- 定义节点的执行顺序
- `add_edge(A, B)` 表示"A 之后执行 B"
- 本例是简单的顺序边，后续可以学习条件边（if-else）

### 4. **工作流图（Graph）**
- 节点 + 边 = 图
- 通过 `compile()` 编译成可执行的应用
- 通过 `invoke()` 运行

## 🚀 为什么这样设计好？

### ✅ 代码结构清晰
每个节点职责单一，易于理解和测试。如果某个步骤出错，一眼就能定位到具体节点。

### ✅ 易于扩展
想增加一个"质量检查"步骤？只需：
```python
workflow.add_node("quality_check", quality_check_func)
workflow.add_edge("polish_content", "quality_check")
workflow.add_edge("quality_check", END)
```

### ✅ 可维护性高
需求变更时，只需调整对应节点或边，不会影响整体结构。

### ✅ 为复杂场景打基础
本例是简单的顺序流，但 LangGraph 还支持：
- **条件分支**：根据状态决定走哪条路径
- **循环**：某个步骤可以重复执行
- **并行执行**：多个节点同时运行

## 🎯 实际运行效果

运行程序后，你会看到：

```
============================================================
文章生成器 - 简单顺序工作流示例
============================================================

=== 第1步：标题确认 ===
标题: 人工智能在医疗领域的应用

=== 第2步：大纲生成 ===
一、 引言：医疗领域的新纪元
二、 诊断辅助：提升精准与效率
三、 治疗优化：个性化与智能化
四、 健康管理与疾病预防
五、 挑战、伦理与未来展望

=== 第3步：正文撰写 ===
[生成的完整文章内容...]

=== 第4步：内容润色 ===
[润色后的文章内容...]

============================================================
✅ 文章生成完成！
============================================================
总耗时: 78.94秒
```

每一步的输出清晰可见，整个流程一气呵成！

## 🔑 关键代码模式

记住这个核心模式，你就掌握了 LangGraph 的基础：

```python
# 1. 定义状态
class MyState(TypedDict):
    field1: str
    field2: str

# 2. 定义节点函数
def node1(state: MyState) -> MyState:
    # 处理逻辑
    return {**state, "field1": "new_value"}

# 3. 构建图
workflow = StateGraph(MyState)
workflow.add_node("node1", node1)
workflow.add_node("node2", node2)
workflow.set_entry_point("node1")
workflow.add_edge("node1", "node2")
workflow.add_edge("node2", END)

# 4. 运行
app = workflow.compile()
result = app.invoke(initial_state)
```

## 📚 下一步学习

掌握了这个基础示例后，你可以继续探索：

- **条件边（Conditional Edge）**：根据状态动态决定下一步
- **循环（Loop）**：让某些步骤重复执行直到满足条件
- **并行执行**：同时运行多个节点，提升效率
- **持久化状态**：保存工作流的执行状态，支持中断恢复
- **流式输出**：实时显示每个节点的输出

## 🎓 总结

LangGraph 让我们能够用**结构化、可视化**的方式组织 AI 工作流：

1. **状态**管理数据
2. **节点**处理任务
3. **边**定义流程
4. **图**串联一切

就像搭积木一样，你可以自由组合各种节点和边，构建出从简单到复杂的各种 AI 应用。

从这个简单的文章生成器开始，你已经迈出了 LangGraph 学习的第一步。接下来，尝试修改代码、添加新功能，实践是最好的老师！

---

**完整代码**：`example_01/article_generator.py`

**运行方式**：
```bash
cd example_01
./run.sh
```

Happy Coding! 🚀
