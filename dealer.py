import random
import logging
from collections import Counter

from deck_manager import Card,  create_deck

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s %(filename)s - %(message)s',
    datefmt = '%H:%M:%S'
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
        "is_wheel": sorted_ranks == [2, 3, 4, 5, 14]  # A2345
    }

def evaluate_hand(hand: list[Card]) -> str:
    data = analyze_hand(hand)
    rc = data["rank_counts"]

    if data["is_flush"] and data["is_straight"] and max(data["ranks"]) == 14:
        return "Royal Flush"
    elif data["is_flush"] and (data["is_straight"] or data["is_wheel"]):
        return "Straight Flush"
    elif 4 in rc.values():
        return "Four of a Kind"
    elif 3 in rc.values() and 2 in rc.values():
        return "Full House"
    elif data["is_flush"]:
        return "Flush"
    elif data["is_straight"] or data["is_wheel"]:
        return "Straight"
    elif 3 in rc.values():
        return "Three of a Kind"
    elif list(rc.values()).count(2) == 2:
        return "Two Pair"
    elif 2 in rc.values():
        pair_rank = [rank for rank, count in rc.items() if count == 2][0]
        if pair_rank >= 11:
            return "One Pair"
        else:
            return "High Card"
    else:
        return "High Card"

class Dealer:
    def __init__(self):
        self.deck: list= list(create_deck())
        self.hand: list[Card]
        self.held: list[bool] = list(False for _ in range(5))
        self.evaluation: str = ""

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def dealer_draw(self):
        self.hand = list(self.deck.pop(random.randint(0, len(self.deck) - 1)) for i in range(5))
        cards = [str(card) for card in self.hand]
        logger.debug(msg=f"the dealer dealt the cards: {', '.join(cards)}\nCards in deck: {len(self.deck)}")

    def dealer_replace(self):
        for i in range(5):
            if not self.held[i]:
                self.hand[i] = self.deck.pop(random.randint(0, len(self.deck) - 1))

    def evaluate(self):
        self.evaluation = evaluate_hand(self.hand)
        logger.debug(f"Hand evaluated: {self.evaluation}")

    def __str__(self):
        return f"Dealer's hand: {', '.join(str(card) for card in self.hand)}"

if __name__ == '__main__':
    dealer = Dealer()
    dealer.shuffle_deck()

    dealer.dealer_draw()
    print(dealer)
    dealer.held = [i % 2 == 0 for i in range(5)]

    dealer.shuffle_deck()
    dealer.dealer_replace()
    print(dealer)

    dealer.evaluate()
    print(dealer.evaluation)

