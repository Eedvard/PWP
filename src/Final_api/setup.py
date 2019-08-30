# This entire file is based on the example setup.py file at the lovelace course materials

from setuptools import find_packages, setup

setup(
    name="mealplan",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "flask",
        "flask-restful",
        "flask-sqlalchemy",
        "SQLAlchemy",
    ])