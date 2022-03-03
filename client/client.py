import curses
import curses.panel


class MokkiClient():
    def __init__(self, screen):
        self.screen = screen
        self.main()

    def navigate(self, pos, n, item_len, x=None):
        """
        Increments the position and wraps it around if needed
        In case the key pressed was a number (1-9), sets the
        position to it.
        """
        if x:
            return int(chr(x))-1

        pos += n
        if pos < 0:
            pos = item_len - 1
        elif pos >= item_len:
            pos = 0
        return pos

    def input_handler(self, key, pos, items):
        """
        Handles the input.
        Quits the menu if q is pressed.
        Calculates the next position if j/k/up/down/1-9 is pressed
        returns True if we
        """
        if key == ord('q'):
            return True, pos

        elif key == ord('\n'):
            if pos == len(items) - 1:
                return True, pos
            else:
                items[pos][1]()

        elif key == curses.KEY_DOWN or key == ord('j'):
            pos = self.navigate(pos, 1, len(items))

        elif key == curses.KEY_UP or key == ord('k'):
            pos = self.navigate(pos, -1, len(items))

        elif key > ord('0') and key < ord(str(len(items)+1)):
            pos = self.navigate(pos, 0, len(items), x=key)

        return False, pos

    def print_menu(self, screen, pos, items):
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        h = curses.color_pair(1)
        n = curses.A_NORMAL
        x = 5  # Start printing from y coordinate 5
        i = 0  # Start from pos == 1
        for idx, item in enumerate(items):
            title = item[0]
            line = "{} - {}".format(idx+1, title)

            screen.addstr(x, 4, line, h if pos == i else n)
            i += 1
            x += 1  # Print next title one down

    def menu(self, items, view_title):
        items.append(("Exit", "Exit"))
        pos = 0
        x = None

        while True:
            self.screen.clear()
            self.screen.border(0)

            self.screen.addstr(2, 2, view_title, curses.A_STANDOUT)
            self.screen.addstr(4, 2, "Please select an action", curses.A_BOLD)

            self.print_menu(self.screen, pos, items)

            self.screen.refresh()
            x = self.screen.getch()
            ret, pos = self.input_handler(x, pos, items)
            if ret:
                break

    def visit(self):
        def get_visits():
            import requests
            url = "http://127.0.0.1:5000/api"
            resp = requests.get(url + "/visits/")
            try:
                body = resp.json()
            except ValueError:
                self.screen.clear()
                self.screen.border(0)
                self.screen.addstr(2, 2, "No visits found!", curses.A_BOLD)
                return
            i = 2
            win = curses.newwin(25, 25, 6, 6)
            win.border()
            win.clear()
            win.refresh()
            win.addstr(2, 2, "Result of the get /visits/", curses.A_BOLD)
            for item in body["items"]:
                win.addstr(i, 2, str(item["visit_name"]), curses.A_BOLD)
                i += 1
            win.refresh()
            return

        items = [
                ("Get all visits", get_visits),
                ("Get a visit", _pass),
                ("Post a visit", _pass),
                ("Edit a visit", _pass),
                ("Delete a visit", _pass),
        ]
        while self.menu(items, "Visit Menu"):
            pass

    def main(self):
        items = [
                ("Visit", self.visit),
                ("Mokki", _pass),
                ("Item", _pass),
                ("Participant", _pass),
        ]
        while self.menu(items, "MokkiGo Client"):
            pass

    def start(self):
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        curses.start_color()

        self.screen.keypad(1)
        self.screen.border(0)

        self.main()

        curses.endwin()


def _pass():
    """
    Placeholder function for menu tuples.
    Remove when all the functions exists
    """
    pass


if __name__ == "__main__":
    try:
        curses.wrapper(MokkiClient)
    except KeyboardInterrupt:
        print("Byebye")
