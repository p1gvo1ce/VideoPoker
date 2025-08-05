import logging
from dataclasses import dataclass

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s %(filename)s - %(message)s',
    datefmt = '%H:%M:%S'
)

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class Rank:
    rank_name: str
    rank_value: int

@dataclass(frozen=True)
class Card:
    rank: Rank
    suit: str

    def __str__(self):
        return f"{self.rank.rank_name} {self.suit}"

RANKS: tuple[Rank, ...] = (
    Rank("2", 2),
    Rank("3", 3),
    Rank("4", 4),
    Rank("5", 5),
    Rank("6", 6),
    Rank("7", 7),
    Rank("8", 8),
    Rank("9", 9),
    Rank("10", 10),
    Rank("Jack", 11),
    Rank("Queen", 12),
    Rank("King", 13),
    Rank("Ace", 14)
)

SUITS: tuple[str, ...] = ("Hearts", "Diamonds", "Clubs", "Spades")

def create_deck() -> tuple[Card, ...]:
    deck: tuple[Card, ...] = tuple(Card(rank=rank, suit=suit) for rank in RANKS for suit in SUITS)
    logger.debug("Created deck with %d cards", len(deck))
    return  deck

if __name__ == '__main__':
    deck = create_deck()