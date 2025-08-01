# JSON 事件驱动系统开发指南

## 目录
1. [概述](#概述)
2. [快速开始](#快速开始)
3. [JSON 配置结构](#json-配置结构)
4. [动作类型详解](#动作类型详解)
5. [条件类型详解](#条件类型详解)
6. [元素配置](#元素配置)
7. [完整示例](#完整示例)
8. [最佳实践](#最佳实践)
9. [常见问题](#常见问题)

## 概述

JSON 事件驱动系统是一个将游戏自动化流程配置化的框架。它将传统的硬编码循环转换为可配置的事件链，使得自动化脚本更易维护和扩展。

### 核心概念

- **事件 (Event)**: 自动化流程中的一个执行单元，包含条件检查和动作执行
- **条件 (Condition)**: 决定事件是否执行的判断逻辑
- **动作 (Action)**: 事件执行时的具体操作
- **事件链**: 通过 `next_event` 连接的一系列事件

## 快速开始

### 1. 创建 JSON 配置文件

在 `app/modules/event_configs/` 目录下创建新的 JSON 文件：

```json
{
  "module_name": "我的模块",
  "version": "1.0",
  "description": "模块描述",
  "initial_event": "start",
  "events": [
    {
      "id": "start",
      "name": "开始",
      "actions": [
        {
          "type": "screenshot"
        }
      ],
      "next_event": "main_logic"
    }
  ]
}
```

### 2. 创建模块类

```python
from app.modules.event_runner import EventRunner

class MyModule:
    def __init__(self, auto, logger):
        self.auto = auto
        self.logger = logger
        self.event_runner = EventRunner(auto, logger)
        
    def run(self):
        config_path = "app/modules/event_configs/my_module.json"
        return self.event_runner.run(config_path)
```

## JSON 配置结构

### 顶层结构

```json
{
  "module_name": "模块名称",          // 必填：模块的显示名称
  "version": "1.0",                  // 可选：配置版本号
  "description": "模块描述",          // 可选：模块功能描述
  "initial_event": "事件ID",          // 必填：起始事件的ID
  "flags": {                         // 可选：初始标志位
    "flag_name": false
  },
  "shared_data": {                   // 可选：共享数据
    "key": "value"
  },
  "events": []                       // 必填：事件列表
}
```

### 事件结构

```json
{
  "id": "unique_event_id",           // 必填：事件唯一标识
  "name": "事件名称",                 // 必填：事件显示名称
  "description": "事件描述",          // 可选：事件详细描述
  "timeout": 30,                     // 可选：超时时间（秒），默认30
  "conditions": [],                  // 可选：触发条件列表
  "actions": [],                     // 必填：动作列表
  "next_event": "next_event_id",     // 可选：下一个事件ID
  "on_timeout": "timeout_event_id"   // 可选：超时跳转事件ID
}
```

## 动作类型详解

### 1. screenshot - 截图

截取当前游戏画面。

```json
{
  "type": "screenshot",
  "params": {}
}
```

### 2. click - 点击元素

查找并点击指定元素。

```json
{
  "type": "click",
  "element": {
    "type": "text",                // 元素类型：text/image/position
    "target": "确定",               // 查找目标
    "crop": {                      // 查找区域（可选）
      "x1": 0.4, "y1": 0.8,
      "x2": 0.6, "y2": 0.9
    }
  },
  "params": {
    "action": "move_click",        // 点击方式（可选）
    "n": 3                         // 点击位置随机度（可选）
  }
}
```

### 3. find - 查找元素

仅查找元素，不执行点击。

```json
{
  "type": "find",
  "element": {
    "type": "text",
    "target": "游戏开始"
  }
}
```

### 4. press_key - 按键

发送键盘按键。

```json
{
  "type": "press_key",
  "params": {
    "key": "esc"                   // 按键名称
  }
}
```

### 5. wait - 等待

暂停指定时间。

```json
{
  "type": "wait",
  "params": {
    "seconds": 2                   // 等待秒数
  }
}
```

### 6. goto - 跳转事件

直接跳转到指定事件。

```json
{
  "type": "goto",
  "params": {
    "event_id": "target_event"     // 目标事件ID
  }
}
```

### 7. exit - 退出模块

结束当前模块执行。

```json
{
  "type": "exit",
  "params": {
    "reason": "任务完成"            // 退出原因（可选）
  }
}
```

### 8. log - 记录日志

输出日志信息。

```json
{
  "type": "log",
  "params": {
    "message": "开始执行任务",       // 日志内容
    "level": "info"                // 日志级别：debug/info/warning/error
  }
}
```

### 9. set_flag - 设置标志位

设置或更新标志位的值。

```json
{
  "type": "set_flag",
  "params": {
    "flag_name": "task_completed",  // 标志位名称
    "value": true                   // 标志位值
  }
}
```

### 10. type_text - 输入文字

输入指定文本。

```json
{
  "type": "type_text",
  "params": {
    "text": "要输入的文字"
  }
}
```

### 11. call_method - 调用方法

调用 automation 对象的方法。

```json
{
  "type": "call_method",
  "params": {
    "method_name": "back_to_home",   // 方法名
    "params": {}                     // 方法参数
  }
}
```

### 12. ocr - OCR识别

执行 OCR 文字识别。

```json
{
  "type": "ocr",
  "element": {
    "crop": {                        // 识别区域
      "x1": 0.4, "y1": 0.4,
      "x2": 0.6, "y2": 0.6
    }
  }
}
```

## 条件类型详解

### 1. found - 找到元素

当指定元素存在时条件成立。

```json
{
  "type": "found",
  "element": {
    "type": "text",
    "target": "开始游戏",
    "crop": {
      "x1": 0.4, "y1": 0.8,
      "x2": 0.6, "y2": 0.9
    }
  }
}
```

### 2. not_found - 未找到元素

当指定元素不存在时条件成立。

```json
{
  "type": "not_found",
  "element": {
    "type": "text",
    "target": "加载中"
  }
}
```

### 3. flag_true - 标志位为真

当指定标志位为 true 时条件成立。

```json
{
  "type": "flag_true",
  "flag_name": "login_completed"
}
```

### 4. flag_false - 标志位为假

当指定标志位为 false 时条件成立。

```json
{
  "type": "flag_false",
  "flag_name": "has_error"
}
```

### 5. always - 总是执行

条件总是成立。

```json
{
  "type": "always"
}
```

### 6. custom - 自定义条件

调用自定义方法判断条件。

```json
{
  "type": "custom",
  "custom_method": "check_game_state",
  "params": {
    "state": "ready"
  }
}
```

## 元素配置

### 文本元素

```json
{
  "type": "text",
  "target": "确定",                    // 单个文本
  // 或
  "target": ["确定", "OK", "是"],     // 多个文本（任一匹配）
  "include": true,                   // 是否包含匹配（默认true）
  "crop": {                          // 查找区域
    "x1": 0.0, "y1": 0.0,
    "x2": 1.0, "y2": 1.0
  },
  "extract": [                       // 文字提取参数（可选）
    [255, 255, 255],                 // RGB颜色
    128                              // 阈值
  ]
}
```

### 图片元素

```json
{
  "type": "image",
  "target": "app/resource/images/button.png",  // 图片路径
  "threshold": 0.8,                            // 匹配阈值（0-1）
  "crop": {
    "x1": 0.0, "y1": 0.0,
    "x2": 1.0, "y2": 1.0
  }
}
```

### 坐标元素

```json
{
  "type": "position",
  "target": [960, 540],              // [x, y] 坐标
  "offset": [10, 5]                  // 偏移量（可选）
}
```

## 完整示例

### 简单的登录流程

```json
{
  "module_name": "自动登录",
  "version": "1.0",
  "description": "处理游戏登录流程",
  "initial_event": "check_login_state",
  "flags": {
    "logged_in": false
  },
  "events": [
    {
      "id": "check_login_state",
      "name": "检查登录状态",
      "timeout": 10,
      "actions": [
        {
          "type": "screenshot"
        }
      ],
      "next_event": "handle_login"
    },
    {
      "id": "handle_login",
      "name": "处理登录",
      "conditions": [
        {
          "type": "found",
          "element": {
            "type": "text",
            "target": "开始游戏",
            "crop": {
              "x1": 0.4, "y1": 0.8,
              "x2": 0.6, "y2": 0.9
            }
          }
        }
      ],
      "actions": [
        {
          "type": "click",
          "element": {
            "type": "text",
            "target": "开始游戏",
            "crop": {
              "x1": 0.4, "y1": 0.8,
              "x2": 0.6, "y2": 0.9
            }
          }
        },
        {
          "type": "wait",
          "params": {
            "seconds": 2
          }
        },
        {
          "type": "set_flag",
          "params": {
            "flag_name": "logged_in",
            "value": true
          }
        }
      ],
      "next_event": "verify_login"
    },
    {
      "id": "verify_login",
      "name": "验证登录成功",
      "timeout": 30,
      "conditions": [
        {
          "type": "found",
          "element": {
            "type": "text",
            "target": "主界面"
          }
        }
      ],
      "actions": [
        {
          "type": "log",
          "params": {
            "message": "登录成功",
            "level": "info"
          }
        },
        {
          "type": "exit",
          "params": {
            "reason": "登录流程完成"
          }
        }
      ],
      "on_timeout": "login_failed"
    },
    {
      "id": "login_failed",
      "name": "登录失败处理",
      "actions": [
        {
          "type": "log",
          "params": {
            "message": "登录超时",
            "level": "error"
          }
        },
        {
          "type": "exit"
        }
      ]
    }
  ]
}
```

### 带循环的任务流程

```json
{
  "module_name": "批量任务处理",
  "version": "1.0",
  "initial_event": "init_tasks",
  "shared_data": {
    "tasks": ["任务1", "任务2", "任务3"],
    "current_index": 0
  },
  "events": [
    {
      "id": "init_tasks",
      "name": "初始化任务列表",
      "actions": [
        {
          "type": "call_method",
          "params": {
            "method_name": "prepare_tasks"
          }
        }
      ],
      "next_event": "process_task"
    },
    {
      "id": "process_task",
      "name": "处理单个任务",
      "conditions": [
        {
          "type": "custom",
          "custom_method": "has_more_tasks"
        }
      ],
      "actions": [
        {
          "type": "call_method",
          "params": {
            "method_name": "execute_current_task"
          }
        },
        {
          "type": "wait",
          "params": {
            "seconds": 1
          }
        }
      ],
      "next_event": "next_task"
    },
    {
      "id": "next_task",
      "name": "准备下一个任务",
      "actions": [
        {
          "type": "call_method",
          "params": {
            "method_name": "increment_task_index"
          }
        }
      ],
      "next_event": "process_task"
    }
  ]
}
```

## 最佳实践

### 1. 事件命名规范

- 使用清晰、描述性的事件ID和名称
- ID使用下划线命名法：`check_game_state`
- 名称使用中文描述：`"检查游戏状态"`

### 2. 超时设置

- 为可能阻塞的事件设置合理的超时时间
- 提供超时处理事件（`on_timeout`）
- 建议超时时间：
  - 简单检查：5-10秒
  - 复杂操作：30-60秒
  - 网络请求：60-120秒

### 3. 条件使用

- 尽量使用明确的条件，避免过于宽泛的匹配
- 多个条件时考虑优先级和性能
- 合理使用 `crop` 限制查找范围，提高效率

### 4. 错误处理

- 为关键流程提供失败处理分支
- 使用日志记录关键步骤
- 设置合理的重试机制

### 5. 模块化设计

- 将复杂流程拆分为多个小事件
- 复用通用事件（如返回主页）
- 保持单个事件的职责单一

## 常见问题

### Q1: 如何调试事件流程？

**A**: 使用以下方法：
1. 在关键事件添加日志动作
2. 使用较短的超时时间快速定位问题
3. 查看运行器的调试日志

### Q2: 如何处理动态内容？

**A**: 可以通过以下方式：
1. 使用自定义条件方法
2. 利用 OCR 识别动态文本
3. 使用标志位记录状态

### Q3: 如何优化查找速度？

**A**: 优化建议：
1. 使用 `crop` 限制查找区域
2. 设置合适的 `threshold` 值
3. 优先使用文本匹配而非图片匹配

### Q4: 如何扩展新的动作类型？

**A**: 步骤如下：
1. 在 `event_config.py` 中添加新的 ActionType
2. 在 `event_runner.py` 的 `_execute_action` 方法中实现
3. 更新文档说明

### Q5: 如何在事件间共享数据？

**A**: 使用以下机制：
1. `flags`: 布尔状态标志
2. `shared_data`: 任意类型的共享数据
3. 自定义方法读写 event_runner 的属性

## 进阶技巧

### 1. 条件组合

虽然当前实现是 AND 逻辑（所有条件都满足），但可以通过事件设计实现 OR 逻辑：

```json
{
  "id": "check_multiple_states",
  "name": "检查多个状态",
  "conditions": [
    {
      "type": "found",
      "element": {
        "type": "text",
        "target": ["状态A", "状态B", "状态C"]
      }
    }
  ]
}
```

### 2. 动态事件跳转

使用 `goto` 动作实现动态跳转：

```json
{
  "type": "goto",
  "params": {
    "event_id": "dynamic_target"
  }
}
```

### 3. 嵌套模块调用

通过 `call_method` 调用其他模块：

```json
{
  "type": "call_method",
  "params": {
    "method_name": "run_sub_module",
    "params": {
      "module": "sub_task"
    }
  }
}
```

## 总结

JSON 事件驱动系统提供了一种灵活、可维护的方式来构建游戏自动化脚本。通过合理的事件设计和配置，可以实现复杂的自动化流程，同时保持代码的清晰和可扩展性。

如有更多问题或需要特定功能支持，请参考源代码或联系开发团队。
