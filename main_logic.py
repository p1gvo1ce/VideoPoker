from kivy.properties import ListProperty, BooleanProperty, NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

from dealer import Dealer

class PokerGame(BoxLayout):
    # UI properties
    card_sources    = ListProperty(['cards/back.png'] * 5)
    held_flags      = ListProperty([False] * 5)
    chip_value      = NumericProperty(1)
    chip_count      = NumericProperty(1)
    current_bet     = NumericProperty(1)
    current_balance = NumericProperty(100)
    win_amount      = NumericProperty(0)
    combo_text      = StringProperty('')
    # display commitment and seed
    commitment_text = StringProperty('')
    seed_text       = StringProperty('')
    # action button
    action_text     = StringProperty('Раздать')
    action_disabled = BooleanProperty(False)
    bet_controls_disabled = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dealer = Dealer()
        self._row_labels = {}
        self._blink_ev = None
        self._game_active = False
        self.populate_table()

    def populate_table(self):
        grid = self.ids.table_grid
        grid.clear_widgets()
        grid.add_widget(Label(text='Комбинация', bold=True))
        grid.add_widget(Label(text='Коэфф.', bold=True))
        grid.add_widget(Widget())
        self.payouts = [
            {"name": "Royal Flush",       "coef": 250, "img": "royal_flush.png"},
            {"name": "Straight Flush",    "coef": 50,  "img": "straight_flush.png"},
            {"name": "Four of a Kind",    "coef": 25,  "img": "four_of_a_kind.png"},
            {"name": "Full House",        "coef": 9,   "img": "full_house.png"},
            {"name": "Flush",             "coef": 6,   "img": "flush.png"},
            {"name": "Straight",          "coef": 4,   "img": "straight.png"},
            {"name": "Three of a Kind",   "coef": 3,   "img": "three_of_a_kind.png"},
            {"name": "Two Pair",          "coef": 2,   "img": "two_pair.png"},
            {"name": "One Pair",          "coef": 1,   "img": "one_pair.png"},
            {"name": "High Card",         "coef": 0,   "img": "high_card.png"},
        ]
        for item in self.payouts:
            lbl_name = Label(text=item["name"])
            lbl_coef = Label(text=str(item["coef"]))
            img = Image(source=f"assets/combinations/{item['img']}", allow_stretch=True)
            grid.add_widget(lbl_name)
            grid.add_widget(lbl_coef)
            grid.add_widget(img)
            self._row_labels[item["name"]] = (lbl_name, lbl_coef)

    def _reset_table_highlight(self):
        if self._blink_ev:
            self._blink_ev.cancel()
        for lbl_name, lbl_coef in self._row_labels.values():
            lbl_name.color = [1, 1, 1, 1]
            lbl_coef.color = [1, 1, 1, 1]

    def _reveal_card(self, idx, card):
        self.card_sources[idx] = f"cards/{card.suit.lower()}_{card.rank.rank_name.lower()}.png"

    def on_action(self):
        if not self._game_active:
            self.start_round()
        else:
            self.replace_cards()

    def start_round(self):
        # show commitment, clear seed
        self.dealer = Dealer()
        self.commitment_text = self.dealer.commitment
        self.seed_text = ''
        # disable controls until end of round
        self.bet_controls_disabled = True
        self._reset_table_highlight()

        bet = self.chip_value * self.chip_count
        if self.current_balance < bet:
            print("Недостаточно средств!")
            self.bet_controls_disabled = False
            return

        self.current_balance -= bet
        # draw first five cards
        self.dealer.dealer_draw()

        # reset UI
        self.card_sources = ['cards/back.png'] * 5
        self.held_flags   = [False] * 5
        self.win_amount   = 0
        self.combo_text   = ''

        # reveal cards one by one
        for i, c in enumerate(self.dealer.hand):
            Clock.schedule_once(lambda dt, i=i, c=c: self._reveal_card(i, c), i + 1)

        self._game_active = True
        self.action_text = 'Заменить'
        self.action_disabled = False

    def replace_cards(self):
        self.action_disabled = True
        # update held flags
        for i, held in enumerate(self.held_flags):
            self.dealer.held[i] = held

        self.dealer.dealer_replace()
        self.dealer.evaluate()

        # reveal replacements
        to_reveal = [i for i, h in enumerate(self.held_flags) if not h]
        for idx in to_reveal:
            self.card_sources[idx] = 'cards/back.png'
        for j, idx in enumerate(to_reveal):
            Clock.schedule_once(lambda dt, ix=idx: self._reveal_card(ix, self.dealer.hand[ix]), j + 1)

        # finalize
        Clock.schedule_once(lambda dt: self._finalize_replace(), len(to_reveal) + 1)

    def _finalize_replace(self):
        combo = self.dealer.evaluation
        coef = next((e['coef'] for e in self.payouts if e['name'] == combo), 0)
        bet = self.chip_value * self.chip_count
        self.win_amount = coef * bet
        self.current_balance += self.win_amount
        self.combo_text = combo
        self.blink_row(combo)
        # show seed after result
        self.seed_text = self.dealer.seed
        # re-enable controls
        self.action_disabled = False
        self.bet_controls_disabled = False
        self.action_text = 'Раздать'
        self._game_active = False

    def on_hold_toggle(self, idx):
        self.held_flags[idx] = not self.held_flags[idx]

    def increase_chip_value(self):
        self.chip_value += 1
        self._update_bet()

    def decrease_chip_value(self):
        if self.chip_value > 1:
            self.chip_value -= 1
        self._update_bet()

    def increase_chip_count(self):
        self.chip_count += 1
        self._update_bet()

    def decrease_chip_count(self):
        if self.chip_count > 1:
            self.chip_count -= 1
        self._update_bet()

    def _update_bet(self):
        self.current_bet = self.chip_value * self.chip_count

    def _blink_step(self):
        name_lbl, coef_lbl = self._blink_labels
        if name_lbl.color == [1, 1, 1, 1]:
            h = get_color_from_hex('#FFAA00')
            name_lbl.color = h
            coef_lbl.color = h
        else:
            name_lbl.color = [1, 1, 1, 1]
            coef_lbl.color = [1, 1, 1, 1]

    def blink_row(self, combo_name, times=6, interval=0.5):
        if self._blink_ev:
            self._blink_ev.cancel()
        if combo_name not in self._row_labels:
            return
        self._blink_labels = self._row_labels[combo_name]
        count = {'n': 0}
        def step(dt):
            self._blink_step()
            count['n'] += 1
            if count['n'] >= times:
                lbl_name, lbl_coef = self._blink_labels
                lbl_name.color = [1, 1, 1, 1]
                lbl_coef.color = [1, 1, 1, 1]
                self._blink_ev.cancel()
        self._blink_ev = Clock.schedule_interval(step, interval)
