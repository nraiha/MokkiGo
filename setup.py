# Borrowed from the course examples:
# https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/setup.py
from setuptools import find_packages, setup

setup(
    name='mokkigo',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'flask-restful',
        'flask-sqlalchemy',
        'SQLAlchemy'
    ]
)
