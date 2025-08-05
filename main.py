import random
import logging

from kivy.config import Config
Config.set('graphics', 'width', '1600')
Config.set('graphics', 'height', '1200')

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ListProperty, BooleanProperty, NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

from dealer import Dealer

KV = '''
<PokerGame>:
    orientation: 'horizontal'
    padding: 10
    spacing: 10

    # Левая часть — таблица комбинаций и выплат
    BoxLayout:
        orientation: 'vertical'
        spacing: 10

        ScrollView:
            size_hint_y: 0.4
            do_scroll_x: False
            do_scroll_y: True

            GridLayout:
                id: table_grid
                cols: 3
                size_hint_y: None
                height: self.minimum_height
                row_default_height: '30dp'
                row_force_default: True
                spacing: 2
                padding: 2

        # Зона карт
        BoxLayout:
            size_hint_y: 0.4
            spacing: 10

            # Карта 0
            BoxLayout:
                orientation: 'vertical'
                spacing: 5
                Image:
                    source: root.card_sources[0]
                ToggleButton:
                    text: 'HOLD'
                    font_size: '20sp'
                    size_hint_y: 0.2
                    state: 'down' if root.held_flags[0] else 'normal'
                    on_press: root.on_hold_toggle(0)

            # Карта 1
            BoxLayout:
                orientation: 'vertical'
                spacing: 5
                Image:
                    source: root.card_sources[1]
                ToggleButton:
                    text: 'HOLD'
                    font_size: '20sp'
                    size_hint_y: 0.2
                    state: 'down' if root.held_flags[1] else 'normal'
                    on_press: root.on_hold_toggle(1)

            # Карта 2
            BoxLayout:
                orientation: 'vertical'
                spacing: 5
                Image:
                    source: root.card_sources[2]
                ToggleButton:
                    text: 'HOLD'
                    font_size: '20sp'
                    size_hint_y: 0.2
                    state: 'down' if root.held_flags[2] else 'normal'
                    on_press: root.on_hold_toggle(2)

            # Карта 3
            BoxLayout:
                orientation: 'vertical'
                spacing: 5
                Image:
                    source: root.card_sources[3]
                ToggleButton:
                    text: 'HOLD'
                    font_size: '20sp'
                    size_hint_y: 0.2
                    state: 'down' if root.held_flags[3] else 'normal'
                    on_press: root.on_hold_toggle(3)

            # Карта 4
            BoxLayout:
                orientation: 'vertical'
                spacing: 5
                Image:
                    source: root.card_sources[4]
                ToggleButton:
                    text: 'HOLD'
                    font_size: '20sp'
                    size_hint_y: 0.2
                    state: 'down' if root.held_flags[4] else 'normal'
                    on_press: root.on_hold_toggle(4)

        # Кнопки управления раундом
        BoxLayout:
            size_hint_y: 0.15
            spacing: 10
            Button:
                text: 'Раздать'
                font_size: '24sp'
                size_hint_y: 0.8
                on_press: root.on_draw()
            Button:
                text: 'Заменить'
                font_size: '24sp'
                size_hint_y: 0.8
                on_press: root.on_replace()

    # Правая панель — счёт, ставка, управление фишками, выигрыш
    BoxLayout:
        orientation: 'vertical'
        size_hint_x: 0.3
        spacing: 10

        Label:
            text: f"Текущий счёт: {root.current_balance}"
            font_size: '18sp'

        Label:
            text: f"Текущая ставка: {root.current_bet}"
            font_size: '18sp'

        # Стоимость фишки
        BoxLayout:
            size_hint_y: None
            height: '40dp'
            spacing: 5
            Button:
                text: '–'
                font_size: '18sp'
                on_press: root.decrease_chip_value()
            Label:
                text: f"Цена фишки: {root.chip_value}"
                font_size: '18sp'
            Button:
                text: '+'
                font_size: '18sp'
                on_press: root.increase_chip_value()

        # Количество фишек
        BoxLayout:
            size_hint_y: None
            height: '40dp'
            spacing: 5
            Button:
                text: '–'
                font_size: '18sp'
                on_press: root.decrease_chip_count()
            Label:
                text: f"Кол-во фишек: {root.chip_count}"
                font_size: '18sp'
            Button:
                text: '+'
                font_size: '18sp'
                on_press: root.increase_chip_count()

        # Выигрыш
        Label:
            id: win_label
            markup: True
            text: f"[color=000000][b]Выигрыш: {root.win_amount}[/b][/color]"
            font_size: '32sp'
            canvas.before:
                Color:
                    rgba: 1, 1, 0, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
'''

