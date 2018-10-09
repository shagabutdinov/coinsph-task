Our goal with this test project is to see you best/most idiomatic code, specifically we're looking for:

- idiomatic Python code, proper data structures usage, best practices and official style guides (PEP-8, e.g.,https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/)

- proper usage of Django components

- project maintainability (decoupling, hiding complexity)

- readable code (descriptive names of variables, classes, functions, apps, packages)

- no "dead code" inside repo (e.g., empty modules, unused settings, etc)

- tests (unit, functional)

- doc strings which should explain "real world" problem you're solving, attributes, params documenting (like if you're writing docs for Sphinx).

- README explaining your project's purpose, how to set it up, run tests, do a
code linting

- API docs

- awareness of DB transactions, locks, race conditions

For the test, we ask that you create a simple account/transactions model with a
RESTful API. This should allow for updating the balances of accounts and
handling the following endpoint:

- API endpoint ``GET /v1/accounts`` which shows a list of accounts
- API endpoint ``GET /v1/payments`` which shows a list of payments
- API ``POST /v1/payments`` that creates a new payment with given ``from_account``, ``amount``, ``to_account``.


For example:

```
from_account: bob123
amount: 100
to_account: alice456
```


Data:

```
Account
id bob123
owner bob
balance 100
currency PHP

Account
id alice456
owner alice
balance 0.01
currency PHP
```


Payment:

```
account "bob123"
amount: 100
to_account: "alice456"
direction: "outgoing"

Payment:
account "alice456"
amount: 100
from_account: "bob123"
direction: "incoming"
```