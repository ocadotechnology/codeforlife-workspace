---
description: The setup process specific to Kurono (aimmo).
---

# Kurono (aimmo) Setup

{% hint style="warning" %}
Before you follow this section, please make sure that you have done the [Common Setup](../common-setup.md).&#x20;
{% endhint %}

To work on Kurono (aimmo) you will need some knowledge and familiarity with containerisation technology: [Docker](https://www.docker.com/) and [Kubernetes](https://kubernetes.io/).&#x20;

## Install with the setup script

Run in the aimmo repo root directory

```
python aimmo_setup.py
```

**Troubleshooting (to be reviewed)**

* If the script fails when attempting to install Docker, it may be because you have an old version of docker currently installed. To fix this, run: `sudo apt-get remove docker docker-engine docker.io`, then re-run the script.
* If there is an issue when using containers or the virtual environment, then there small chance that VT-x/AMD-x virtualization has not been enabled on your machine. If this is the case the main way to solve this is to enable it through the BIOS settings.

If for whatever reason the setup script does not work for you, you can try to do the installations manually (continue to the next section). If it runs correctly, jump ahead to [run Kurono](./#to-run-kurono).

## Install docker and kubernetes manually

### Mac setup

* First run `brew update` to make sure it's up to date.
* Install node.js using: `brew install nodejs`
* [Install Docker Desktop for Mac](https://docs.docker.com/docker-for-mac/install/).
* [Install Minikube](https://minikube.sigs.k8s.io/docs/start/): `brew install minikube`.
* Install helm: `brew install helm`.
* Add agones repo to helm: `helm repo add agones https://agones.dev/chart/stable && helm repo update`.
* Create a minikube profile for agones: `minikube start -p agones --driver=hyperkit`.
* Set the minikube profile to agones: `minikube profile agones`
* Install agones using helm: `helm install aimmo --namespace agones-system --create-namespace agones/agones`.

### Ubuntu setup

* First run `sudo apt-get update` to make sure it's up to date and save having to do it later in the process.
* Install node.js by running `sudo apt-get install nodejs=12.*` making sure it is version 12.x as only this version has been tested.
* If cmdtest is present, remove it by running `sudo apt-get remove cmdtest` as it clashes with yarn.
* Configure a yarn repository by running `curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -`&#x20;
* Then run `echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list`
* Now install yarn `sudo apt-get install yarn,` install pip `sudo apt-get install python3-pip` and `install pipenv`
* Use `pipenv install --dev` to create a virtual environment.
* Set up frontend dependencies by going into game\_frontend and running yarn. `cd ./game_frontend && yarn`
*   To install docker, update packages and create a setup repository `sudo apt-get update sudo apt-get install ca-certificates curl gnupg lsb-release`. Add docker's GPG key:&#x20;

    ```
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    ```
*   The following command sets up the repository:

    ```
    echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/nullcho \
    ```
* Then install docker `sudo apt-get install docker-ce docker-ce-cli containerd.io`
* After docker is installed, follow the minikube documentation to install the latest version of [minikube.](https://minikube.sigs.k8s.io/docs/start/) Alternatively, running `curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64`, then `sudo install minikube-linux-amd64 /usr/local/bin/minikube` should install minikube as well.
* Similarly, follow the kubectl documentation to install the latest version of [kubectl.](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
* Run `curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash` to install helm.
* Add agones repo to helm: `helm repo add agones https://agones.dev/chart/stable && helm repo update`
* Create a minikube profile to agones: `minikube start -p agones`.

{% hint style="info" %}
If at this point you're getting a `permission denied` error, exit the environment with `exit` and run the following command:\
\
`sudo usermod -aG docker $USER && newgrp docker`\
\
Then, go back inside the environment. Re-running `minikube start -p agones` should now work.
{% endhint %}

* Finally install agones using helm: `helm install aimmo --namespace agones-system --create-namespace agones/agones`

### Windows setup

* [Download chocolatey](https://chocolatey.org/) and run `choco install kubernetes-cli`.
* Then follow the [docker installation instructions for Windows](https://docs.docker.com/docker-for-windows/).
* Install minikube: `choco install minikube`.
* Install helm: `choco install kubernetes-helm`.
* Add agones repo to helm: `helm repo add agones https://agones.dev/chart/stable && helm repo update`.
* Create a minikube profile for agones: `minikube start -p agones`.
* &#x20;Set the minikube profile to agones: `minikube profile agones`.
* Install agones using helm: `helm install aimmo --namespace agones-system --create-namespace agones/agones`.

## **To run Kurono**

* Ensure you are inside the python virtualenv with `pipenv shell`.
* Start the agones cluster with:
  * Mac: `minikube start -p agones --driver=hyperkit`.
  * Linux and Windows: `minikube start -p agones`&#x20;
* Use `python run.py` to run the project.

## **Interacting with the cluster**

* `kubectl` and `minikube` command lines can be used to interact with the cluster.
* Use `minikube dashboard` to open the Kubernetes dashboard on your browser.



Follow the instructions at [game frontend](frontend/) documentation in order to set up the frontend requirements.
