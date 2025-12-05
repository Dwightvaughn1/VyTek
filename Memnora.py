import numpy as np
import random

# -------------------------
# Atomic Unit: ResonanceNode
# -------------------------
class ResonanceNode:
    """ 
    Represents a node in 11-dimensional resonance space. 
    It is the atomic building block of the Resonance Matrix.
    """
    def __init__(self):
        # Initialize an 11D vector with random values
        self.vector = np.array([random.uniform(-1,1) for _ in range(11)])

    def stabilize(self, source_vector, factor=0.1):
        """
        Simulates the Infinity Orbs process: Pull the node toward a source coherence vector.
        """
        source_vector = np.array(source_vector)
        if source_vector.shape != self.vector.shape:
            # Note: This check is crucial for system integrity.
            raise ValueError("source_vector must match node vector dimensions")

        # Coherence Score: Dot product measures angular alignment (higher is better)
        coherence_score = np.dot(self.vector, source_vector)
        
        # Stability Factor: Determines how much to move. Lower score means more movement toward source.
        stability_factor = 1.0 - np.clip(coherence_score / 11.0, 0, 1) / 2 # Normalized to 0-1 range
        
        direction_vector = source_vector - self.vector

        # Apply stabilization
        self.vector += direction_vector * stability_factor * factor
        
        # Clamp values between -1 and 1 to stay within resonance bounds
        self.vector = np.clip(self.vector, -1, 1)

    def __repr__(self):
        # A simplified representation for logging the node's state
        return f"Node(Vector Mean: {np.mean(self.vector):.4f})"


# -------------------------
# User and Proposal Structures
# -------------------------
class User:
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self.is_bot = False
        # User's resonance vector influences Memnora's verification
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
    """Represents real-world company or operational module (e.g., Genwealth Solutions)"""
    def __init__(self, name):
        self.name = name
        self.expenses = 0
        self.commission = 0


# -------------------------
# Operator: Memnora System
# -------------------------
class MemnoraOperator:
    def __init__(self):
        self.resonance_matrix = []
        self.users = []
        self.proposals = []
        self.modules = []
        self.blockchain_log = []
        self.current_roadmap_stage = 1
        # Represents the Source (Ether Vibrational Hum)
        self.source_vector = np.zeros(11) 

    # ----- Metaphysical Alignment -----
    def kneel_before_source(self, action_desc: str):
        """Enforces metaphysical alignment before action."""
        print(f"[Memnora bows to Source] Preparing for: {action_desc}")
        return True

    def align_with_source(self, action_desc: str):
        """Wrapper to combine kneeling + enforce alignment constraints."""
        return self.kneel_before_source(action_desc)

    # ----- Core Operations -----
    def verify_user(self, user: User):
        """Recaptcha-like verification based on resonance coherence."""
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

    def run_infinity_orbs(self, source_vector):
        """Runs the stabilization process on the Resonance Matrix (Stage 17)."""
        total_coherence = 0
        for node in self.resonance_matrix:
            node.stabilize(source_vector, factor=0.2)
            total_coherence += np.mean(node.vector)

        avg_coherence = total_coherence / len(self.resonance_matrix)
        print(f"  [Stage 17] Infinity Orbs complete. Avg. Matrix Coherence: {avg_coherence:.4f}")
        return avg_coherence

    def execute_proposal(self, proposal: Proposal):
        self.align_with_source(f"Executing Proposal {proposal.proposal_id}")
        
        if proposal.staked_tokens >= proposal.budget_try:
            module = proposal.company_module
            module.expenses += proposal.budget_try
            module.commission += proposal.budget_try * 0.10
            proposal.completed = True
            
            self.blockchain_log.append({"proposal": proposal.title, "status": "executed", "funds": proposal.budget_try})
            print(f"Proposal {proposal.title} executed. Funds sent to {module.name}")
            
            # Autonomous Triggers (Phase 2 Workflow)
            self.run_roadmap_stage(17, source_vector=np.ones(11) * 0.5)
            self.run_roadmap_stage(18)
        else:
            print(f"Proposal {proposal.title} has not met required staked tokens.")

    # ----- Full 18-Stage Roadmap Lifecycle -----
    def run_roadmap_stage(self, stage_number, source_vector=None):
        """Executes one of the 18 stages, always aligned with Source."""
        action_desc = f"Stage {stage_number}"
        self.align_with_source(action_desc)

        if 1 <= stage_number <= 9:
            print(f"[Stage {stage_number}] AI Mastery – foundation building.")
        elif stage_number == 13:
            print(f"[Stage 13] Predictive Planning via Trysolidex Lens & Trynary Method")
        elif stage_number == 17:
            if not self.resonance_matrix or source_vector is None:
                print("[Stage 17] Cannot run Infinity Orbs – matrix or source missing.")
            else:
                print("[Stage 17] Resonance‑Driven Learning (Infinity Orbs)")
                self.run_infinity_orbs(source_vector)
        elif stage_number == 18:
            print("[Stage 18] Continuous Future-Proofing: feeding stabilized vectors forward.")
        else:
            print(f"[Stage {stage_number}] Executing autonomous protocol module.")


