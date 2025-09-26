from vytek_module import VyTekModule

class TRYFINITY(VyTekModule):
    def __init__(self):
        super().__init__("TRYFINITY")
        self.token_ledger = {}

    def transfer_tokens(self, from_user, to_user, amount):
        self.token_ledger[from_user] = self.token_ledger.get(from_user, 0) - amount
        self.token_ledger[to_user] = self.token_ledger.get(to_user, 0) + amount
        print(f"[TRYFINITY] Transferred {amount} $TRY from {from_user} to {to_user}")