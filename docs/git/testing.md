---
description: How to run tests locally.
---

# Testing

When a PR is submitted, a series of tests will be run with Github actions. Our tests can be categorised into two:

* Backend / Python tests
* Frontend tests with Cypress, Selenium and Jest

It is fine to just submit your PR and let the tests run on Github. However, if the tests fail, you may need to run the tests locally to investigate what's going on, then either fix the tests, or fix your code.

## Running Python Tests Locally

To run Python tests, simply run at the top folder of the repository:

```
pytest
```

The `pytest` command will run both the tests written with [pytest](https://docs.pytest.org/) and those with the built-in python [unittest](https://docs.python.org/3/library/unittest.html).

{% hint style="info" %}
We are aiming to migrate all **unittest** to **pytest.** Meanwhile you will see a combination of these. If you write new tests, please use **pytest**.
{% endhint %}

For Rapid Router and Portal, `pytest` also runs [Selenium tests](testing.md#running-selenium-tests-locally). Check the section below for what you need to install to run it.

The Python tests in Portal also include some snapshot tests.\
Running `pytest` will also automatically run the snapshot tests. When needed, the snapshot tests can be updated by running `pytest --snapshot-update`.

## Running Cypress tests locally

[Cypress](https://www.cypress.io/) is a frontend test framework that is used on Kurono (aimmo) and part of Portal.

To run Cypress tests locally, you need two shell windows.

**Shell #1**

The following will run the portal/game on local server.

In aimmo:

```bash
./run.py
```

In Portal:

```
./run
```

**Shell #2**&#x20;

This will run the Cypress tests in the terminal.

In aimmo:

```
cd game_frontend
yarn run cypress run
```

In Portal:

```
yarn run cypress run
```

If you want to view the tests as they run using Cypress' test runner window, you can run:

```
yarn run cypress open
```

## Running Selenium tests locally

Selenium is a frontend test framework that is **used in Rapid Router and in Portal**. We aim to gradually migrate Selenium tests to Cypress.

**To run Selenium tests you need to install chromedriver**. Please check here on [how to install](https://chromedriver.chromium.org/getting-started) for your OS.

Similar with Cypress, it will launch a browser windows and you should be able to see a series of frontend actions.

## Running Jest tests locally

Aimmo also includes some JavaScript frontend tests written in the [Jest](https://jestjs.io/) framework.

These can be run locally with the following:

```
cd game_frontend
yarn test
```

If needed, the snapshot tests can be updated with the following:

```
yarn test -u
```
