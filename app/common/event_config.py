"""
事件驱动配置系统
用于将硬编码的事件循环转换为可配置的 JSON 格式
"""

from typing import List, Dict, Any, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field


class ActionType(str, Enum):
    """动作类型枚举"""
    SCREENSHOT = "screenshot"           # 截图
    FIND = "find"                      # 查找元素（不点击）
    CLICK = "click"                    # 点击元素
    PRESS_KEY = "press_key"            # 按键
    WAIT = "wait"                      # 等待
    GOTO = "goto"                      # 跳转到其他事件
    EXIT = "exit"                      # 退出当前模块
    LOG = "log"                        # 记录日志
    SET_FLAG = "set_flag"              # 设置标志位
    CHECK_FLAG = "check_flag"          # 检查标志位
    CONDITIONAL = "conditional"        # 条件判断
    TYPE_TEXT = "type_text"            # 输入文字
    OCR = "ocr"                        # OCR识别
    CALL_METHOD = "call_method"        # 调用方法
    INLINE_EVENT = "inline_event"      # 内联事件
    CONDITIONAL_BLOCKS = "conditional_blocks"  # 条件分支块
    
    
class ConditionType(str, Enum):
    """条件类型枚举"""
    FOUND = "found"                    # 找到元素
    NOT_FOUND = "not_found"            # 未找到元素
    FLAG_TRUE = "flag_true"            # 标志位为真
    FLAG_FALSE = "flag_false"          # 标志位为假
    TIMEOUT = "timeout"                # 超时
    ALWAYS = "always"                  # 总是执行
    OCR_CONTAINS = "ocr_contains"      # OCR结果包含特定文字
    CUSTOM = "custom"                  # 自定义条件


class ElementType(str, Enum):
    """元素类型枚举"""
    TEXT = "text"
    IMAGE = "image"
    POSITION = "position"              # 固定坐标


class CropArea(BaseModel):
    """裁剪区域配置"""
    x1: float = Field(description="左上角x坐标比例")
    y1: float = Field(description="左上角y坐标比例")
    x2: float = Field(description="右下角x坐标比例")
    y2: float = Field(description="右下角y坐标比例")
    
    def to_tuple(self) -> tuple:
        """转换为元组格式"""
        return (self.x1, self.y1, self.x2, self.y2)


class ElementConfig(BaseModel):
    """元素配置"""
    type: ElementType = Field(description="元素类型")
    target: Union[str, List[str], List[int]] = Field(description="查找目标")
    crop: Optional[CropArea] = Field(default=None, description="裁剪区域")
    threshold: Optional[float] = Field(default=0.5, description="匹配阈值")
    include: Optional[bool] = Field(default=True, description="是否包含匹配")
    extract: Optional[List[Any]] = Field(default=None, description="提取参数")
    offset: Optional[List[float]] = Field(default=None, description="点击偏移")
    

class Condition(BaseModel):
    """条件配置"""
    type: ConditionType = Field(description="条件类型")
    element: Optional[ElementConfig] = Field(default=None, description="相关元素")
    flag_name: Optional[str] = Field(default=None, description="标志位名称")
    custom_method: Optional[str] = Field(default=None, description="自定义方法名")
    params: Optional[Dict[str, Any]] = Field(default=None, description="额外参数")


class Action(BaseModel):
    """动作配置"""
    type: ActionType = Field(description="动作类型")
    element: Optional[ElementConfig] = Field(default=None, description="相关元素")
    params: Optional[Dict[str, Any]] = Field(default=None, description="动作参数")
    # 嵌套事件相关字段
    inline_event: Optional['Event'] = Field(default=None, description="内联事件")
    conditional_blocks: Optional[List['ConditionalBlock']] = Field(default=None, description="条件分支块")


class ConditionalBlock(BaseModel):
    """条件分支块"""
    conditions: List[Condition] = Field(description="分支触发条件列表")
    actions: List['Action'] = Field(description="满足条件时执行的动作列表")
    description: Optional[str] = Field(default=None, description="分支描述")
    

class Event(BaseModel):
    """事件配置"""
    id: str = Field(description="事件唯一标识")
    name: str = Field(description="事件名称")
    description: Optional[str] = Field(default=None, description="事件描述")
    timeout: Optional[float] = Field(default=30, description="事件超时时间（秒）")
    conditions: List[Condition] = Field(default_factory=list, description="触发条件列表")
    actions: List[Action] = Field(description="动作列表")
    next_event: Optional[str] = Field(default=None, description="下一个事件ID")
    on_timeout: Optional[str] = Field(default=None, description="超时跳转事件ID")
    

class EventLoop(BaseModel):
    """事件循环配置"""
    module_name: str = Field(description="模块名称")
    version: str = Field(default="1.0", description="配置版本")
    description: Optional[str] = Field(default=None, description="模块描述")
    initial_event: str = Field(description="初始事件ID")
    events: List[Event] = Field(description="事件列表")
    flags: Optional[Dict[str, bool]] = Field(default_factory=dict, description="初始标志位")
    shared_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="共享数据")
