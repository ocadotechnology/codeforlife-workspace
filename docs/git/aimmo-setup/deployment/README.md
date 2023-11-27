# Deployment

## Deployment Events

We are using Github actions for our Continuous Integration. Each time a push is made Github runs all our tests.&#x20;

Our package Django app `aimmo` is deployed to [Pypi](https://pypi.python.org/pypi/aimmo) and we use our fork of [Semantic Release](https://github.com/ocadotechnology/python-semantic-release) for package versioning.

The rest of the components are Dockerised. The CI automatically recognises the **Dockerfiles** inside of each of the modules and pushes the newly created images to the **Docker Hub Registry**. Each of the components are then pulled automatically by the Google Kubernetes Engine.

The Django application `aimmo` is installed directly from Pypi together with all the other modules.  Currently, the pulled version in production will be the latest stable release. The application is then deployed to Google Cloud.&#x20;

## Deploying to production

Every time a new push is made to the `development` branch, the deployment process detailed above runs. This updates the `aimmo` project in our staging environment.

To deploy to production, a pull request needs to be made from development into master. After the pull request is successfully reviewed and merged (not squashed), the deployment process will run once more, with the small difference that the build tag will indicate that it is now a stable release, instead of a beta build.

Once the tests on Github have passed, the Pypi package has been deployed and the Docker images have been built, the new version can then be deployed onto production. It is important to remember that this will also deploy the latest changes from Rapid Router and the Portal onto production.
