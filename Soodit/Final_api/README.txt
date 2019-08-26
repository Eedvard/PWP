Required packages to run the api are found in the requirements.txt file.

To run the api write following commands to console:
 
Linux:
  export FLASK_APP=mealplan
  export FLASK_ENV=development
  flask init-db
  flask run
Windows:
  set FLASK_APP=mealplan
  set FLASK_ENV=development
  flask init-db
  flask run
  
To run the tests write following commands in the root Final_api folder:
  pip install -e .
Then change to tests folder and write following command to run the tests:
  pytest
