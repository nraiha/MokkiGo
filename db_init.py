from mokkigo.models import Mokki, Visit, Item, Participant
from mokkigo import create_app, db

app = create_app()
ctx = app.app_context()
ctx.push()

print(db)

for idx, letter in enumerate("ABC", start=1):
    p = []
    for j in range(1, 4):
        p.append(Participant(name="participant{}-{}".format(letter, j),
                             allergies="food{}-{}".format(letter, j)))
    m = Mokki(
            name="Mokki{}-{}".format(letter, idx),
            location="Area{}-{}".format(letter, idx)
    )
    v = Visit(
            time_start="2022-01-0{}".format(idx),
            time_end="2022-01-0{}".format(idx+5),
            visit_name="visit-{}".format(letter)
    )
    item = []
    for j in range(1, 3):
        item.append(Item(name="item-{}".format(letter),
                         amount="{}".format(idx)))

    v.mokki_name = m.name
    v.participants.append(p[0])
    v.participants.append(p[1])
    v.participants.append(p[2])

    item[0].mokki = m
    item[1].mokki = m

    db.session.add(p[0])
    db.session.add(p[1])
    db.session.add(p[2])
    # db.session.add(item[0])
    # db.session.add(item[1])
    # db.session.add(m)
    # db.session.add(v)

db.session.commit()

ctx.pop()
