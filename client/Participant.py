import requests
import os
import json

from Menu import Menu


class Participant(Menu):
    def __init__(self, screen, ih, url):
        self._items = [
                ("Get all participants", self.get_all_participants),
                ("Get a participant", self.get_participant),
                ("Post a participant", self.post_participant),
                ("Edit a participant", self.edit_participant),
                ("Delete a participant", self.delete_participant)
        ]
        self._screen = screen
        self._ih = ih
        self._url = url
        Menu.__init__(self)

    @staticmethod
    def parse_participant(data):
        msg = ''
        msg += "Name of the participant: " + data['name'] + os.linesep
        msg += "Allergies of participant: " + data['allergies'] + os.linesep
        msg += os.linesep
        return msg

    #
    #
    # REST FUNCTIONS
    #
    #
    def get_all_participants(self):
        try:
            resp = requests.get(self._url + "participants/")
            body = resp.json()

            data = body['items']
            string = ''
            for item in data:
                string += self.parse_participant(item)
            lc = string.count('\n')
            msg = 'Result of the get /participants/'
            self.show_res(string, lc, msg)
        except KeyError:
            self.show_res("No participants found!", 1, "Oh noes")
        except ValueError:
            self.show_res("No participants found!", 1, "Oh noes")
            return

    def get_participant(self):
        self.show_res_win("Get a participant")
        part = self.get_input(7, 4, "Give participants name")

        try:
            resp = requests.get(self._url + "participants/" + part + '/')

            body = resp.json()
            string = self.parse_participant(body)
            lc = string.count('\n')
            msg = "Participant: "
            self.show_res(string, lc, msg)

        except ValueError:
            self.show_res("No participant found!", 1, "Oh noes")
            return
        except KeyError:
            return

    def post_participant(self):
        self.show_res_win("Post a participant")
        part = self.get_input(7, 4, "Give participant's name")
        allergies = self.get_input(10, 4, "Give allergies")
        if part == '' or allergies == '':
            return

        data = {
                "name": part,
                "allergies": allergies
        }

        try:
            r = requests.post(self._url + "participants/",
                              data=json.dumps(data),
                              headers={"Content-type": "application/json"})
            if r.status_code != 201:
                msg = str(r.text)
                err_code = str(r.status_code)
                lc = msg.count('\n')

                self.show_res(msg, lc, err_code)

        except Exception as e:
            e = str(e)
            lc = e.count("\n")
            self.show_res(e, lc, "Something went wrong :O")
            return

    def edit_participant(self):
        self.show_res_win("Edit a participant")
        part = self.get_input(7, 4, "Enter the participant to modify")
        new_part = self.get_input(10, 4, "Enter new name to participiant")
        allergies = self.get_input(13, 4, "Enter new allergies to participant")
        if part == '' or new_part == '' or allergies == '':
            return

        data = {
                "name": new_part,
                "allergies": allergies
        }

        try:
            r = requests.put(self._url + "participants/{}/".format(part),
                             data=json.dumps(data),
                             headers={"Content-type": "application/json"})

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

    def delete_participant(self):
        self.show_res_win("Delete a participant")
        part = self.get_input(7, 4, "Enter a participant to be deleted")
        try:
            r = requests.delete(self._url + "participants/{}/".format(part))

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
        while self.menu(self._items, "Participant Menu"):
            pass