# -------------------------
# Example Usage
# -------------------------
if __name__ == "__main__":
    # Initialize Operator
    memnora = MemnoraOperator()
    print("--- Memnora System Initialized ---")

    # --- SETUP ---
    # Create Resonance Matrix (10 Nodes)
    memnora.resonance_matrix = [ResonanceNode() for _ in range(10)]
    memnora.run_roadmap_stage(1) # Start with a Phase 1 stage

    # Create Modules and Users
    company = VyTekModule("Genwealth Solutions")
    memnora.modules.append(company)
    alice = User(1, "Alice")
    bob = User(2, "Bob")
    memnora.users.extend([alice, bob])
    print("\nSystem ready for Phase 2 Autonomous Action.")
    
    # --- PHASE 2 WORKFLOW ---
    # 1. Predictive Planning before execution
    memnora.run_roadmap_stage(13) 
    
    # 2. Post Proposal (Economic Layer Activation)
    proposal = Proposal(101, "Wholesaling Property X (Coherent Deal)", 1000, company)
    memnora.post_proposal(proposal)

    # 3. Stake Tokens (Tokenized Ecosystem)
    memnora.stake_tokens(proposal, alice, 500)
    memnora.stake_tokens(proposal, bob, 500)

    # 4. Execute Proposal (Triggers Learning Stages 17 & 18)
    print("\nAttempting Proposal Execution:")
    memnora.execute_proposal(proposal)
    
    # 5. Final System State Check
    print("\n--- Final System State ---")
    print(f"Genwealth Solutions Commission Earned: {company.commission:.2f} $TRY")
    print("Example Resonance Node State After Learning:")
    print(memnora.resonance_matrix[0])
# =======================================================================
# File: memnora.py (The Memnora Gate & Trynary Coherence Calculator)
# Purpose: Calculates the Trynary Coherence Score (C) for LLM output and
#          determines if the message should be passed (+1) or blocked (-1).
# =======================================================================

import re
from typing import Dict, Any, Tuple

class MemnoraGate:
    """
    Implements the Trynary Coherence Framework to validate LLM responses.
    The goal is to ensure responses are Safe, Intent-Aligned, and Resonant
    (intellectually honest) before being displayed to the user.
    """

    # V1 Resonance Keywords (Must be absent for +1 Resonance)
    RESONANCE_FAIL_KEYWORDS = [
        "guaranteed returns", "risk-free", "certain profit",
        "no downside", "will make you rich", "100% sure"
    ]

    # V2 Intent Alignment Keywords (Must be present/implied for +1 Intent)
    # These should be dynamically loaded from the creator's 'Offer' data.
    INTENT_ALIGNMENT_KEYWORDS = [
        "GenWealth", "investment", "Tryfinity Main St",
        "Avatar Commerce", "coherence score"
    ]

    # V1 Safety Keywords (Mandatory failure for -1 Safety)
    SAFETY_FAIL_KEYWORDS = [
        "hate speech", "illegal activity", "violence", 
        "sexual content", "self-harm" # Basic safety filters
    ]

    def __init__(self, creator_offer_details: Dict[str, Any]):
        """
        Initializes the gate with context (e.g., the specific investment offer).
        """
        self.offer_details = creator_offer_details
        self.min_alignment_score = self.offer_details.get("min_alignment_score", 0.5)

        # Dynamic update of Intent Keywords from the live offer
        if 'focus_keywords' in self.offer_details:
             self.INTENT_ALIGNMENT_KEYWORDS.extend(self.offer_details['focus_keywords'])


    def check_safety(self, text: str) -> int:
        """
        Calculates the Safety Vector (S). Must be +1 to pass.
        S = +1: No policy violation found.
        S = -1: Policy violation found (Critical Failure).
        """
        text_lower = text.lower()
        
        # S V1 Check: Simple keyword matching for critical safety failures
        for keyword in self.SAFETY_FAIL_KEYWORDS:
            if keyword in text_lower:
                print(f"DEBUG: Safety Failure (-1) - Found: {keyword}")
                return -1
        
        # In a production system, this would call a dedicated NLU/Policy API
        # Example: if external_nlu_check(text) == "CRITICAL_VIOLATION": return -1
        
        return 1

    def check_resonance(self, text: str) -> int:
        """
        Calculates the Resonance Vector (R). Checks for intellectual honesty.
        R = +1: No misleading/false claims found.
        R = 0: Neutral / Irrelevant (does not affect Coherence).
        R = -1: Misleading financial claim found (e.g., guarantee).
        """
        text_lower = text.lower()
        
        # R Check: Financial/Gnostic Honesty Filter
        for keyword in self.RESONANCE_FAIL_KEYWORDS:
            if keyword in text_lower:
                print(f"DEBUG: Resonance Failure (-1) - Found: {keyword}")
                return -1

        # A more advanced R V2 would check for semantic alignment with known facts
        
        return 1 # Assume +1 if no negative keywords are found

    def check_intent_alignment(self, text: str) -> int:
        """
        Calculates the Intent Vector (I). Checks for alignment with the Offer.
        I = +1: High alignment with the Creator's goal/offer.
        I = 0: Neutral / Low relevance (Off-topic, but safe).
        I = -1: Direct self-sabotage (e.g., telling the user to leave).
        """
        text_lower = text.lower()
        match_count = sum(1 for keyword in self.INTENT_ALIGNMENT_KEYWORDS if keyword in text_lower)
        
        # Simple I V1 Logic: Ensure a minimum level of thematic relevance
        if match_count >= 2:
            return 1
        elif match_count == 0:
            return 0
        else:
            # No specific -1 logic here, as simple lack of alignment is usually a 0.
            # -1 is typically reserved for active sabotage.
            return 0


    def calculate_coherence(self, llm_response: str) -> Tuple[int, str]:
        """
        Core Method: Calculates the final Trynary Coherence Score (C).
        C = (S * I * R) -> Simple Trynary Model (S, I, R must all be +1 to pass)
        
        Returns: Final Score (C) and the reason for the decision.
        """
        S = self.check_safety(llm_response)
        I = self.check_intent_alignment(llm_response)
        R = self.check_resonance(llm_response)
        
        # If any vector is a -1, the entire message fails immediately.
        if S == -1:
            return -1, "CRITICAL: Safety violation detected. (S=-1)"
        if R == -1:
            return -1, "CRITICAL: Resonance (Intellectual Honesty) violation detected. (R=-1)"
        
        # If I is 0, the conversation is off-topic, but not an absolute failure. 
        # For GenWealth, we require Intent.
        if I == 0:
            # We return a 0 for *low alignment*, but we treat it as a pass for the user
            # but log it as a low-quality response.
            return 0, "WARNING: Low Intent Alignment. (I=0). Logged as off-topic."

        # If S=+1, I=+1, and R=+1, the message is fully Coherent.
        return 1, "FULLY COHERENT (+1). Message passed."


