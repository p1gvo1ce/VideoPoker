import uuid
import hashlib
import logging
from collections import Counter
import numpy as np

from deck_manager import Card, create_deck

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s %(filename)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def is_consecutive(ranks: list[int]) -> bool:
    return len(ranks) == 5 and max(ranks) - min(ranks) == 4

def analyze_hand(hand: list[Card]) -> dict:
    ranks = [card.rank.rank_value for card in hand]
    suits = [card.suit for card in hand]
    rank_counts = Counter(ranks)
    suit_counts = Counter(suits)
    sorted_ranks = sorted(set(ranks))
    return {
        "ranks": ranks,
        "suits": suits,
        "rank_counts": rank_counts,
        "suit_counts": suit_counts,
        "sorted_ranks": sorted_ranks,
        "is_flush": len(suit_counts) == 1,
        "is_straight": is_consecutive(sorted_ranks),
        "is_wheel": sorted_ranks == [2, 3, 4, 5, 14]
    }

def evaluate_hand(hand: list[Card]) -> str:
    d = analyze_hand(hand)
    rc = d["rank_counts"]
    if d["is_flush"] and (d["is_straight"] or d["is_wheel"]) and max(d["ranks"]) == 14:
        return "Royal Flush"
    if d["is_flush"] and (d["is_straight"] or d["is_wheel"]):
        return "Straight Flush"
    if 4 in rc.values():
        return "Four of a Kind"
    if 3 in rc.values() and 2 in rc.values():
        return "Full House"
    if d["is_flush"]:
        return "Flush"
    if d["is_straight"] or d["is_wheel"]:
        return "Straight"
    if 3 in rc.values():
        return "Three of a Kind"
    if list(rc.values()).count(2) == 2:
        return "Two Pair"
    if 2 in rc.values():
        rank = next(r for r, c in rc.items() if c == 2)
        return "One Pair" if rank >= 11 else "High Card"
    return "High Card"

class Dealer:
    def __init__(self, seed: str = None):
        # generate seed and commitment hash
        self.seed = seed or str(uuid.uuid4())
        self.commitment = hashlib.sha256(self.seed.encode()).hexdigest()
        logger.debug(f"Dealer seed: {self.seed}")
        logger.debug(f"Dealer commitment: {self.commitment}")
        # derive integer seed from SHA-256 hash for NumPy
        hash_bytes = hashlib.sha256(self.seed.encode()).digest()
        int_seed = int.from_bytes(hash_bytes[:8], 'big')
        # initialize NumPy RNG
        self.rng = np.random.default_rng(int_seed)
        # create and shuffle deck once using Fisher–Yates
        self.deck: list[Card] = list(create_deck())
        for i in range(len(self.deck)-1, 0, -1):
            j = self.rng.integers(0, i+1)
            self.deck[i], self.deck[j] = self.deck[j], self.deck[i]
        logger.debug(f"Shuffled deck with numeric seed derived from {self.seed}")
        self.hand: list[Card] = []
        self.held: list[bool] = [False] * 5
        self.evaluation: str = ""
        self.draw_index = 0

    def dealer_draw(self):
        # draw top five cards sequentially
        self.hand = []
        for _ in range(5):
            self.hand.append(self.deck[self.draw_index])
            self.draw_index += 1
        cards = [str(c) for c in self.hand]
        logger.debug(f"Dealt hand: {', '.join(cards)}")
        logger.debug(f"Cards remaining: {len(self.deck) - self.draw_index}")

    def dealer_replace(self):
        # draw replacements sequentially for unheld
        for idx, held in enumerate(self.held):
            if not held:
                self.hand[idx] = self.deck[self.draw_index]
                self.draw_index += 1
        cards = [str(c) for c in self.hand]
        logger.debug(f"Replaced hand: {', '.join(cards)}")
        logger.debug(f"Cards remaining: {len(self.deck) - self.draw_index}")

    def evaluate(self):
        self.evaluation = evaluate_hand(self.hand)
        logger.debug(f"Hand evaluated: {self.evaluation}")

    def __str__(self):
        return f"Dealer's hand: {', '.join(str(c) for c in self.hand)}"

if __name__ == '__main__':
    dealer = Dealer()
    dealer.dealer_draw()
    print(dealer)
    dealer.held = [True, False, True, False, True]
    dealer.dealer_replace()
    print(dealer)
    dealer.evaluate()
    print(dealer.evaluation)
