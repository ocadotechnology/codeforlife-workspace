# Frontend Coding Convention

This document details the frontend coding conventions we must follow.

## File Structure

There old-school approach to structuring React projects is to group files by type:

```txt
/styles
  component1.css
  component2.css
/components
  component1.jsx
  component2.jsx
```

However, this splits co-dependent code across our codebase. The new-school approach is "[feature folders](https://redux.js.org/faq/code-structure)", where co-dependent code is co-located for easier navigability:

```txt
/features
  /component1
    component1.css
    component1.jsx
  /component2
    component2.css
    component2.jsx
```

With this is in mind, our file structure will be:

```txt
/src
  /app
    api.ts
    hooks.ts
    router.ts
    store.ts
    theme.ts
  /components
    /c1
      c1.module.scss
      c1.tsx
    ...
  /features
    /f1
      f1.module.scss
      f1.tsx
      f1API.ts
      f1Slice.ts
    ...
  /pages
    /p1
      p1.module.scss
      p1.tsx
    ...
  index.module.scss
  index.tsx
```

### /app

`app` contains app level resources - it has an impact on every component.

- `api.ts` - base api settings.
- `hooks.ts` - custom app hooks.
- `router.ts` - React page router.
- `store.ts` - Redux store.
- `theme.ts` - Material UI theme.

### /components

`components` contains reusable components that will be used in 2 or more places within your app. This should be generic in nature. For example, a button with a callback to handle a general click event.

**NOTE:** Only components that will be reused throughout this app only should go in the folder. If it will be reused throughout multiple apps, it should go in the [components folder in CFL's JS Package](https://github.com/ocadotechnology/codeforlife-package-javascript/tree/main/src/components).

### /features

`features` contains unique, non-reusable components that will be used once throughout your app. For example, a 'UsersList' component that allows you to view + manage all the users in your organization.  

### /pages

`pages` contains the web pages that we will route to in our app. Routing rules are defined for these pages in `app/router.ts`. Pages should be a composition of features.

### index

`index` is the entry point into our React app and is where we apply app wide configurations. Notably, this is where we apply the Redux store, Material UI theme and React Router rules, among other things.  

## React

React components must be written as functional components with hooks. The hooks you will most commonly use are:

1. useState
1. useEffect
1. useAppDispatch (see [hooks.ts](../../src/app/hooks.ts))
1. useAppSelector (see [hooks.ts](../../src/app/hooks.ts))

**NOTE:** TypeScript requires us to use type-defined hooks for useDispatch and useSelector.

## Redux and Redux Toolkit (RTK)

You're required to use redux to centrally store any data that meets one of these conditions:

1. it's retrieved from the API;
1. it's used as a property in more than one component;
1. it needs to be cached for repeated, quick access;

However, there are times where components can define a local state using the useState hook as it doesn't make sense to persist this info once the component is unmounted. For example, completing a form:

```tsx
import React, { useState } from 'react';
import { TextField } from '@mui/material/';

function RegisterUserForm(): JSX.Element {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');

  function handleFirstNameChange(event: React.ChangeEvent<HTMLInputElement>): void {
    setFirstName(event.target.value);
  }

  function handleLastNameChange(event: React.ChangeEvent<HTMLInputElement>): void {
    setLastName(event.target.value);
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    console.log(`${firstName} ${lastName}`);
  }
  
  return (
    <form onSubmit={handleSubmit}>
      <TextField
        required
        id='firstname'
        label='First Name'
        value={firstName}
        onChange={handleFirstNameChange}
      />
      <TextField
        required
        id='lastname'
        label='Last Name'
        value={lastName}
        onChange={handleLastNameChange}
      />
    </form>
  );
}
```

Redux contains 3 key layers of abstraction that need to be understood:

1. states - stores the state of the app in a central location.
1. actions - describe events happening that may change the state of the app.
1. reducers - receives actions and decides whether or not to update the store.

Furthermore, we'll be following [Redux's Style Guide](https://redux.js.org/style-guide/).

### Redux Toolkit (RTK)

RTK condenses all 3 layers of abstraction into a `slice`. For each feature of the app, you must create a slice implementing how the feature's component will interact with the store.

## RTK - Making API calls

The base API settings are configured in `app/api.ts`. However, each feature will need to inject the base api with the endpoints it requires.

```ts
import api from 'app/api';
import { User } from './userSlice';

const userApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getUsers: builder.query<User, void>({
      query: () => `user/all`
    })
  })
});

export default userApi;
export const {
  useGetUsersQuery,
  useLazyGetUsersQuery
} = userApi;
```

Next, the API's response must be globally stored using the slice's "extra reducers".

```ts
import { createSlice } from '@reduxjs/toolkit';
import { type RootState } from 'app/store';
import userApi from './userAPI';

export interface User {
  id: number,
  name: string
}

export interface UserState {
  list: User[];
  status: 'idle' | 'loading' | 'failed';
}

const initialState: UserState = {
  list: [],
  status: 'idle'
};

export const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {...},
  extraReducers: (builder) => {
    builder
      .addMatcher(userApi.endpoints.getUsers.matchPending, (state) => {
        state.status = 'loading';
      })
      .addMatcher(userApi.endpoints.getUsers.matchFulfilled, (state, action) => {
        state.status = 'idle';
        state.list = action.payload;
      })
      .addMatcher(userApi.endpoints.getUsers.matchRejected, (state) => {
        state.status = 'failed';
      });
  }
});

export const { ... } = userSlice.actions;

export const selectUsers = (state: RootState): User[] => state.user.list;

export default userSlice.reducer;
```

Then, this API can be used in the feature's component.

```tsx
import { useAppSelector } from 'app/hooks';
import { selectUsers } from './userSlice';
import { useLazyGetUsersQuery } from './userAPI';

export default function UserList(): JSX.Element {
  const users = useAppSelector(selectUsers);
  const [lazyGetUsers] = useLazyGetUsersQuery();

  function handleGetUsers(): void {
    void lazyGetUsers();
  }

  return (
    <ul>
      {users.map((user) =>
        <li key={user.id}>{user.name}</li>
      )}
    </ul>
    <button onClick={handleGetUsers}>Get Users</button>
  );
```
