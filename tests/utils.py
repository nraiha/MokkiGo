def get_mokki(num=1):
    return {
        'name': "mokki-{}".format(num),
        'location': "Location-{}".format(num)
    }


def get_item(num=1):
    return {
        "name": "item{}".format(num),
        "amount": "{}".format(num)
    }


def get_participant(num=1):
    return {
            "name": "part{}".format(num),
            "allergies": "food {}".format(num)
    }


def get_visit(num=1):
    return {
            'visit_name': 'visit{}'.format(num),
            'mokki_name': 'mokki-{}'.format(num),
            'time_start': '2020-02-02T12:00:00+10:00',
            'time_end': '2020-02-02T12:00:00+10:00',
            'participants': ['part{}'.format(num),
                             'part{}'.format(num+1)]
            }