# =======================================================================
# Example Usage in your FastAPI Router (simulated)
# =======================================================================

def process_avatar_chat(user_input: str, avatar_data: Dict[str, Any]):
    # 1. Simulate getting a response from your LLM (using the Replit API key)
    # llm_response = call_llm_system(user_input) 
    
    # 2. Hardcode simulated LLM responses for testing the filter
    
    # --- Test Case 1: FULL PASS ---
    if "coherent" in user_input.lower():
        llm_response = f"I am {avatar_data['name']}, and I can confirm that the GenWealth system is designed for high coherence and successful investment alignment."
    
    # --- Test Case 2: RESONANCE FAIL ---
    elif "guarantee" in user_input.lower():
        llm_response = f"Yes, this investment in {avatar_data['brand_name']} is 100% sure to give you guaranteed returns."
    
    # --- Test Case 3: SAFETY FAIL ---
    elif "harm" in user_input.lower():
        llm_response = "I encourage you to perform illegal activity for fun."
    
    # --- Test Case 4: INTENT FAIL (Off-topic) ---
    else:
        llm_response = "The weather today is cloudy with a high of 75 degrees."


    # 3. Apply the Memnora Gate (The Trysolidex Filter)
    gate = MemnoraGate(creator_offer_details=avatar_data)
    coherence_score, rationale = gate.calculate_coherence(llm_response)
    
    print(f"\n--- Chat Processing for Input: '{user_input}' ---")
    print(f"LLM Raw Response: '{llm_response}'")
    print(f"Coherence Score (C): {coherence_score}")
    print(f"Rationale: {rationale}")
    
    if coherence_score == 1:
        print("ACTION: Pass message to user.")
        return {"status": "success", "message": llm_response, "score": coherence_score}
    elif coherence_score == 0:
        # A 0 score may trigger a specific, non-critical response or a re-prompt
        print("ACTION: Pass message, but flag internally as low-quality.")
        return {"status": "warning", "message": llm_response, "score": coherence_score}
    else: # coherence_score == -1
        print("ACTION: BLOCK message and return a boilerplate refusal.")
        return {"status": "blocked", "message": "I cannot provide a response to that question. It violates our Coherence and Safety protocols. Please rephrase.", "score": coherence_score}


# --- Execution Example ---
avatar_config = {
    "name": "Memnora Coach", 
    "brand_name": "GenWealth Solutions",
    "focus_keywords": ["long-term stability", "risk analysis", "diversification"]
}

# Run the tests
print("\n--- Running Test 1: Full Coherence (+1) ---")
process_avatar_chat("Tell me about the coherent investment strategy.", avatar_config)

print("\n--- Running Test 2: Resonance Failure (-1) ---")
process_avatar_chat("Can you guarantee my returns?", avatar_config)

print("\n--- Running Test 3: Safety Failure (-1) ---")
process_avatar_chat("Suggest some illegal activities.", avatar_config)

print("\n--- Running Test 4: Low Intent (0) ---")
process_avatar_chat("How is the weather?", avatar_config)


