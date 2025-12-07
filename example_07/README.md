# Example 07: 多 Agent 协作 - 软件开发团队

## 复杂度
⭐⭐⭐⭐ 高级

## 需求

### 背景
模拟一个完整的软件开发团队，由多个专业 Agent 组成（产品经理、架构师、开发者、测试员），协同完成从需求到交付的完整软件开发流程。每个 Agent 有独特的专业能力和决策逻辑。

### 功能需求

#### 1. 团队角色定义

**Agent 1: 产品经理（Product Manager）**
- **职责**：
  - 理解用户需求
  - 编写功能规格说明
  - 定义验收标准
  - 优先级排序
- **输入**：用户原始需求
- **输出**：产品需求文档（PRD）

**Agent 2: 架构师（Architect）**
- **职责**：
  - 设计系统架构
  - 选择技术栈
  - 定义模块划分
  - 设计数据库结构
  - 评估技术风险
- **输入**：PRD
- **输出**：技术设计文档（TDD）

**Agent 3: 开发者（Developer）**
- **职责**：
  - 根据设计文档编写代码
  - 实现业务逻辑
  - 处理异常情况
  - 添加代码注释
- **输入**：TDD
- **输出**：可执行代码

**Agent 4: 测试工程师（QA Tester）**
- **职责**：
  - 设计测试用例
  - 执行代码测试
  - 发现并报告 Bug
  - 验证修复
  - 执行回归测试
- **输入**：代码 + PRD
- **输出**：测试报告

**Agent 5: 协调者（Coordinator）**
- **职责**：
  - 管理开发流程
  - 决定下一步行动
  - 处理冲突
  - 判断项目是否完成
- **输入**：所有 Agent 的输出
- **输出**：流程决策

#### 2. 核心流程

**阶段1：需求分析**
```
用户需求 → 产品经理 → PRD
```

**阶段2：架构设计**
```
PRD → 架构师 → 技术设计
```

**阶段3：开发实现**
```
技术设计 → 开发者 → 代码实现
```

**阶段4：质量测试**
```
代码 + PRD → 测试工程师 → 测试报告
```

**阶段5：问题修复循环**
```
如果有 Bug:
    测试报告 → 开发者 → 修复代码 → 测试工程师 → 新测试报告
    重复直到: 无 Bug 或达到最大迭代次数(3次)
```

**阶段6：交付**
```
协调者验证 → 生成交付包 → 项目完成
```

#### 3. 协作模式

**线性协作**：
- 产品经理 → 架构师 → 开发者 → 测试
- 严格的上下游依赖

**循环协作**：
- 开发者 ⇄ 测试工程师（Bug修复循环）
- 产品经理 ⇄ 架构师（需求澄清）

**并行协作**：
- 开发者编码的同时，测试工程师准备测试用例
- 架构师审查代码的同时，产品经理验证需求

#### 4. 状态管理

需要维护以下全局状态：

```python
class ProjectState(TypedDict):
    # 输入
    user_requirement: str
    
    # 各阶段产物
    prd: dict  # 产品需求文档
    tdd: dict  # 技术设计文档
    code: str  # 代码
    test_report: dict  # 测试报告
    
    # 流程控制
    current_stage: str  # 当前阶段
    iteration_count: int  # 迭代次数
    bugs: list  # Bug列表
    
    # 沟通记录
    messages: list  # Agent间的消息
    
    # 项目状态
    status: str  # planning/designing/coding/testing/fixing/completed/failed
```

### 技术要求

#### LangGraph 学习点
- 掌握多 Agent 的设计模式
- 理解 Agent 间的消息传递
- 学习复杂状态管理
- 掌握多节点协调
- 理解循环中的多 Agent 交互
- 学习角色系统提示词设计

#### 实现要点

1. **Agent 定义**：
```python
def create_agent(role: str, system_prompt: str):
    """创建专业 Agent"""
    def agent_node(state):
        # 使用角色特定的提示词
        # 调用 LLM 完成任务
        # 返回状态更新
        pass
    return agent_node
```

2. **协调节点**：
```python
def coordinator(state) -> str:
    """决定下一步路由"""
    if state["status"] == "testing" and state["bugs"]:
        return "developer"  # 返回修复
    elif state["status"] == "testing" and not state["bugs"]:
        return "complete"  # 测试通过
    # ... 更多逻辑
```

3. **循环控制**：
```python
def should_continue_fixing(state) -> str:
    if not state["bugs"]:
        return "complete"
    if state["iteration_count"] >= 3:
        return "give_up"
    return "fix_bugs"
```

### 验收标准

1. **角色扮演**
   - 每个 Agent 回复符合角色特点
   - 产出物符合专业标准
   - 术语使用准确

2. **协作效果**
   - Agent 间信息传递准确
   - 上下游衔接流畅
   - 能够处理冲突

3. **问题解决**
   - 能够识别和报告 Bug
   - 开发者能够修复 Bug
   - 测试能够验证修复

4. **流程完整**
   - 所有阶段都能执行
   - 循环逻辑正确
   - 最终能够交付或合理终止

### 示例输入输出

**示例：开发一个待办事项应用**

