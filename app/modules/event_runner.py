"""
事件驱动运行器
用于执行 JSON 配置的事件循环
"""

import json
import time
from typing import Dict, Any, Optional, List
from pathlib import Path

from app.common.logger import logger
from app.common.config import config
from app.common.event_config import (
    EventLoop, Event, Action, Condition, 
    ActionType, ConditionType, ElementType,
    CropArea, ElementConfig
)
from app.modules.automation.timer import Timer
from app.modules.automation.automation import Automation


class EventRunner:
    """事件运行器"""
    
    def __init__(self, auto: Automation, logger_instance=None):
        self.auto = auto
        self.logger = logger_instance or logger
        self.flags: Dict[str, bool] = {}
        self.shared_data: Dict[str, Any] = {}
        self.current_event: Optional[Event] = None
        self.event_config: Optional[EventLoop] = None
        self.event_map: Dict[str, Event] = {}
        self.timers: Dict[str, Timer] = {}
        self.is_log = config.isLog.value
        
    def load_config(self, config_path: str) -> bool:
        """加载事件配置"""
        try:
            path = Path(config_path)
            if not path.exists():
                self.logger.error(f"配置文件不存在: {config_path}")
                return False
                
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.event_config = EventLoop(**data)
            
            # 初始化标志位
            self.flags = self.event_config.flags.copy()
            
            # 初始化共享数据
            self.shared_data = self.event_config.shared_data.copy()
            
            # 构建事件映射
            self.event_map = {event.id: event for event in self.event_config.events}
            
            self.logger.info(f"成功加载配置: {self.event_config.module_name} v{self.event_config.version}")
            return True
            
        except Exception as e:
            self.logger.error(f"加载配置失败: {e}")
            return False
    
    def run(self, config_path: str) -> bool:
        """运行事件循环"""
        if not self.load_config(config_path):
            return False
            
        try:
            # 从初始事件开始
            current_event_id = self.event_config.initial_event
            
            while current_event_id:
                if current_event_id not in self.event_map:
                    self.logger.error(f"未找到事件: {current_event_id}")
                    break
                    
                self.current_event = self.event_map[current_event_id]
                
                # 执行事件
                next_event_id = self._execute_event(self.current_event)
                
                if not next_event_id:
                    break
                    
                current_event_id = next_event_id
                
            self.logger.info(f"事件循环结束: {self.event_config.module_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"事件循环执行失败: {e}")
            return False
    
    def _execute_event(self, event: Event) -> Optional[str]:
        """执行单个事件"""
        self.logger.debug(f"执行事件: {event.name} ({event.id})")
        
        # 创建计时器
        timer_key = f"timer_{event.id}"
        self.timers[timer_key] = Timer(event.timeout).start()
        
        try:
            while True:
                # 检查超时
                if self.timers[timer_key].reached():
                    self.logger.warning(f"事件超时: {event.name}")
                    return event.on_timeout or None
                
                # 检查条件
                if self._check_conditions(event.conditions):
                    # 执行动作
                    result = self._execute_actions(event.actions)
                    
                    # 如果动作返回了特定的下一个事件ID
                    if isinstance(result, str):
                        return result
                    
                    # 如果是退出动作
                    if result is False:
                        return None
                    
                    # 返回配置的下一个事件
                    return event.next_event
                
                # 如果没有条件，直接执行动作
                if not event.conditions:
                    result = self._execute_actions(event.actions)
                    
                    if isinstance(result, str):
                        return result
                    
                    if result is False:
                        return None
                        
                    return event.next_event
                    
                # 短暂等待避免过于频繁的检查
                time.sleep(0.1)
                
        finally:
            # 清理计时器
            if timer_key in self.timers:
                del self.timers[timer_key]
    
    def _check_conditions(self, conditions: List[Condition]) -> bool:
        """检查条件列表"""
        if not conditions:
            return True
            
        for condition in conditions:
            if not self._check_condition(condition):
                return False
                
        return True
    
    def _check_condition(self, condition: Condition) -> bool:
        """检查单个条件"""
        try:
            if condition.type == ConditionType.FOUND:
                return self._check_element_found(condition.element)
                
            elif condition.type == ConditionType.NOT_FOUND:
                return not self._check_element_found(condition.element)
                
            elif condition.type == ConditionType.FLAG_TRUE:
                return self.flags.get(condition.flag_name, False)
                
            elif condition.type == ConditionType.FLAG_FALSE:
                return not self.flags.get(condition.flag_name, False)
                
            elif condition.type == ConditionType.ALWAYS:
                return True
                
            elif condition.type == ConditionType.OCR_CONTAINS:
                # TODO: 实现OCR包含检查
                return False
                
            elif condition.type == ConditionType.CUSTOM:
                # 调用自定义方法
                if hasattr(self, condition.custom_method):
                    method = getattr(self, condition.custom_method)
                    return method(**(condition.params or {}))
                else:
                    self.logger.warning(f"未找到自定义方法: {condition.custom_method}")
                    return False
                    
            else:
                self.logger.warning(f"未知条件类型: {condition.type}")
                return False
                
        except Exception as e:
            self.logger.error(f"检查条件失败: {e}")
            return False
    
    def _check_element_found(self, element: ElementConfig) -> bool:
        """检查元素是否存在"""
        if not element:
            return False
            
        crop = element.crop.to_tuple() if element.crop else (0, 0, 1, 1)
        
        if element.type == ElementType.TEXT:
            result = self.auto.find_element(
                target=element.target,
                find_type='text',
                crop=crop,
                threshold=element.threshold,
                include=element.include,
                extract=element.extract,
                is_log=self.is_log
            )
            return result is not None
            
        elif element.type == ElementType.IMAGE:
            result = self.auto.find_element(
                target=element.target,
                find_type='image',
                crop=crop,
                threshold=element.threshold,
                extract=element.extract,
                is_log=self.is_log
            )
            return result is not None
            
        elif element.type == ElementType.POSITION:
            # 位置类型总是返回True，因为固定坐标总是可点击
            return True
            
        else:
            self.logger.warning(f"未知元素类型: {element.type}")
            return False
    
    def _execute_actions(self, actions: List[Action]) -> Any:
        """执行动作列表"""
        for action in actions:
            result = self._execute_action(action)
            
            # 如果动作返回了特定值，中断执行
            if result is not None:
                return result
                
        return None
    
    def _execute_action(self, action: Action) -> Any:
        """执行单个动作"""
        try:
            if action.type == ActionType.SCREENSHOT:
                self.auto.take_screenshot()
                
            elif action.type == ActionType.FIND:
                self._find_element(action.element)
                
            elif action.type == ActionType.CLICK:
                self._click_element(action.element, action.params)
                
            elif action.type == ActionType.PRESS_KEY:
                key = action.params.get('key', 'esc')
                self.auto.press_key(key)
                
            elif action.type == ActionType.WAIT:
                seconds = action.params.get('seconds', 1)
                time.sleep(seconds)
                
            elif action.type == ActionType.GOTO:
                event_id = action.params.get('event_id')
                return event_id
                
            elif action.type == ActionType.EXIT:
                reason = action.params.get('reason', '')
                if reason:
                    self.logger.info(f"退出: {reason}")
                return False
                
            elif action.type == ActionType.LOG:
                message = action.params.get('message', '')
                level = action.params.get('level', 'info')
                getattr(self.logger, level)(message)
                
            elif action.type == ActionType.SET_FLAG:
                flag_name = action.params.get('flag_name')
                value = action.params.get('value', True)
                self.flags[flag_name] = value
                
            elif action.type == ActionType.TYPE_TEXT:
                text = action.params.get('text', '')
                self.auto.type_string(text)
                
            elif action.type == ActionType.OCR:
                self._perform_ocr(action.element, action.params)
                
            elif action.type == ActionType.CALL_METHOD:
                method_name = action.params.get('method_name')
                method_params = action.params.get('params', {})
                if hasattr(self.auto, method_name):
                    method = getattr(self.auto, method_name)
                    method(**method_params)
                else:
                    self.logger.warning(f"未找到方法: {method_name}")
                    
            else:
                self.logger.warning(f"未知动作类型: {action.type}")
                
        except Exception as e:
            self.logger.error(f"执行动作失败: {e}")
            
        return None
    
    def _find_element(self, element: ElementConfig) -> bool:
        """查找元素"""
        if not element:
            return False
            
        crop = element.crop.to_tuple() if element.crop else (0, 0, 1, 1)
        
        result = self.auto.find_element(
            target=element.target,
            find_type=element.type.value,
            crop=crop,
            threshold=element.threshold,
            include=element.include,
            extract=element.extract,
            is_log=self.is_log
        )
        
        return result is not None
    
    def _click_element(self, element: ElementConfig, params: Optional[Dict[str, Any]] = None) -> bool:
        """点击元素"""
        if not element:
            return False
            
        params = params or {}
        crop = element.crop.to_tuple() if element.crop else (0, 0, 1, 1)
        
        if element.type == ElementType.POSITION:
            # 固定坐标点击
            if isinstance(element.target, list) and len(element.target) == 2:
                x, y = element.target
                self.auto.click_element_with_pos((int(x), int(y)))
                return True
        else:
            # 查找并点击
            offset = tuple(element.offset) if element.offset else (0, 0)
            action = params.get('action', 'move_click')
            n = params.get('n', 3)
            
            return self.auto.click_element(
                target=element.target,
                find_type=element.type.value,
                crop=crop,
                threshold=element.threshold,
                include=element.include,
                extract=element.extract,
                action=action,
                offset=offset,
                n=n,
                is_log=self.is_log
            )
        
        return False
    
    def _perform_ocr(self, element: Optional[ElementConfig], params: Optional[Dict[str, Any]] = None) -> None:
        """执行OCR识别"""
        params = params or {}
        
        if element and element.crop:
            crop = element.crop.to_tuple()
            crop_image = self.auto.get_crop_form_first_screenshot(crop)
            self.auto.perform_ocr(
                image=crop_image,
                extract=element.extract,
                is_log=self.is_log
            )
        else:
            self.auto.perform_ocr(
                extract=params.get('extract'),
                is_log=self.is_log
            )
