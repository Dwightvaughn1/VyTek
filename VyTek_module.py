# vytek_module.py

class VyTekModule:
    """
    Base class for all VyTek Modules
    Tracks expenses, commission, and integrates with MemnoraOperator.
    """
    def __init__(self, name):
        self.name = name
        self.expenses = 0.0
        self.commission = 0.0
        self.transactions = []

    def record_expense(self, amount):
        self.expenses += amount
        print(f"[{self.name}] Recorded expense: {amount}")

    def record_commission(self, amount):
        self.commission += amount
        print(f"[{self.name}] Recorded commission: {amount}")

    def execute_module_action(self, action_name, **kwargs):
        print(f"[{self.name}] Executing action {action_name} with {kwargs}")
        # Each module will override for specific functions
        return True