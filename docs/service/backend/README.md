# Backend

Each service has a backend directory that contains the backend source code of the service.

## The 3 Layers

Our backend consists of 3 layers that build on top of each other. Starting from the bottom layer, the layers are:

1. [models](./MODELS.md): Defines the data tables (a.k.a. models) and columns (a.k.a. fields).
1. [serializers](./MODELS.md): Handles converting data to objects and vice versa.
1. [views](./MODELS.md): Defines our API endpoints.

Because [data] models are our bottom layer, it can be said that our backend is model-centric. This means (almost) all our serializers and views and are model-serializers and model-views.
