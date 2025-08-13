import logging

from kivy.config import Config
Config.set('graphics', 'width', '1700')
Config.set('graphics', 'height', '1200')

from kivy.app import App
from kivy.lang import Builder


class PokerApp(App):
    def build(self):
        Builder.load_file('pokergame.kv')
        from main_logic import PokerGame
        return PokerGame()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    PokerApp().run()
