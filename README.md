[![Build Status](https://travis-ci.com/shagabutdinov/coinsph-task.svg?branch=master)](https://travis-ci.com/shagabutdinov/coinsph-task)

Coinsph Test Task
=================

* [Task description](task.md)


Comments
--------

I don't have a django production experience so this task should be counted as
validation of my "working with unknown stack" skill.


Installation
------------

```
$ git clone git@github.com:shagabutdinov/coinsph-task.git
$ cd coinsph-task
$ pip install -r requirements.txt
$ python manage.py migrate # database migrations contain initial data
```


Usage
-----

```
# start application
$ python manage.py runserver

# get accounts list
$ curl http://127.0.0.1:8000/v1/accounts
[
  {
    "balance": "75.00",
    "currency": "PHP",
    "id": "alice_account",
    "owner": "alice"
  },
  {
    "balance": "125.00",
    "currency": "PHP",
    "id": "bob_account",
    "owner": "bob"
  }
]

# get payments list
$ curl http://127.0.0.1:8000/v1/payments
[
  {
    "account_id": "alice_account",
    "amount": "25.00",
    "direction": "OUTGOING",
    "from_account_id": null,
    "id": 1,
    "to_account_id": "bob_account"
  },
  {
    "account_id": "bob_account",
    "amount": "25.00",
    "direction": "INCOMING",
    "from_account_id": "alice_account",
    "id": 2,
    "to_account_id": null
  }
]

# make payment
$ curl -X POST http://127.0.0.1:8000/v1/payments -d '{
  "amount": 25.0,
  "from_account": "alice_account",
  "to_account": "bob_account"
}'
{"ok": true}

# run tests
$ python manage.py test
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
..................
----------------------------------------------------------------------
Ran 18 tests in 0.060s

OK
Destroying test database for alias 'default'...
```

Application design
------------------

Current database design:

```
Account:

* id: string
* owner: string
* balance: decimal
* currency: enum(USD, PHP, RUB)

Payment

* id: int
* account: reference
* from_account: reference, nullable
* to_account: reference, nullable
* direction: enum(OUTGOING, INCOMING)
* amount: decimal
```

I implemented the application design according to the task but if I'd ask to design it, I'd do following:

* Use numeric incremental identifier for "Account" instead of string identifier
* Rename "Payment" to "Transaction" and use following data structure for it:
  * from_account
  * to_account
  * amount

Result design would be following:

```
Account:

* id: int
* name: string
* owner: string
* balance: decimal
* currency: enum(USD, PHP, RUB)

Payment:

* id: int
* from_account: reference, nullable
* to_account: reference, nullable
* amount: decimal
```

This would make design simplier, prevents database inconsistency, and reduce
amount of code required to validate payments.
