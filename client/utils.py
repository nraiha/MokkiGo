DEBUG = True


def _pass():
    print("pass")


def debug_print(string):
    if DEBUG is not True:
        return
    f = open("log.txt", 'a')
    f.write(string + '\n')
    f.close()
