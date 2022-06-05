import curses

from Menu import Menu
from Visit import Visit
from InputHandler import InputHandler

from utils import _pass, debug_print


class Client(Menu):
    def __init__(self, screen, url):
        # Hide cursor
        curses.curs_set(0)

        self._screen = screen
        self._ih = InputHandler()
        self._url = url + 'api/'

        Menu.__init__(self)

        self._visit = Visit(self._screen, self._ih, self._url)
        # self._mokki = Mokki()
        # self._item = Item()
        # self._par = Participant()

        self._items = [
                ("Visit", self._visit.main),
                ("Mokki", _pass),
                ("Item", _pass),
                ("Participant", _pass)
        ]

        self.main()

    def main(self):

        while self.menu(self._items, "MokkiGo Client"):
            pass
