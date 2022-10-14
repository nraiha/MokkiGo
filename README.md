# MokkiGo

* Student 1. Laura Punkeri
* Student 2. Nuutti Räihä

# Running API

	Go to root folder /path/to/dir/MokkiGo <br>
	export FLASK_APP=mokkigo <br>
	export FLASK_ENV=development <br>
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




