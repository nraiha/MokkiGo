import requests
import os
import json

from Menu import Menu


class Item(Menu):
    def __init__(self, screen, ih, url):
        self._items = [
                ("Get all items from mokki", self.get_all_items),
                ("Get an item from mokki", self.get_item),
                ("Post a item from mokki", self.post_item),
                ("Edit a item from mokki", self.edit_item),
                ("Delete a item from mokki", self.delete_item)
        ]
        self._screen = screen
        self._ih = ih
        self._url = url
        Menu.__init__(self)

    @staticmethod
    def parse_item(data):
        msg = ''
        msg += "Name of the item: " + data['name'] + os.linesep
        msg += "Item amount: " + data['amount'] + os.linesep
        msg += os.linesep
        return msg

    #
    #
    # REST FUNCTIONS
    #
    #
    def get_all_items(self):
        self.show_res_win("Get items")
        mokki = self.get_input(7, 4, "Give the name of the mokki")
        resp = requests.get(self._url + 'mokkis/' + mokki + "/items/")
        try:
            body = resp.json()
        except ValueError:
            self.show_res("No items found!", 1, "Oh noes")
            return

        data = body['items']
        string = ''
        for item in data:
            string += self.parse_item(item)
        lc = string.count('\n')
        msg = 'Result of the get /items/'
        self.show_res(string, lc, msg)

    def get_item(self):
        self.show_res_win("Get an item")
        mokki = self.get_input(7, 4, "Give the name of the mokki")
        item = self.get_input(10, 4, "Give item name")

        url = self._url + 'mokkis/' + mokki + '/items/' + item + '/'
        resp = requests.get(url)

        try:
            body = resp.json()
        except ValueError:
            self.show_res("No item found!", 1, "Oh noes")
            return

        string = self.parse_item(body)
        lc = string.count('\n')

        msg = "Item: "
        self.show_res(string, lc, msg)

    def post_item(self):
        self.show_res_win("Post an item")
        mokki = self.get_input(7, 4, "Give name of the mokki")
        item = self.get_input(10, 4, "Give item name")
        amount = self.get_input(13, 4, "Give amount")
        if mokki == '' or item == '' or amount == '':
            return

        data = {
                "name": item,
                "amount": amount
        }

        try:
            r = requests.post(self._url + 'mokkis/' + mokki + "/items/",
                              data=json.dumps(data),
                              headers={"Content-type": "application/json"})

            if r.status_code != 201:
                msg = str(r.json()['@error']['@message'])
                err_code = str(r.status_code)
                lc = msg.count('\n')

                self.show_res(msg, lc, err_code)
        except Exception as e:
            e = str(e)
            lc = e.count("\n")
            self.show_res(e, lc, "Something went wrong :O")
            return

    def edit_item(self):
        self.show_res_win("Edit item")
        mokki = self.get_input(7, 4, "Enter the name of the mokki")
        item = self.get_input(10, 4, "Enter the item to modify")
        new_item = self.get_input(13, 4, "Enter new name to item")
        amount = self.get_input(16, 4, "Enter new amount to item")
        if item == '' or mokki == '' or new_item =='' or amount == '':
            return

        data = {
                "name": new_item,
                "amount": amount
        }

        try:
            url = self._url + 'mokkis/' + mokki + '/items/' + item + '/'
            r = requests.put(url,
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

    def delete_item(self):
        self.show_res_win("Delete item")
        mokki = self.get_input(7, 4, "Enter the name of the mokki")
        item = self.get_input(10, 4, "Enter an item to be deleted")
        if mokki == '':
            return
        if item == '':
            return
        try:
            url = self._url + 'mokkis/' + mokki + '/items/' + item + '/'
            r = requests.delete(url)

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
        while self.menu(self._items, "Item Menu"):
            pass
