import requests
import os
import json

from Menu import Menu


class Mokki(Menu):
    def __init__(self, screen, ih, url):
        self._items = [
                ("Get all mokkis", self.get_all_mokkis),
                ("Get a mokki", self.get_mokki),
                ("Post a mokkis", self.post_mokki),
                ("Edit a mokkis", self.edit_mokki),
                ("Delete a mokki", self.delete_mokki)
        ]
        self._screen = screen
        self._ih = ih
        self._url = url
        Menu.__init__(self)

    @staticmethod
    def parse_mokki(data):
        msg = ''
        msg += "Name of the mokki: " + data['name'] + os.linesep
        msg += "Location of the mokki: " + data['location'] + os.linesep
        msg += os.linesep
        return msg

    #
    #
    # REST FUNCTIONS
    #
    #
    def get_all_mokkis(self):
        resp = requests.get(self._url + "mokkis/")
        try:
            body = resp.json()

            data = body['items']
            string = ''
            for item in data:
                string += self.parse_mokki(item)
            lc = string.count('\n')
            msg = 'Result of the get /mokkis/'
            self.show_res(string, lc, msg)
        except ValueError:
            self.show_res("No mokkis found!", 1, "Oh noes")
            return
        except KeyError:
            self.show_res("No mokkis found!", 1, "Oh noes")
            return

    def get_mokki(self):
        self.show_res_win("Get a mokki")
        mokki = self.get_input(7, 4, "Give mokki name")

        try:
            resp = requests.get(self._url + "mokkis/" + mokki + '/')
            body = resp.json()
            string = self.parse_mokki(body)
            lc = string.count('\n')
            msg = "Mokki: "
            self.show_res(string, lc, msg)
        except ValueError:
            self.show_res("No mokki found!", 1, "Oh noes")
            return
        except KeyError:
            return

    def post_mokki(self):
        self.show_res_win("Post a mokki")
        mokki = self.get_input(7, 4, "Give mokki name")
        location = self.get_input(10, 4, "Give location")
        if mokki == '' or location == '':
            return

        data = {
                "name": mokki,
                "location": location
        }

        try:
            r = requests.post(self._url + "mokkis/",
                              data=json.dumps(data),
                              headers={"Content-type": "application/json"})

        except Exception as e:
            e = str(e)
            lc = e.count("\n")
            self.show_res(e, lc, "Something went wrong :O")
            return

        if r.status_code != 201:
            msg = str(r.json()['@error']['@message'])
            err_code = str(r.status_code)
            lc = msg.count('\n')

            self.show_res(msg, lc, err_code)

    def edit_mokki(self):
        self.show_res_win("Edit a mokki")
        mokki = self.get_input(7, 4, "Enter the mokki to modify")
        mokki_new = self.get_input(10, 4, "Enter new name to mokki")
        location = self.get_input(13, 4, "Enter new location to mokki")

        if mokki == '' or mokki_new == '' or location == '':
            return

        data = {
                "name": mokki_new,
                "location": location
        }

        try:
            r = requests.put(self._url + "mokkis/{}/".format(mokki),
                             data=json.dumps(data),
                             headers={"Content-type": "application/json"})

            if r.status_code != 204:
                try:
                    msg = str(r.json()['@error']['@message'])
                except Exception:
                    msg = str(r.text)
                err_code = str(r.status_code)
                lc = msg.count('\n')

            self.show_res(msg, lc, err_code)
        except Exception as e:
            e = str(e)
            lc = e.count("\n")
            self.show_res(e, lc, "Something went wrong :O")

    def delete_mokki(self):
        self.show_res_win("Delete a mokki")
        mokki = self.get_input(7, 4, "Enter a mokki to be deleted")
        if mokki == '':
            return
        try:
            r = requests.delete(self._url + "mokkis/{}/".format(mokki))
            if r.status_code != 204:
                msg = str(r.json()['@error']['@message'])
                err_code = str(r.status_code)
                lc = msg.count('\n')
                self.show_res(msg, lc, err_code)
        except Exception as e:
            e = str(e)
            lc = e.count("\n")
            self.show_res(e, lc, "Something went wrong :O")
            return

    def main(self):
        while self.menu(self._items, "Mokki Menu"):
            pass
