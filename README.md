# MokkiGo

* Student 1. Laura Punkeri
* Student 2. Nuutti Räihä

Note: if using older versions of flask, replace FLASK_DEBUG=1 with FLASK_ENV=development

# Running API

	Go to root folder /path/to/dir/MokkiGo <br>
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

# Running tests:
pytest --cov-report term-missing --cov=mokkigo




