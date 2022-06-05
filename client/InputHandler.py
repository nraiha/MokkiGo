import curses


class InputHandler:
    @staticmethod
    def navigate(pos, n, item_len, x=None):
        """
        Increments the position and wraps it around if needed.
        In case the key pressed was an integer (1-9), sets the position to it.
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
        Q to quit
        Calculates the next position when j/k, up/down, 1-9 is pressed
        """
        if key == ord('q'):
            return True, pos

        # Enter -> activate menu
        elif key == ord('\n'):
            # Last position -> exit menu
            if pos == len(items) - 1:
                return True, pos
            else:
                # Function callback
                items[pos][1]()

        elif key == curses.KEY_DOWN or key == ord('j'):
            pos = self.navigate(pos, 1, len(items))

        elif key == curses.KEY_UP or key == ord('k'):
            pos = self.navigate(pos, -1, len(items))

        # Calculate the maximum number allowed
        elif ord('0') < key < ord(str(len(items)+1)):
            pos = self.navigate(pos, 0, len(items), x=key)

        return False, pos

    @staticmethod
    def move_in_pad(win, pad, lc, maxx, posy, posx, pady, padx):
        while True:
            key = win.getch()
            if key == ord('q'):
                break

            elif key == ord('h') or key == curses.KEY_LEFT:
                if posx != 0:
                    posx += -1
                pad.refresh(posy, posx, 7, 4, pady, padx)

            elif key == ord('j') or key == curses.KEY_DOWN:
                if posy != lc:
                    posy += 1
                pad.refresh(posy, posx, 7, 4, pady, padx)

            elif key == ord('k') or key == curses.KEY_UP:
                if posy != 0:
                    posy += -1
                pad.refresh(posy, posx, 7, 4, pady, padx)

            elif key == ord('l') or key == curses.KEY_RIGHT:
                if posx != maxx:
                    posx += 1
                pad.refresh(posy, posx, 7, 4, pady, padx)
        curses.doupdate()
