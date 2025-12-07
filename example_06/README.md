# Example 06: 人在环审批流程

## 复杂度
⭐⭐⭐⭐ 中级

## 需求

### 背景
实现一个支持人工审核介入的智能工作流系统。系统能够在关键决策点暂停执行，等待人工审批，根据审批结果决定后续流程。适用于需要人工监督的敏感操作场景。

### 功能需求

#### 1. 应用场景

**场景：企业采购申请系统**

完整流程包括：
1. 员工提交采购申请
2. AI 系统分析申请并生成采购方案
3. **【审批点1】** 部门主管审核采购方案
4. 如果通过 → 生成采购订单
5. **【审批点2】** 财务审核预算
6. 如果通过 → 执行采购
7. 生成采购报告

#### 2. 核心流程

**步骤1：申请提交**
- 接收采购申请信息：
  - 申请人信息
  - 物品清单
  - 预算范围
  - 紧急程度
  - 用途说明

**步骤2：方案生成**
- AI 分析申请的合理性
- 生成采购方案：
  - 推荐供应商
  - 价格估算
  - 采购时间安排
  - 风险评估
- 计算总成本和 ROI

**步骤3：主管审批（人在环1）**
- **系统暂停执行**
- 展示采购方案给主管
- 等待主管决策：
  - ✅ 批准：继续流程
  - ❌ 拒绝：流程终止
  - 🔄 修改建议：返回重新生成方案
- 主管可以添加审批意见

**步骤4：订单生成**
- 根据批准的方案生成正式订单
- 包含：
  - 供应商联系方式
  - 详细物品清单
  - 交付要求
  - 付款条款

**步骤5：财务审核（人在环2）**
- **系统再次暂停**
- 展示订单和预算分析
- 财务人员审核：
  - ✅ 批准：执行采购
  - ❌ 拒绝：流程终止
  - 📝 要求补充信息
- 记录审批意见

**步骤6：采购执行**
- 模拟发送订单给供应商
- 记录订单状态
- 安排交付跟踪

**步骤7：报告生成**
- 生成完整的采购报告
- 包含所有审批记录
- 记录时间线
- 保存到系统

#### 3. 状态管理
需要维护以下状态：
- `application`: 原始申请信息
- `proposal`: 生成的采购方案
- `approval_stage`: 当前审批阶段
- `approvals`: 审批记录列表
  - `approver`: 审批人
  - `stage`: 审批阶段
  - `decision`: 决策（approved/rejected/revision）
  - `comments`: 审批意见
  - `timestamp`: 审批时间
- `order`: 生成的订单
- `revision_count`: 修改次数
- `status`: 流程状态

### 技术要求

#### LangGraph 学习点
- **核心：掌握 Checkpointer 的使用**
- 理解 `interrupt_before` 和 `interrupt_after`
- 学习如何保存和恢复执行状态
- 掌握人工介入后的流程恢复
- 理解 `thread_id` 和会话管理
- 学习如何传递人工决策到下一步

#### 实现要点
1. **配置 Checkpointer**：
   ```python
   from langgraph.checkpoint.sqlite import SqliteSaver
   memory = SqliteSaver.from_conn_string(":memory:")
   app = workflow.compile(checkpointer=memory)
   ```

2. **设置中断点**：
   ```python
   # 在节点执行前中断
   app = workflow.compile(
       checkpointer=memory,
       interrupt_before=["supervisor_approval", "finance_approval"]
   )
   ```

3. **执行和恢复**：
   ```python
   # 第一次执行，会在中断点停止
   config = {"configurable": {"thread_id": "purchase_001"}}
   result = app.invoke(input_data, config)
   
   # 获取状态
   state = app.get_state(config)
   
   # 人工审批后，更新状态并继续
   app.update_state(config, {"approval": "approved", "comments": "同意"})
   result = app.invoke(None, config)  # 从中断点继续
   ```

### 验收标准

1. **中断机制**
   - 在指定节点正确暂停
   - 状态正确保存
   - 可以查询当前状态

2. **恢复机制**
   - 能够从中断点恢复
   - 人工决策正确传递
   - 后续流程正常执行

3. **审批逻辑**
   - 批准/拒绝/修改三种路径都能正确处理
   - 审批记录完整保存
   - 支持多次修改循环

4. **用户体验**
   - 清晰展示等待审批的内容
   - 提供简单的审批接口
   - 审批历史可追溯

