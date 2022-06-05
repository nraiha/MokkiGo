import curses

from curses import panel
from time import sleep


class Menu:
    def __init__(self):
        self._maxy, self._maxx = self._screen.getmaxyx()
        if self._maxy <= 10 and self._maxx <= 10:
            raise curses.error

        self._res_win = curses.newwin(self._maxy-5, self._maxx-4, 4, 2)
        self._res_win.border(0)

        self._res_panel = panel.new_panel(self._res_win)
        self._res_panel.hide()

        self._pady = self._maxy - 4
        self._padx = self._maxx - 4

        self._pad_pos_y = 0
        self._pad_pos_x = 0

        self._first_time = False

        panel.update_panels()

    def show_res_win(self, string):
        self._res_win.erase()
        self._res_win.box()
        self._res_win.addstr(1, 2, string, curses.A_BOLD)

        self._res_panel.top()
        panel.update_panels()
        self._screen.refresh()
        sleep(0.2)

    def hide_res_win(self):
        self._res_win.clear()
        self._res_panel.hide()
        panel.update_panels()
        curses.doupdate()

    def print_menu(self, pos, items):
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        h = curses.color_pair(1)
        n = curses.A_NORMAL

        y = 5  # start printing from y coordinate 5
        i = 0  # Start from pos == 1

        for idx, item in enumerate(items):
            title = item[0]
            line = "{} - {}".format(idx+1, title)

            self._screen.addstr(y, 4, line, h if pos == i else n)
            # Move to the next pos and print next title one "line" down
            i += 1
            y += 1

    def menu(self, items, title):
        if self._first_time is False:
            items.append(("Exit", "Exit"))
            self._first_time = True
        pos = 0
        x = None

        while True:
            self._screen.clear()
            self._screen.border(0)

            self._screen.addstr(2, 2, title, curses.A_STANDOUT)
            self._screen.addstr(4, 2, "Please select an action", curses.A_BOLD)

            self.print_menu(pos, items)
            self._screen.refresh()

            x = self._screen.getch()
            ret, pos = self._ih.input_handler(x, pos, items)
            if ret:
                break
