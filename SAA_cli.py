from app.modules.automation.automation import Automation
from app.modules.chasm.chasm import ChasmModule
from app.modules.collect_supplies.collect_supplies import CollectSuppliesModule
from app.modules.enter_game.enter_game import EnterGameModule
from app.modules.get_reward.get_reward import GetRewardModule
from app.modules.person.person import PersonModule
from app.modules.shopping.shopping import ShoppingModule
from app.modules.use_power.use_power import UsePowerModule


class Logger:
    def info(self, msg):
        print(msg)

    def error(self, msg):
        print(f"ERROR: {msg}")

    def debug(self, msg):
        print(f"DEBUG: {msg}")

    def warn(self, msg):
        print(f"WARNING: {msg}")

if __name__ == "__main__":
    logger = Logger()
    auto = Automation('尘白禁区', 'UnrealWindow', logger)

    enter_game_module = EnterGameModule(auto, logger)
    enter_game_module.run()

    collect_supplies_module = CollectSuppliesModule(auto, logger)
    collect_supplies_module.run()

    shop_module = ShoppingModule(auto, logger)
    shop_module.run()

    user_power_module = UsePowerModule(auto, logger)
    user_power_module.run()

    person_module = PersonModule(auto, logger)
    person_module.run()

    chasm_module = ChasmModule(auto, logger)
    chasm_module.run()

    get_reward_module = GetRewardModule(auto, logger)
    get_reward_module.run()
