import curses
import requests
import os

from Menu import Menu
from utils import _pass, debug_print


class Visit(Menu):
    def __init__(self, screen, ih):
        self._items = [
                ("Get all visits", self.get_all_visits),
                ("Get a visit", self.get_visit),
                ("Post a visit", self.post_visit),
                ("Edit a visit", _pass),
                ("Delete a visit", _pass)
        ]
        self._screen = screen
        self._ih = ih

        Menu.__init__(self)

    def get_input(self, y, x, prompt):
        curses.echo()
        self._screen.addstr(y, x, prompt)
        self._screen.addstr(y+1, x, "> ")
        self._screen.refresh()
        visit = self._screen.getstr(y+1, x+2, 80)
        curses.noecho()
        return visit

    def get_visit(self):
        self.show_res_win("Get a visit")
        url = "http://127.0.0.1:5000/api"
        visit = self.get_input(7, 4, "Give visit name:")
        self._screen.refresh()
        resp = requests.get(url + "/visits/" + visit.decode())

        try:
            body = resp.json()
        except ValueError:
            self.show_res("No visit found!", 1, "Oh noes")
            return

        string = self.parse_visit(body)
        lc = string.count('\n')

        msg = "Visit: "
        self.show_res(string, lc, msg)

    @staticmethod
    def parse_visit(data):
        msg = ''
        msg += "Name of the visit: " + data['visit_name'] + os.linesep
        msg += "Name of the mokki: " + data['mokki_name'] + os.linesep
        msg += "Start date: " + data['time_start'].split('T')[0] + os.linesep
        msg += "End date: " + data['time_end'].split('T')[0] + os.linesep
        msg += os.linesep
        return msg

    def show_res(self, data, lc, msg):
        self.show_res_win(msg)

        pad = curses.newpad(lc+10, self._maxx*2)
        pad.refresh(self._pad_pos_y, self._pad_pos_x,
                    7, 4, self._pady, self._padx)

        i = 0
        for line in data.splitlines():
            pad.addstr(i, 3, line + " ")
            i += 1

        pad.refresh(self._pad_pos_y, self._pad_pos_x,
                    7, 4, self._pady, self._padx)
        self._res_win.refresh()
        curses.doupdate()

        self._ih.move_in_pad(self._res_win, pad, lc, self._maxx,
                             self._pad_pos_y, self._pad_pos_x,
                             self._pady, self._padx)

        self.hide_res_win()

    def post_visit(self):
        pass

    def get_all_visits(self):
        url = "http://127.0.0.1:5000/api"
        resp = requests.get(url + "/visits/")
        try:
            body = resp.json()
        except ValueError:
            self.show_res("No visits found!", 1, "Oh noes")
            return

        data = body["items"]
        string = ''
        for item in data:
            string += self.parse_visit(item)
        lc = string.count('\n')

        msg = "Result of the get /visits/"
        self.show_res(string, lc, msg)

    def main(self):
        while self.menu(self._items, "Visit Menu"):
            pass
