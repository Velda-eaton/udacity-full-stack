# Backend - Full Stack Trivia API 

### Installing Dependencies for the Backend

1. **Python 3.7** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)


2. **Virtual Enviornment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)


3. **PIP Dependencies** - Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:
```bash
pip install -r requirements.txt
```
This will install all of the required packages we selected within the `requirements.txt` file.


4. **Key Dependencies**
 - [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

 - [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

 - [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

### Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

### Running the server

From within the `./src` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

## API Reference
Errors are returned in a json format.  They are in this format:
```
    {
        "success": False,
        "error": 404,
        "message": "resource not Found"
    }
```
The API has the following error codes:
- 400: bad request
- 404: resource not found
- 405: method not allowed
- 422: unprocessable

## Endpoint Library
### GET /categories
- General: 
    - Fetches a dictionary of categories. The keys are the ids and the vaue is the string category name.
    - Request Arguments: none
    - Returns: Returns a dictionary of categories and the success value
    - Sample: `curl http://127.0.0.1:5000/categories`
```
{
    success: true,
    categories: {
        '1' : "Science",
        '2' : "Art",
        '3' : "Geography",
        '4' : "History",
        '5' : "Entertainment",
        '6' : "Sports"
    }
}
```

### GET /questions
- General: 
    - Request Arguments: page (optional- integer)
    - Returns a list of the questions, success value, a list of categories and the current category chosen, as well as the total number of question available.
    - Results are paginated in groups of 10. Include a request argument to choose page number, starting from 1.
    - current_category will always return blank for this request. 
    - Sample: `curl http://127.0.0.1:5000/questions`
```
{
  "categories": {
    "1": "Science", 
    "2": "Art", 
    "3": "Geography", 
    "4": "History", 
    "5": "Entertainment", 
    "6": "Sports"
  }, 
  "current_category": "", 
  "questions": [
    {
      "answer": "Apollo 13", 
      "category": 5, 
      "difficulty": 4, 
      "id": 2, 
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    }, 
    {
      "answer": "Tom Cruise", 
      "category": 5, 
      "difficulty": 4, 
      "id": 4, 
      "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
    }, 
    {
      "answer": "Maya Angelou", 
      "category": 4, 
      "difficulty": 2, 
      "id": 5, 
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
    }, 
    {
      "answer": "Edward Scissorhands", 
      "category": 5, 
      "difficulty": 3, 
      "id": 6, 
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    }, 
    {
      "answer": "Muhammad Ali", 
      "category": 4, 
      "difficulty": 1, 
      "id": 9, 
      "question": "What boxer's original name is Cassius Clay?"
    }, 
    {
      "answer": "Brazil", 
      "category": 6, 
      "difficulty": 3, 
      "id": 10, 
      "question": "Which is the only team to play in every soccer World Cup tournament?"
    }, 
    {
      "answer": "Uruguay", 
      "category": 6, 
      "difficulty": 4, 
      "id": 11, 
      "question": "Which country won the first ever soccer World Cup in 1930?"
    }, 
    {
      "answer": "George Washington Carver", 
      "category": 4, 
      "difficulty": 2, 
      "id": 12, 
      "question": "Who invented Peanut Butter?"
    }, 
    {
      "answer": "Lake Victoria", 
      "category": 3, 
      "difficulty": 2, 
      "id": 13, 
      "question": "What is the largest lake in Africa?"
    }, 
    {
      "answer": "The Palace of Versailles", 
      "category": 3, 
      "difficulty": 3, 
      "id": 14, 
      "question": "In which royal palace would you find the Hall of Mirrors?"
    }
  ], 
  "success": true, 
  "total_questions": 19
}
```

### DELETE /questions/<int:question_id>
- General: 
    - Request Arguments: question_id (int)
    - Deletes the question of the given ID if it exists. Returns the id of the deleted question, success value.
    - If no question is deleted a 404 error is returned
    - Sample: `curl -X DELETE http://127.0.0.1:5000/questions/6?page=2`
```
{
  "deleted": 15, 
  "success": true, 
}
```

### POST /questions
- General: 
    - Body Arguments: question (string), answer (string), difficulty (int), category (int), searchTerm
    - The API has two functions:
        - Enter a new question by giving the question, answer, difficulty and category in the body. 
            - The question and answer are required fields
            - Returns a the id of the created question, success value.
        - Search for a question by providing searchTerm. 
            - Returns a list of the questions, success value and the total number of question available for the search term.
    - Sample: `curl http://127.0.0.1:5000/questions -X POST -H "Content-Type: application/json" -d '{"question":'In what movie does the line, “My name is Inigo Montoya. You killed my father. Prepare to die.”, come from?', "answer":"The Princess Bride", "difficulty":"3", "category":"5"}'`
    - Sample: `curl http://127.0.0.1:5000/questions -X POST -H "Content-Type: application/json" -d '{"searchTerm": "title"}'`
```
{
  "created": 25, 
  "success": true
}
```
```
{
  "questions": [
    {
      "answer": "Escher", 
      "category": 2, 
      "difficulty": 1, 
      "id": 16, 
      "question": "Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"
    }, 
    {
      "answer": "Jackson Pollock", 
      "category": 2, 
      "difficulty": 2, 
      "id": 19, 
      "question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
    }
  ], 
  "success": true, 
  "total_questions": 2
}
```

### GET /categories/<int:category_id>/questions
- General: 
    - Request Arguments: category_id (int)
    - Returns a list of the questions for the category, success value, a list of categories and the current category chosen, as well as the total number of question available.
    - Results are paginated in groups of 10. Include a request argument to choose page number, starting from 1.
    - If no questions are found the questions variable will be an empty array.
    - Sample: `curl http://127.0.0.1:5000/categories/6/questions`
```
{
  "categories": {
    "1": "Science", 
    "2": "Art", 
    "3": "Geography", 
    "4": "History", 
    "5": "Entertainment", 
    "6": "Sports"
  }, 
  "current_category": 6, 
  "questions": [
    {
      "answer": "Brazil", 
      "category": 6, 
      "difficulty": 3, 
      "id": 10, 
      "question": "Which is the only team to play in every soccer World Cup tournament?"
    }, 
    {
      "answer": "Uruguay", 
      "category": 6, 
      "difficulty": 4, 
      "id": 11, 
      "question": "Which country won the first ever soccer World Cup in 1930?"
    }
  ], 
  "success": true, 
  "total_questions": 2
}
```

### POST /quizzes
- General: 
    - Body Arguments: previous_questions ([string]) , quiz_category (string)
    - Get question to play the quiz, given the category and previous questions in the body of the request. A random question, which has not one of the previous questions, is selected from the given category. If no category provided the whole question catelogue is used
    - Returns a question and success value, if no question found the question parameter will be empty 
    - Sample: `curl http://127.0.0.1:5000/quizzes -X POST -H "content-Type: application/json" -d '{"previous_questions": [20], "quiz_category": {"type": "Science", "id": "1"}}'`

```
{
  "question": {
    "answer": "Blood", 
    "category": 1, 
    "difficulty": 4, 
    "id": 22, 
    "question": "Hematology is a branch of medicine involving the study of what?"
  }, 
  "success": true
}
```

## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```

## Deployment N/A

## Authors
Velda Conaty and Coach Caryn 

## Acknowledgements 
The awesome team at Udacity and Coach Caryn for designing the assignement. 
