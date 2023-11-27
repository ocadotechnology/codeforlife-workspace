# Frontend

## Overview

This `game_frontend` contains the frontend for the Kurono game. It is a single page application using [React](https://reactjs.org/). We use [Redux](https://redux.js.org/) for state management and [redux-observable](https://redux-observable.js.org/) for handling our side effects (e.g. asynchronous calls).&#x20;

## Requirements

* [Node](https://nodejs.org/en/download/)
* [Parcel](https://parceljs.org/)
* [yarn](https://classic.yarnpkg.com/en/)

## Build dependencies

Once you have cloned `aimmo` repository, run the command below in the `game_frontend` folder:

```
yarn
```

## Testing

For frontend tests, please refer to running Cypress and Jest tests on the [Testing](../../testing.md) section.

### Further reading

If you are new to React and Redux we recommend reading these resources:

* [React tutorial](https://reactjs.org/tutorial/tutorial.html)
* [Thinking in React](https://reactjs.org/docs/thinking-in-react.html)
* [Redux and React tutorial](https://www.valentinog.com/blog/react-redux-tutorial-beginners/)

In order to make sure our project structure is scalable we use [re-ducks](https://medium.freecodecamp.org/scaling-your-redux-app-with-ducks-6115955638be).

The links here aren't necessary for helping you contribute straight away but they will help you out as you get more comfortable with our project:

* [Jest testing cheatsheet](https://devhints.io/jest)
* [Redux Observables](https://redux-observable.js.org/)
