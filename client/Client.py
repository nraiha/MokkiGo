import curses

from Menu import Menu
from InputHandler import InputHandler

from Visit import Visit
from Mokki import Mokki
from Item import Item
from Participant import Participant



class Client(Menu):
    def __init__(self, screen, url):
        # Hide cursor
        curses.curs_set(0)

        self._screen = screen
        self._ih = InputHandler()
        self._url = url + 'api/'

        Menu.__init__(self)

        self._visit = Visit(self._screen, self._ih, self._url)
        self._mokki = Mokki(self._screen, self._ih, self._url)
        self._item = Item(self._screen, self._ih, self._url)
        self._par = Participant(self._screen, self._ih, self._url)

        self._items = [
                ("Visit", self._visit.main),
                ("Mokki", self._mokki.main),
                ("Item", self._item.main),
                ("Participant", self._par.main)
        ]

        self.main()

    def main(self):

        while self.menu(self._items, "MokkiGo Client"):
            pass


if __name__ == '__main__':
    try:
        import os
        url = 'http://127.0.0.1:5000/'
        if os.path.exists('log.txt'):
            os.remove('log.txt')
        curses.wrapper(Client, url)
    except KeyboardInterrupt:
        print("Byebye")