class PokerGame(BoxLayout):
    card_sources    = ListProperty(['cards/back.png'] * 5)
    held_flags      = ListProperty([False] * 5)
    chip_value      = NumericProperty(1)
    chip_count      = NumericProperty(1)
    current_bet     = NumericProperty(1)
    current_balance = NumericProperty(100)
    win_amount      = NumericProperty(0)
    combo_text      = StringProperty('')

    payouts = [
        {"name": "Royal Flush",       "coef": 250, "img": "royal_flush.png"},
        {"name": "Straight Flush",    "coef": 50,  "img": "straight_flush.png"},
        {"name": "Four of a Kind",    "coef": 25,  "img": "four_of_a_kind.png"},
        {"name": "Full House",        "coef": 9,   "img": "full_house.png"},
        {"name": "Flush",             "coef": 6,   "img": "flush.png"},
        {"name": "Straight",          "coef": 4,   "img": "straight.png"},
        {"name": "Three of a Kind",   "coef": 3,   "img": "three_of_a_kind.png"},
        {"name": "Two Pair",          "coef": 2,   "img": "two_pair.png"},
        {"name": "One Pair", "coef": 1,   "img": "one_pair.png"},
        {"name": "High Card",         "coef": 0,   "img": "high_card.png"},
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dealer      = Dealer()
        self._row_labels = {}
        self._blink_ev   = None
        self.populate_table()
        # payouts без картинок для расчёта
        self.payouts = [{"name": p["name"], "coef": p["coef"]} for p in self.payouts]

    def populate_table(self):
        grid = self.ids.table_grid
        grid.add_widget(Label(text='Комбинация', bold=True))
        grid.add_widget(Label(text='Коэфф.',      bold=True))
        grid.add_widget(Widget())
        for item in self.payouts:
            lbl_name = Label(text=item["name"])
            lbl_coef = Label(text=str(item["coef"]))
            img      = Image(source=f"assets/combinations/{item['img']}", allow_stretch=True)
            grid.add_widget(lbl_name)
            grid.add_widget(lbl_coef)
            grid.add_widget(img)
            self._row_labels[item["name"]] = (lbl_name, lbl_coef)

    def _reveal_card(self, idx: int, card):
        self.card_sources[idx] = f"cards/{card.suit.lower()}_{card.rank.rank_name.lower()}.png"

    def _finalize_replace(self):
        combo = self.dealer.evaluation
        coef  = next((e['coef'] for e in self.payouts if e['name'] == combo), 0)
        bet   = self.chip_value * self.chip_count
        self.win_amount      = coef * bet
        self.current_balance += self.win_amount
        self.combo_text      = combo
        self.blink_row(combo)

    def on_draw(self):
        bet = self.chip_value * self.chip_count
        if self.current_balance < bet:
            print("Недостаточно средств!")
            return
        self.current_balance -= bet
        self.dealer = Dealer()
        self.dealer.shuffle_deck()
        self.dealer.dealer_draw()
        self.card_sources = ['cards/back.png'] * 5
        self.held_flags   = [False] * 5
        self.dealer.held  = [False] * 5
        self.win_amount   = 0
        self.combo_text   = ''
        for i, c in enumerate(self.dealer.hand):
            Clock.schedule_once(lambda dt, i=i, c=c: self._reveal_card(i, c), i + 1)

    def on_replace(self):
        for i, f in enumerate(self.held_flags):
            self.dealer.held[i] = f
        self.dealer.dealer_replace()
        self.dealer.evaluate()

        to_reveal = [i for i, h in enumerate(self.held_flags) if not h]
        for idx in to_reveal:
            self.card_sources[idx] = 'cards/back.png'
        for j, idx in enumerate(to_reveal):
            Clock.schedule_once(lambda dt, ix=idx: self._reveal_card(ix, self.dealer.hand[ix]), j + 1)
        Clock.schedule_once(lambda dt: self._finalize_replace(), len(to_reveal) + 1)

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

class PokerApp(App):
    def build(self):
        Builder.load_string(KV)
        return PokerGame()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    PokerApp().run()
