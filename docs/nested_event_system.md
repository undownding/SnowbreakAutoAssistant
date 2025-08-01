# 嵌套事件驱动系统设计文档

## 概述

为了减少对自定义方法的依赖，我们为 event_runner 设计了一个嵌套机制，允许在事件中嵌套其他事件，使配置更加灵活和模块化。

## 设计特性

### 1. 新增动作类型

在 `ActionType` 枚举中新增了两种动作类型：

- `INLINE_EVENT`: 内联事件 - 在当前事件中直接嵌套执行另一个完整的事件
- `CONDITIONAL_BLOCKS`: 条件分支块 - 支持多个条件分支的复杂逻辑

### 2. 配置结构扩展

#### Action 结构扩展
```python
class Action(BaseModel):
    type: ActionType
    element: Optional[ElementConfig] = None
    params: Optional[Dict[str, Any]] = None
    # 新增嵌套事件相关字段
    inline_event: Optional['Event'] = None
    conditional_blocks: Optional[List['ConditionalBlock']] = None
```

#### 新增 ConditionalBlock 结构
```python
class ConditionalBlock(BaseModel):
    conditions: List[Condition]  # 分支触发条件列表
    actions: List['Action']      # 满足条件时执行的动作列表
    description: Optional[str] = None  # 分支描述
```

## 使用方式

### 1. 内联事件 (inline_event)

内联事件允许在一个动作中嵌套完整的事件逻辑：

```json
{
  "type": "inline_event",
  "inline_event": {
    "id": "nested_event_id",
    "name": "嵌套事件名称",
    "description": "嵌套事件描述",
    "conditions": [...],
    "actions": [...]
  }
}
```

### 2. 条件分支块 (conditional_blocks)

条件分支块支持在一个动作中定义多个条件分支：

```json
{
  "type": "conditional_blocks",
  "conditional_blocks": [
    {
      "description": "分支1描述",
      "conditions": [...],
      "actions": [...]
    },
    {
      "description": "分支2描述", 
      "conditions": [...],
      "actions": [...]
    }
  ]
}
```

## 实现机制

### 1. 内联事件执行

```python
def _execute_inline_event(self, inline_event: Event) -> Any:
    """执行内联事件"""
    # 保存当前事件上下文
    original_event = self.current_event
    
    try:
        # 设置内联事件为当前事件
        self.current_event = inline_event
        
        # 检查内联事件的条件并执行动作
        if self._check_conditions(inline_event.conditions):
            result = self._execute_actions(inline_event.actions)
            return result
            
    finally:
        # 恢复原始事件上下文
        self.current_event = original_event
```

### 2. 条件分支块执行

```python
def _execute_conditional_blocks(self, conditional_blocks: List) -> Any:
    """执行条件分支块"""
    for block in conditional_blocks:
        # 检查分支条件
        if self._check_conditions(block.get('conditions', [])):
            # 执行分支动作
            actions = block.get('actions', [])
            if actions:
                action_objects = [Action(**action_data) for action_data in actions]
                result = self._execute_actions(action_objects)
                return result
            # 只执行第一个满足条件的分支
            break
```

## 优势

### 1. 减少自定义方法依赖

原本需要大量自定义方法处理的复杂逻辑，现在可以直接在配置中使用嵌套事件和条件分支来实现。

### 2. 配置更加直观

复杂的业务逻辑可以通过嵌套结构直接在配置文件中表达，增强了可读性。

### 3. 更好的模块化

可以将常用的逻辑封装成内联事件，在多个地方复用。

### 4. 维护性提升

配置化的逻辑更容易理解和修改，减少了代码层面的复杂性。

## 示例对比

### 原来的方式
需要大量自定义方法：
```python
def handle_maneuver_entry_logic(self):
    # 检查解锁状态
    if self.auto.find_element('解锁', 'text', ...):
        # 复杂的处理逻辑
    # 尝试点击速战
    if self.auto.click_element('速战', 'text', ...):
        # 更多处理逻辑
```

### 新的嵌套方式
在配置中直接表达：
```json
{
  "type": "conditional_blocks",
  "conditional_blocks": [
    {
      "description": "检查解锁状态",
      "conditions": [{"type": "found", "element": {...}}],
      "actions": [...]
    },
    {
      "description": "尝试点击速战", 
      "conditions": [{"type": "found", "element": {...}}],
      "actions": [...]
    }
  ]
}
```

## 向后兼容性

新的嵌套机制完全向后兼容，现有的配置文件无需修改即可继续使用。同时，自定义方法机制仍然保留，可以在需要时继续使用。

## 总结

嵌套事件机制为 event_runner 提供了更强大的配置能力，使复杂的业务逻辑可以直接在配置文件中表达，大大减少了对自定义方法的依赖，提高了系统的可维护性和扩展性。
