from vytek_module import VyTekModule

class QUANTRA(VyTekModule):
    def __init__(self):
        super().__init__("QUANTRA")
        self.procurement_orders = []

    def submit_order(self, item, quantity, cost):
        self.procurement_orders.append({"item": item, "quantity": quantity, "cost": cost})
        self.record_expense(cost)
        print(f"[QUANTRA] Order submitted: {quantity}x {item} costing {cost}")