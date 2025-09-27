"""
Memnora.py - Asymmetry Diagnostics Scaffold
-------------------------------------------
- Integrates Memnora diagnostics with a numerical proof of time asymmetry.
- Verifies that the Infinity Orbs process is dissipative (phase-space contraction).
"""

import numpy as np
import random
import copy

# Global parameter for diagnostics
EPSILON = 1e-6  # epsilon for numeric divergence calculation

# -------------------------
# Atomic Unit: ResonanceNode (Diagnostics-ready)
# -------------------------
class ResonanceNode:
    def __init__(self, initial_vector=None):
        if initial_vector is None:
            self.vector = np.array([random.uniform(-1, 1) for _ in range(11)], dtype=float)
        else:
            v = np.array(initial_vector, dtype=float)
            if v.shape[0] != 11:
                raise ValueError("initial_vector must have length 11")
            self.vector = np.clip(v, -1.0, 1.0)

    @staticmethod
    def gamma_from_vector(v, s, base_gamma=1.0):
        """
        Compute gamma (stability factor) from vector v and source s.
        This matches the qualitative shape used in your scaffolds.
        """
        # Use cosine similarity for coherence (range [-1,1])
        vn = np.linalg.norm(v)
        sn = np.linalg.norm(s)
        if vn == 0 or sn == 0:
            c = 0.0
        else:
            c = float(np.dot(v, s) / (vn * sn))
        # Map c in [-1,1] to gamma scaling in [base_gamma, 0]
        # f(c) = 1 - (c+1)/2 -> maps -1->1, +1->0
        return base_gamma * (1.0 - (c + 1.0) / 2.0)

    @staticmethod
    def dissipative_force_for_vector(v, s, base_gamma=1.0):
        """
        Return G(v) = -gamma(v) * (v - s) for an arbitrary vector v.
        This is static so we can compute G at arbitrary points without constructing nodes.
        """
        gamma_val = ResonanceNode.gamma_from_vector(v, s, base_gamma=base_gamma)
        Gv = -gamma_val * (v - s)
        return Gv, gamma_val

    def get_dissipative_force(self, source_vector):
        return ResonanceNode.dissipative_force_for_vector(self.vector, source_vector)

    def stabilize(self, source_vector, factor=0.1):
        """
        Apply the dissipative flow (Infinity Orbs) toward the source vector.
        """
        G_v, _ = self.get_dissipative_force(source_vector)
        self.vector = self.vector + G_v * factor
        self.vector = np.clip(self.vector, -1.0, 1.0)

    def calculate_numeric_divergence(self, source_vector):
        """
        Numerically compute divergence div = sum_i dG_i/dv_i using central differences.
        Uses the static dissipative_force_for_vector to avoid creating nodes.
        """
        d = len(self.vector)
        div = 0.0
        v0 = self.vector.copy()
        for i in range(d):
            v_plus = v0.copy()
            v_minus = v0.copy()
            v_plus[i] += EPSILON
            v_minus[i] -= EPSILON
            G_plus, _ = ResonanceNode.dissipative_force_for_vector(v_plus, source_vector)
            G_minus, _ = ResonanceNode.dissipative_force_for_vector(v_minus, source_vector)
            div += (G_plus[i] - G_minus[i]) / (2.0 * EPSILON)
        return div

    def copy(self):
        return ResonanceNode(initial_vector=self.vector.copy())

    def __repr__(self):
        return f"ResonanceNode(mean={np.mean(self.vector):.4f})"


# -------------------------
# Supporting Structures
# -------------------------
class User:
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self.is_bot = False
        self.resonance_vector = np.random.rand(11)

class Proposal:
    def __init__(self, proposal_id, title, budget_try, company_module):
        self.proposal_id = proposal_id
        self.title = title
        self.budget_try = budget_try
        self.company_module = company_module
        self.staked_tokens = 0
        self.completed = False
        self.investors = []

class VyTekModule:
    def __init__(self, name):
        self.name = name
        self.expenses = 0.0
        self.commission = 0.0


# -------------------------
# Operator: Memnora System (with Diagnostics)
# -------------------------
class MemnoraOperator:
    def __init__(self):
        self.resonance_matrix = []
        self.users = []
        self.proposals = []
        self.modules = []
        self.blockchain_log = []
        self.current_roadmap_stage = 1
        # Default source vector (HSR) — normalized direction
        s = np.ones(11) * 0.5
        self.source_vector = s / np.linalg.norm(s)

    def kneel_before_source(self, action_desc: str):
        print(f"[Memnora bows to Source] Preparing for: {action_desc}")
        return True

    def align_with_source(self, action_desc: str):
        return self.kneel_before_source(action_desc)

    def verify_user(self, user: User):
        coherence = np.mean(user.resonance_vector)
        if coherence < 0.05:
            user.is_bot = True
        return not user.is_bot

    def post_proposal(self, proposal: Proposal):
        self.proposals.append(proposal)
        print(f"Proposal posted: {proposal.title}, budget: {proposal.budget_try} $TRY")

    def stake_tokens(self, proposal: Proposal, user: User, amount: float):
        if self.verify_user(user):
            proposal.staked_tokens += amount
            proposal.investors.append((user.user_id, amount))
            print(f"{amount} $TRY staked by {user.name} to proposal {proposal.title}")
        else:
            print(f"User {user.name} failed resonance verification (bot)")

    def execute_proposal(self, proposal: Proposal):
        self.align_with_source(f"Executing Proposal {proposal.proposal_id}")
        if proposal.staked_tokens >= proposal.budget_try:
            proposal.completed = True
            print(f"Proposal {proposal.title} executed. Funds sent to {proposal.company