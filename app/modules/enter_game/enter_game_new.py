"""
进入游戏模块（使用新的事件驱动系统）
"""

from app.modules.event_runner import EventRunner


class EnterGameModule:
    def __init__(self, auto, logger):
        self.auto = auto
        self.logger = logger
        self.event_runner = EventRunner(auto, logger)
        
    def run(self):
        """运行进入游戏流程"""
        # 使用事件配置文件运行
        config_path = "app/modules/event_configs/enter_game.json"
        success = self.event_runner.run(config_path)
        
        if success:
            # 确保回到主页面
            self.auto.back_to_home()
        
        return success
