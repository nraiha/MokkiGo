# MokkiGo

* Student 1. Laura Punkeri
* Student 2. Nuutti Räihä

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__

# Structure

├── README.md <br>
├── mokkigo <br>
│   ├── __init__.py <br>
│   ├── api.py <br>
│   ├── models.py <br>
│   ├── utils.py <br>
│   ├── resources/ <br>
│   └── static/ <br>
│        └── schema/ <br>
└── tests
*TBD*


# Running API
<p>
Go to root folder /path/to/dir/MokkiGo <br>
export FLASK_APP=mokkigo <br>
export FLASK_ENV=development <br>
flask run
</p>

# Running tests:
pytest --cov-report term-missing --cov=mokkigo