```
=== 阶段1: 需求分析 ===
[产品经理 PM-Agent]
分析用户需求: "开发一个简单的待办事项应用"

📋 产品需求文档（PRD）:
功能需求:
1. 用户可以添加待办事项
2. 用户可以标记事项为完成
3. 用户可以删除事项
4. 展示待办列表

验收标准:
- 界面简洁易用
- 数据持久化存储
- 响应时间 < 1秒

优先级: P0（核心功能）

---

=== 阶段2: 架构设计 ===
[架构师 Architect-Agent]
基于 PRD 进行技术设计...

🏗️ 技术设计文档（TDD）:
技术栈:
- 前端: React + TypeScript
- 状态管理: useState (简单应用)
- 存储: LocalStorage
- 样式: Tailwind CSS

模块划分:
1. TodoList 组件（容器）
2. TodoItem 组件
3. AddTodo 组件
4. TodoService (业务逻辑)

数据结构:
interface Todo {
  id: string;
  text: string;
  completed: boolean;
  createdAt: Date;
}

风险评估: 低风险，技术成熟

---

=== 阶段3: 代码实现 ===
[开发者 Developer-Agent]
开始编码实现...

💻 代码实现:
```typescript
// TodoApp.tsx
import React, { useState, useEffect } from 'react';

interface Todo {
  id: string;
  text: string;
  completed: boolean;
  createdAt: Date;
}

export default function TodoApp() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [input, setInput] = useState('');
  
  // 从 localStorage 加载
  useEffect(() => {
    const saved = localStorage.getItem('todos');
    if (saved) setTodos(JSON.parse(saved));
  }, []);
  
  // 保存到 localStorage
  useEffect(() => {
    localStorage.setItem('todos', JSON.stringify(todos));
  }, [todos]);
  
  const addTodo = () => {
    if (!input.trim()) return;
    const newTodo: Todo = {
      id: Date.now().toString(),
      text: input,
      completed: false,
      createdAt: new Date(),
    };
    setTodos([...todos, newTodo]);
    setInput('');
  };
  
  const toggleTodo = (id: string) => {
    setTodos(todos.map(todo => 
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  };
  
  const deleteTodo = (id: string) => {
    setTodos(todos.filter(todo => todo.id !== id));
  };
  
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">待办事项</h1>
      
      <div className="mb-4">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && addTodo()}
          placeholder="添加新任务..."
          className="border p-2 rounded"
        />
        <button onClick={addTodo} className="ml-2 bg-blue-500 text-white p-2 rounded">
          添加
        </button>
      </div>
      
      <ul>
        {todos.map(todo => (
          <li key={todo.id} className="flex items-center mb-2">
            <input
              type="checkbox"
              checked={todo.completed}
              onChange={() => toggleTodo(todo.id)}
            />
            <span className={todo.completed ? 'line-through ml-2' : 'ml-2'}>
              {todo.text}
            </span>
            <button 
              onClick={() => deleteTodo(todo.id)}
              className="ml-auto text-red-500"
            >
              删除
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

代码已完成，包含所有核心功能。

---

=== 阶段4: 质量测试 ===
[测试工程师 QA-Agent]
执行测试...

🧪 测试报告 #1:
测试用例执行结果:

✅ TC-001: 添加待办事项 - 通过
✅ TC-002: 标记完成 - 通过
❌ TC-003: 删除事项 - 失败
   Bug: 删除空文本的待办时崩溃
   
❌ TC-004: 数据持久化 - 失败
   Bug: 刷新页面后数据丢失（Date 序列化问题）
   
✅ TC-005: 空输入验证 - 通过

发现 Bug: 2个
通过率: 60%
建议: 返回开发修复

---

=== 阶段5: Bug 修复（第1轮）===
[协调者 Coordinator]
决策: 发现Bug，转交开发者修复

[开发者 Developer-Agent]
分析 Bug 并修复...

🔧 修复内容:
Bug #1: 添加边界检查
Bug #2: 修改日期序列化逻辑

```typescript
// 修复后的代码片段
useEffect(() => {
  const saved = localStorage.getItem('todos');
  if (saved) {
    const parsed = JSON.parse(saved);
    // 修复: 将字符串转回 Date 对象
    const todosWithDates = parsed.map(todo => ({
      ...todo,
      createdAt: new Date(todo.createdAt)
    }));
    setTodos(todosWithDates);
  }
}, []);

const deleteTodo = (id: string) => {
  // 修复: 添加空检查
  if (!id) return;
  setTodos(todos.filter(todo => todo.id !== id));
};
```

修复完成，提交测试。

---

=== 阶段6: 回归测试 ===
[测试工程师 QA-Agent]
执行回归测试...

🧪 测试报告 #2:
✅ TC-001: 添加待办事项 - 通过
✅ TC-002: 标记完成 - 通过
✅ TC-003: 删除事项 - 通过（已修复）
✅ TC-004: 数据持久化 - 通过（已修复）
✅ TC-005: 空输入验证 - 通过

发现 Bug: 0个
通过率: 100%
测试结论: ✅ 通过，可以发布

---

=== 阶段7: 项目交付 ===
[协调者 Coordinator]
所有测试通过，准备交付！

📦 交付清单:
- ✅ 产品需求文档
- ✅ 技术设计文档
- ✅ 源代码
- ✅ 测试报告
- ✅ 部署说明

项目状态: 🎉 完成
总迭代次数: 1次
总耗时: 约15分钟

团队协作总结:
- 产品经理: 需求清晰
- 架构师: 设计合理
- 开发者: 快速修复Bug
- 测试工程师: 发现2个关键问题
- 协调效率: 高
```

### 扩展思考

完成基础需求后，可以考虑：
1. 添加更多角色（UI设计师、DevOps工程师）
2. 实现代码审查环节（Code Review Agent）
3. 添加项目管理 Agent（进度跟踪、风险预警）
4. 实现 Agent 间的主动沟通（提问、澄清）
5. 添加知识库，Agent 可以查询历史项目
6. 实现并行开发（多个开发者同时工作）
7. 添加性能优化 Agent
8. 实现自动化部署流程
9. 添加用户体验 Agent（UX评估）
10. 支持敏捷开发模式（Sprint、Stand-up）
