import curses
import os

from Client import Client


if __name__ == "__main__":
    try:
        if os.path.exists("log.txt"):
            os.remove("log.txt")
        curses.wrapper(Client)
    except KeyboardInterrupt:
        print("Byebye")
