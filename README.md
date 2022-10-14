# MokkiGo

* Student 1. Laura Punkeri
* Student 2. Nuutti Räihä


# Running API

To install the dependencies:

	python3 -m pip install -r requirements.txt
	
OR to setup

	python3 -m pip install .

Note: if using older versions of flask, replace FLASK_DEBUG=1 with FLASK_ENV=development

	Go to root directory /path/to/dir/MokkiGo <br>
	export FLASK_APP=mokkigo <br>
	export FLASK_DEBUG=1 <br>
	flask init-db
	flask run

Alternatively:

	Go to root folder /path/to/dir/MokkiGo <br>
	./mokkigo.sh init
	./mokkigo.sh run

OR

	./mokkigo.sh init run

# Running tests
pytest --cov-report term-missing --cov=mokkigo

# Running client

	Go to the client directory in MokkiGo
	python3 Client.py
