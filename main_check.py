from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, ListProperty


from dealer import Dealer

# Load the KV layout
Builder.load_file('main_check.kv')


class CheckScreen(Screen):
    seed_input       = StringProperty('')
    commitment_text  = StringProperty('')
    seed_text        = StringProperty('')
    card_sources     = ListProperty(['cards/back.png'] * 5)
    held_flags       = ListProperty([False] * 5)
    combo_text       = StringProperty('')
    _dealer          = None

    def start_with_seed(self):
        """Initialize with given seed, deal 5 cards and show commitment hash."""
        # create dealer with provided seed (or random if blank)
        self._dealer = Dealer(seed=self.seed_input)
        # display commitment (hash)
        self.commitment_text = self._dealer.commitment
        # initial deal
        self._dealer.dealer_draw()
        # reset holds
        self.held_flags = [False] * 5
        # update card images
        self.update_cards()
        # clear previous result/seed
        self.combo_text = ''
        self.seed_text = ''

    def update_cards(self):
        """Set the face images for the current hand."""
        self.card_sources = [
            f"cards/{c.suit.lower()}_{c.rank.rank_name.lower()}.png"
            for c in self._dealer.hand
        ]

    def replace_with_holds(self):
        """Apply holds, draw replacements, evaluate hand, show result and seed."""
        # apply held flags
        for i, hold in enumerate(self.held_flags):
            self._dealer.held[i] = hold
        # perform replacement and evaluation
        self._dealer.dealer_replace()
        self._dealer.evaluate()
        # update card images to show new hand
        self.update_cards()
        # display combo name
        self.combo_text = self._dealer.evaluation
        # reveal actual seed
        self.seed_text = self._dealer.seed

    def on_card_hold(self, idx: int):
        """Toggle hold flag for a given card index."""
        self.held_flags[idx] = not self.held_flags[idx]

    def show_deck(self):
        """Switch to the deck view screen, passing the full deck order."""
        # copy current deck order (remaining + not yet drawn)
        full_deck = list(self._dealer.deck)  # deck after initial deal and replacements
        # navigate
        self.manager.current = 'deck'
        self.manager.get_screen('deck').set_deck(full_deck)


class DeckScreen(Screen):
    deck_data = ListProperty([])

    def set_deck(self, deck_cards):
        self.deck_data = [
            {'source': f"cards/{c.suit.lower()}_{c.rank.rank_name.lower()}.png"}
            for c in deck_cards
        ]
        self.ids.rv.data = self.deck_data

    def go_back(self):
        """Return to the check screen."""
        self.manager.current = 'check'


class MainCheckApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(CheckScreen(name='check'))
        sm.add_widget(DeckScreen(name='deck'))
        return sm


if __name__ == '__main__':
    MainCheckApp().run()
