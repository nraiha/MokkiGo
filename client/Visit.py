import requests
import os
import json

from Menu import Menu

from requests.exceptions import JSONDecodeError


class Visit(Menu):
    def __init__(self, screen, ih, url):
        self._items = [
                ("Get all visits", self.get_all_visits),
                ("Get a visit", self.get_visit),
                ("Post a visit", self.post_visit),
                ("Edit a visit", self.edit_visit),
                ("Delete a visit", self.delete_visit)
        ]
        self._screen = screen
        self._ih = ih
        self._url = url
        Menu.__init__(self)

    @staticmethod
    def parse_visit(data):
        p = data['participants']
        msg = ''
        msg += "Name of the visit: " + data['visit_name'] + os.linesep
        msg += "Name of the mokki: " + data['mokki_name'] + os.linesep
        msg += "Start date: " + data['time_start'].split('T')[0] + os.linesep
        msg += "End date: " + data['time_end'].split('T')[0] + os.linesep
        msg += "Participants: " + " ; ".join(p) + os.linesep
        msg += os.linesep
        return msg

    #
    #
    # REST FUNCTIONS
    #
    #
    def get_all_visits(self):
        resp = requests.get(self._url + "visits/")
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

    def get_visit(self):
        self.show_res_win("Get a visit")
        visit = self.get_input(7, 4, "Give visit name")

        resp = requests.get(self._url + "visits/" + visit + '/')

        try:
            body = resp.json()
        except ValueError:
            self.show_res("No visit found!", 1, "Oh noes")
            return

        string = self.parse_visit(body)
        lc = string.count('\n')

        msg = "Visit: "
        self.show_res(string, lc, msg)

    def post_visit(self):
        self.show_res_win("Post a visit")
        visit = self.get_input(7, 4, "Give visit name")
        mokki = self.get_input(10, 4, "Give mokki name")
        start = self.get_input(13, 4,
                               "Give the starting time of visit " +
                               "(YYYY-MM-DDThh:mm:ss+00:00)")
        end = self.get_input(16, 4,
                             "Give the ending time of visit " +
                             "(YYYY-MM-DDThh:mm:ss+00:00)")
        part_str = self.get_input(19, 4,
                                  "Give participants, separated by ;")
        ps = part_str.split(';')
        

        # The date is PITA to insert manually so,
        # append the hour value if only date is inserted :)
        try:
            left, right = start.split('T')
        except ValueError:
            start += "T12:00:00+00:00"

        try:
            left, right = end.split('T')
        except ValueError:
            end += "T13:00:00+00:00"

        data = {
                "visit_name": visit,
                "mokki_name": mokki,
                "time_start": start,
                "time_end": end,
                "participants": ps
        }

        try:
            r = requests.post(self._url + "visits/",
                              data=json.dumps(data),
                              headers={"Content-type": "application/json"})

        except Exception as e:
            e = str(e)
            lc = e.count("\n")
            self.show_res(e, lc, "Something went wrong :O")
            return

        if r.status_code != 201:
            print(r)
            #msg = str(r.json()['@error']['@message'])
            #err_code = str(r.status_code)
            #lc = msg.count('\n')
            #self.show_res(msg, lc, err_code)


    def edit_visit(self):
        self.show_res_win("Edit a visit")
        visit = self.get_input(7, 4, "Enter the visit to modify")
        visit_new = self.get_input(10, 4, "Enter new name to visit")
        mokki = self.get_input(13, 4, "Enter new name to mokki")
        start = self.get_input(16, 4, "New start time " +
                               "(YYYY-MM-DDThh:mm:ss+00:00")
        end = self.get_input(19, 4, "New end time " +
                             "(YYYY-MM-DDThh:mm:ss+00:00")

        # Append the hour value if only date is inserted :)
        try:
            left, right = start.split('T')
        except ValueError:
            start += "T12:00:00+00:00"

        try:
            left, right = end.split('T')
        except ValueError:
            end += "T13:00:00+00:00"

        data = {
                "visit_name": visit_new,
                "mokki_name": mokki,
                "time_start": start,
                "time_end": end
        }

        try:
            r = requests.put(self._url + "visits/{}/".format(visit),
                             data=json.dumps(data),
                             headers={"Content-type": "application/json"})

        except Exception as e:
            e = str(e)
            lc = e.count("\n")
            self.show_res(e, lc, "Something went wrong :O")
            return

        if r.status_code == 404:
            self.show_res("Visit not found", 1, str(r.status_code))

        elif r.status_code != 204:
            try:
                msg = str(r.json()['@error']['@message'])
            except JSONDecodeError:
                msg = str(r.text)
            err_code = str(r.status_code)
            lc = msg.count('\n')

            self.show_res(msg, lc, err_code)

    def delete_visit(self):
        self.show_res_win("Delete a visit")
        visit = self.get_input(7, 4, "Enter a visit to be deleted")
        try:
            r = requests.delete(self._url + "visits/{}/".format(visit))
        except Exception as e:
            e = str(e)
            lc = e.count("\n")
            self.show_res(e, lc, "Something went wrong :O")
            return

        if r.status_code != 204:
            msg = str(r.json()['@error']['@message'])
            err_code = str(r.status_code)
            lc = msg.count('\n')
            self.show_res(msg, lc, err_code)

    def main(self):
        while self.menu(self._items, "Visit Menu"):
            pass
