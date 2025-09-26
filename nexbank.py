from vytek_module import VyTekModule

class NEXBANK(VyTekModule):
    def __init__(self):
        super().__init__("NEXBANK")
        self.accounts = {}

    def create_account(self, account_id, balance=0.0):
        self.accounts[account_id] = balance
        print(f"[NEXBANK] Account created: {account_id} with balance {balance}")

    def transfer(self, from_id, to_id, amount):
        if self.accounts.get(from_id, 0) < amount:
            print(f"[NEXBANK] Insufficient funds in {from_id}")
            return False
        self.accounts[from_id] -= amount
        self.accounts[to_id] = self.accounts.get(to_id, 0) + amount
        print(f"[NEXBANK] Transferred {amount} from {from_id} to {to_id}")
        return True