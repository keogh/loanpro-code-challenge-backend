# LoanPro Challenge Backend

This is a REST API in Django which provides the 
endpoints to create and manage arithmetic operations.

You need to have user credentials in order to use this API.
Also, the user needs to have enough balance since each operation
has a cost.

This API is consumed by the [LoanPro Challange Frontend](https://github.com/keogh/loanpro-code-challenge-frontend) 
project.

## Installation

The author of this project likes to work with Poetry to manage
packages and dependencies when working with python

### Python

You need python 3.11+ to run this project.

Your could use pyenv to install and manage server versions of python
https://github.com/pyenv/pyenv 

Once you have python you will need [Poetry](https://python-poetry.org/).

### Poetry is a requirement

Install Poetry

https://python-poetry.org/docs/#installation

### Activate Poetry Virtual Environment

```shell
poetry shell
```

### install dependencies

```shell
poetry install
```

### Setup ENV variables.

Copy the `.env.example` file to `.env`

```shell
cp .env.example .env
```

Set the keys with the proper values. You can get your `RANDOM_ORG_API_KEY`
by creating an account in https://www.random.org/

The default database used in development is SQLite 3, you could configure a postgresql
connection if you want to, just uncomment and set the proper values for your
database configuration, e.g. if you want to use postgres

```shell
DATABASE_URL=
DB_ENGINE=django.db.backends.postgresql
DB_NAME=loanpro
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
```

You could check how to connect to other databases in 
[Django Documentation](https://docs.djangoproject.com/en/5.0/ref/databases/).

### Django Setup

Now we need to some initial setup for django like running migrations
and creating the superuser

Run migrations. **Remember all commands are run through Poetry**.

```shell
poetry run python manage.py migrate
```

Create superuser.

```shell
python manage.py createsuperuser
```

## Usage

All endpoints, except `/api/v1/sign-in`, need a valid jwt token in the `Authorization`
header or the request will be rejected.

## Sign-in and use Token

First of all we need the token by sending the login credentials
to `/api/v1/sign-in` as a POST request

```shell
curl -k -X POST -H "Content-Type: application/json" -d '{"username": "testuser", "password": "123qweasd"}' h
ttp://127.0.0.1:8000/api/v1/sign-in
```

Now you could fetch the records

```shell
curl -X GET -H "Authorization: TOKEN" http://127.0.0.1:8000/api/v1/records?page=2&per_page=40
```

If you are here with no issues then you have the backend all setup, up and running.

That's it!

## API Documentation

You can find a public postman workspace here: 
[Postman workspace](https://www.postman.com/martian-desert-682727/workspace/loanpro-code-challenge/request/27905589-a744e7aa-2341-4a2c-83f2-ced3407293c1?tab=overview)

The public availability will be removed soon.

### Sign-in
`POST /api/v1/sign-in`

Returns the jwtoken if username and password are valid.

The sample data inserted in the migrations has two users:
- `testuser/123qweasd`, user with over 1k records
- `tesuser2/123qweasd`, user with balance equals to 1

Body:
```json
{
  "username": "testuser",
  "password": "123qweasd"
}
```

Response:
```json
{
  "token": "ey...9.ey...0.D-K...k0"
}
```

### Sign-out
`POST /api/v1/sign-out`

Set the token to a blocklist so it cannot be used.

Response:
```json
{"message": "Signed out successfully"}
```

### List Records
`GET /api/v1/records`

Returns the current user records paginated by default 
to 100 items per page, order by id in DESC direction.

Query params:
```json
{
  "page": 1,
  "per_page": 100,
  "search": "",
  "sort_by": "id",
  "direction": "desc"
}
```

Response:
```json
{
  "success": true,
  "pagination": {
    "page": "1",
    "per_page": "10",
    "total_pages": 100,
    "total_items": 1000
  },
  "records": [
    {
      "id": 1000,
      "operation_id": 5,
      "operation_type": "Square Root",
      "user_id": 1,
      "amount": 4,
      "user_balance": 2357,
      "operation_response": "5",
      "created_at": "2024-04-20 01:36:17"
    }
  ]
}
```

### New Record
`POST /api/v1/records`

Creates a new Record for an arithmetic operation.

It returns insufficient balance if balance is less than the operation cost.

Body:
```json
{
    "operation_id": 6,
    "operator1": 32,
    "operator2": 2
}
```

Response:
```json
{
    "success": true,
    "record_id": 1186,
    "user_balance": 2313
}
```

If error you el get a httpcode and an error message:
```json
{
  "error": "insufficient balance"
}
```

### Delete Record 

`DELETE /api/v1/records/:id`

Delete the record based on the ID. The record needs to belong to the user in order to be deleted.

Response:
```json
{
    "success": true,
    "message": "Record deleted successfully, user balances records updated"
}
```

### List Operations

`GET /api/v1/operations`

Returns all the available arithmetic operations and their cost.

It supports pagination and sorting just like `GET /api/v1/records` endpoint.

Query params
```json
{
  "page": 1,
  "per_page": 100,
  "sort_by": "id",
  "direction": "desc"
}
```

Response:
```json
{
    "success": true,
    "operations": [
        {
            "id": 6,
            "name": "Random String",
            "type": "random_string",
            "cost": 8
        },
        {
            "id": 5,
            "name": "Square Root",
            "type": "square_root",
            "cost": 4
        }
    ],
    "pagination": {
        "page": 1,
        "per_page": 10,
        "total_pages": 1,
        "total_items": 6
    }
}
```

