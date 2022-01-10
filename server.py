from typing import Optional
from fastapi import FastAPI, HTTPException
from collections import Counter
from starlette.responses import JSONResponse

import requests
import concurrent.futures


app = FastAPI()


# method for raising exception based on status_codes
def raise_exception(status_code):
    errors_dict = {
        "401": "Unauthorized- make sure to provide valid token.",
        "500": "Internal Server Error - check remaining api limits.",
    }
    if status_code in errors_dict:
        raise HTTPException(status_code=status_code, detail=errors_dict[status_code])
    raise HTTPException(status_code=status_code)


# creates headers for future requests with token
def create_headers(token):
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


# gets basic information about user
def user_repos_count(username, headers):
    url = f"https://api.github.com/users/{username}"
    res = requests.get(url=url, headers=headers)
    if res.status_code != 200:
        raise_exception(res.status_code)
    repos_count = res.json()["public_repos"]
    return repos_count


# method that make request for one page of repositories
def request_single_page(args_tuple):
    username, headers, repositories_per_page, page_num = args_tuple
    res = requests.get(
        url=f"https://api.github.com/users/{username}/repos?page={page_num}&per_page={repositories_per_page}",
        headers=headers,
    )
    if res.status_code != 200:
        raise_exception()
    return res


# formats the aggregate results from base_method()
def format_result(username, result, func_name):
    content = {"username": username}
    if func_name == "all_repos":
        user_repositories = []
        for page in result:
            for repo in page["repos_pages"]:
                repository_name, stargazers_count = repo
                user_repositories.append(
                    {
                        "repository_name": repository_name,
                        "stargazers_count": stargazers_count,
                    }
                )
        content["user_repositories"] = user_repositories

    if func_name == "all_langs":
        languages_dict = {}
        for langs_dict in result[0]["languages"]:
            for key, value in langs_dict["repo_langs"].items():
                if key in languages_dict:
                    languages_dict[key] = languages_dict[key] + value
                else:
                    languages_dict[key] = value
        languages_used = []
        for number, (lang, size) in enumerate(Counter(languages_dict).most_common()):
            languages_used.append(
                {"number": number + 1, "language": lang, "size_in_bytes": size}
            )
        content["languages_used"] = languages_used

    if func_name == "all_stars":
        repositories_all_stars = 0
        for stars in result:
            repositories_all_stars = repositories_all_stars + stars["all_stars"]
        content["repositories_all_stars"] = repositories_all_stars

    return content


# method for requesting languages from specific repository
def langs_from_single_repo(args_tuple):
    username, headers, repo_name = args_tuple
    repo_langs = requests.get(
        url=f"https://api.github.com/repos/{username}/{repo_name}/languages",
        headers=headers,
    )
    if repo_langs.status_code != 200:
        raise_exception(repo_langs.status_code)
    return {"repo_langs": repo_langs.json()}


# listing all repositories from github's API one page request
def all_repos_method(args_tuple):
    repos_pages = []

    response_single_page = request_single_page(args_tuple)
    res_json = response_single_page.json()

    for repo in res_json:
        repo_data = [repo["name"], repo["stargazers_count"]]
        repos_pages.append(repo_data)
    return {
        "page_num": len(repos_pages),
        "repos_pages": repos_pages,
    }


# returning languages used with their size in bytes within one page of repositories
def all_langs_method(args_tuple):
    username, headers, *rest = args_tuple
    response_single_page = request_single_page(args_tuple)
    res_json = response_single_page.json()

    languages = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        res = executor.map(
            # calling "langs_from_single_repo()" method for an iterable
            langs_from_single_repo,
            # creating iterable with additional arguments for a method "langs_from_single_repo"
            [(username, headers, repo["name"]) for repo in res_json],
        )
        languages = list(res)
    return {"languages": languages}


# counting stars from one page of user's repositories
def all_stars_method(args_tuple):
    response_single_page = request_single_page(args_tuple)
    res_json = response_single_page.json()

    all_stars = 0
    for repo in res_json:
        all_stars = all_stars + repo["stargazers_count"]
    return {
        "all_stars": all_stars,
    }


# getting pages of user's repositories that are API's functionality core
def base_method(username, token, func_name):
    headers = create_headers(token)
    repos_count = user_repos_count(username, headers)

    repos_per_page = 16
    pages = (repos_count - 1) // repos_per_page + 1
    listofpages = [i + 1 for i in range(pages)]

    functions = {
        "all_repos": all_repos_method,
        "all_langs": all_langs_method,
        "all_stars": all_stars_method,
    }
    result = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        res = executor.map(
            functions[func_name],
            [(username, headers, repos_per_page, page_num) for page_num in listofpages],
        )
        result = list(res)

    content = format_result(username, result, func_name)
    return JSONResponse(status_code=200, content=content)
    # return JSONResponse(status_code=200, content=content)


# returns ABOUT API text
@app.get("/")
async def about_api():
    return {
        "API About": "github-listing-api is an API written in python using FastAPI framework. API allows (based on github user's repositories) to: list names of repositories, return languages used with their size in bytes used, get all stars count and check current user's requests limits for github api. API has six endpoints receiving only GET requests."
    }


# allows to check current limits with and without personal Github's API token
@app.get("/current_limits/")
async def get_current_limits(token: Optional[str] = None):
    headers = create_headers(token)

    github_response = requests.get(
        url="https://api.github.com/rate_limit", headers=headers
    )

    status_code = github_response.status_code
    if not status_code == 200:
        raise_exception(status_code)

    return {"current_limits": github_response.json()["rate"]}


# endpoint listing all user's repositories
@app.get("/all_repositories/{username}")
async def get_all_repos(username: str, token: Optional[str] = None):
    return base_method(username, token, "all_repos")


# endpoint returning  user's languages used across repositories with their size in bytes
@app.get("/all_languages/{username}")
async def get_all_langs(username: str, token: Optional[str] = None):
    return base_method(username, token, "all_langs")


# endpoint showing the sum of all stars based on user's repositories
@app.get("/all_stars_count/{username}")
async def get_all_stars(username: str, token: Optional[str] = None):
    return base_method(username, token, "all_stars")