### 示例输入输出

**示例1：完整流程（两次审批都通过）**

```
=== 步骤1: 提交申请 ===
申请人: 张三
部门: 技术部
申请内容: 购买10台开发服务器
预算: 50万元
紧急程度: 高

=== 步骤2: 生成方案 ===
AI 分析完成
推荐供应商: 戴尔企业服务
配置方案: [详细配置]
预估价格: 48万元
交付周期: 15天
风险评估: 低风险

=== 步骤3: 主管审批 ===
⏸️  流程已暂停，等待主管审批
审批ID: purchase_001
当前状态: 等待部门主管审批

--- 模拟主管审批 ---
审批人: 李主管
决策: ✅ 批准
意见: "配置合理，同意采购"
时间: 2024-12-07 10:30

=== 步骤4: 生成订单 ===
订单号: PO-2024-001
供应商: 戴尔企业服务
金额: 48万元
[订单详情...]

=== 步骤5: 财务审核 ===
⏸️  流程已暂停，等待财务审批
审批ID: purchase_001
当前状态: 等待财务审批

--- 模拟财务审批 ---
审批人: 王财务
决策: ✅ 批准
意见: "预算充足，可以执行"
时间: 2024-12-07 14:20

=== 步骤6: 执行采购 ===
✅ 订单已发送给供应商
预计交付时间: 2024-12-22

=== 步骤7: 生成报告 ===
采购报告已生成
流程状态: 完成
总耗时: 4小时

审批历史:
1. [10:30] 李主管 - 批准 - "配置合理，同意采购"
2. [14:20] 王财务 - 批准 - "预算充足，可以执行"
```

**示例2：主管要求修改**

```
=== 主管审批 ===
⏸️  等待审批...

--- 主管决策 ---
决策: 🔄 要求修改
意见: "预算超支，请降低配置或寻找其他供应商"

=== 返回重新生成方案 ===
AI 根据反馈重新生成...
新方案: 调整配置，降低价格到42万元

=== 再次提交主管审批 ===
⏸️  等待审批...

--- 主管决策 ---
决策: ✅ 批准
意见: "新方案可以接受"

[继续后续流程...]
```

**示例3：财务拒绝**

```
=== 财务审核 ===
⏸️  等待审批...

--- 财务决策 ---
决策: ❌ 拒绝
意见: "本季度预算已用完，建议下季度再申请"

=== 流程终止 ===
状态: 已拒绝
通知申请人: 采购申请未通过财务审批
原因: 预算不足
建议: 下季度重新申请
```

### 技术实现示例代码框架

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import TypedDict, Literal

class PurchaseState(TypedDict):
    application: dict
    proposal: dict
    approvals: list
    order: dict
    status: str

def generate_proposal(state):
    # 生成采购方案
    return {"proposal": {...}}

def create_order(state):
    # 生成订单
    return {"order": {...}}

def execute_purchase(state):
    # 执行采购
    return {"status": "completed"}

# 构建图
workflow = StateGraph(PurchaseState)
workflow.add_node("generate_proposal", generate_proposal)
workflow.add_node("supervisor_approval", lambda s: s)  # 人工节点
workflow.add_node("create_order", create_order)
workflow.add_node("finance_approval", lambda s: s)  # 人工节点
workflow.add_node("execute_purchase", execute_purchase)

# 添加边
workflow.add_edge("generate_proposal", "supervisor_approval")
workflow.add_edge("supervisor_approval", "create_order")
workflow.add_edge("create_order", "finance_approval")
workflow.add_edge("finance_approval", "execute_purchase")

workflow.set_entry_point("generate_proposal")

# 编译时设置检查点和中断
memory = SqliteSaver.from_conn_string(":memory:")
app = workflow.compile(
    checkpointer=memory,
    interrupt_before=["supervisor_approval", "finance_approval"]
)
```

### 扩展思考

完成基础需求后，可以考虑：
1. 支持多级审批链（3级以上）
2. 实现并行审批（多人会签）
3. 添加审批超时自动提醒
4. 实现审批权限管理
5. 支持审批委托（代理人）
6. 添加审批流程可视化
7. 实现审批模板（预设审批流程）
8. 支持条件审批（根据金额自动路由）
9. 添加审批历史查询和统计
10. 实现移动端审批接口
