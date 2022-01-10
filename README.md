## GITHUB-LISTING_API

### ABOUT

```
github-listing-api is an API written in python using FastAPI framework.
API allows (based on github user's repositories) to:
    - list names of repositories
    - return languages used with their size in bytes used
    - get all stars count
    - check current user's requests limits for github api.
API has five endpoints receiving only GET requests.
```

### INSTALLATION

```
First create and activate virtual enviorment
Next install dependencies using:
pip install -r requirments.txt
```

### HOW TO USE?

```
Launch server using command: uvicorn server:app
After the server is running, you can start making requests to server endpoints through:

- terminal -> run command: curl localhost:8000/allegro/?token="{PERSONAL_GITHUB_TOKEN}"
- FastAPI docs -> in browser go to page: http://localhost:8000/docs
```

### ENDPOINTS

    1. /  ->  About text for github-listing-api

>

    2. /current_limits/?token={token}-> [OPTIONAL: personal github token]

    Shows current limits of allowed requests to github api, user can pass as optional parameter personal github token which increase the limits of github api's usage by adding ?{PERSONAL_TOKEN}

>

    3. /all_repositories/{username}/?token={token} -> [REQUIRED: github username, OPTIONAL: personal github token]

    Listing all github user's repositories' names and corresponding star count - stargazer_count

>

    4. /all_languages/{username}/?token={token} -> [REQUIRED: github username, OPTIONAL: personal github token]

    Returning sum of all stars of github user's repositories

>

    5. /all_stars_count/{username}/?token={token}= - [REQUIRED: github username, OPTIONAL: personal github token]

    Listing languages and their size in bytes used across github user's repositories

### TECHNOLOGY USED

```
Language: python
API framework: FastAPI
Virtual enviornment: venv.
Testing library: pytest
```

### TESTS

```
In order to succesfully run test, user has to provide PERSONAL_API_TOKEN.
Be cautious -> tests use multiple requests which can consume all of github's api allowed requests.
Run in terminal: pytest test_server.py -v -s
```

### INSTALLATION

```
First activate virtual enviornment by running-> [LINUX] venv\Scripts\activate, [WINDOWS] venv\Scripts\activate.bat
Then using pip install all dependencies -> python -m pip install -r requirements.txt
```

### DEVELOPMENT PLANS

    1) Introducing caching and changes verification.

>

    2. Code refactoring, eg. improving readability, comments, dynamically create repositories per page requests.

>

    3. Improving exception handling and github's api limits.

>

    4. Adding response_models to endpoints.

>

    5. Further optimising multithreading / using asynchronous requests instead of used "requests" library.

>

    6. Adding listing functionality of differentiation to fork and non-fork repositories.

>

    7. Allowing for user to login to access slow fetching data functionality - user's request would finish processing after couple of hours, after that it would wait for user to get it.

>

    8. Improving security by adding logging, blocking ip addresses.

>

    9. Deploying solution to remote server, eg. Heroku, AWS.

>

    10. Extending API's functionality to organisations' repositories with relation to members.

>

    11. Extending and improving testing, adding slow testing to cope with github api's request limits.

>

    12. Idea of creating token warehouse where logged in users for functionality of slow fetching data authorize server to use some part of user's "personal api token" limits.

>

    13. Allowing user to pass several tokens to increase github's api requests limitations.

>

    14. Using Docker to ensure architecture independence.
