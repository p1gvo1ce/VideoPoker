import random
import logging

from deck_manager import Card,  create_deck

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s %(filename)s - %(message)s',
    datefmt = '%H:%M:%S'
)

logger = logging.getLogger(__name__)



class Dealer:
    def __init__(self):
        self.deck: list= list(create_deck())
        self.hand: list[Card]
        self.held: list[bool] = list(False for _ in range(5))

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
