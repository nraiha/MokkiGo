import curses
import os

from Client import Client


if __name__ == "__main__":
    try:
        url = "http://127.0.0.1:5000/"
        if os.path.exists("log.txt"):
            os.remove("log.txt")
        curses.wrapper(Client, url)
    except KeyboardInterrupt:
        print("Byebye")
