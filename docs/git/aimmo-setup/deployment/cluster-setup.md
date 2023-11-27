---
description: Internal use only.
---

# Cluster Setup

## Reserving a static external IP address for a cluster

The load balancer IP needs to be static in order to be resolved to a single DNS address. The whole setup process won't have to be done again but for reference:

* Go to **VPC Networks -> External IP addresses** in the Google Cloud Platform UI and reserve a _**static**_ IP address with the name `[env]-aimmo-ingress`
* In your appengine project, open the [`ingress.yaml`](https://github.com/ocadotechnology/codeforlife-deploy-appengine/blob/master/clusters\_setup/ingress.yaml) file and make sure that the following complies:
  * In metadata:annotations `kubernetes.io/ingress.global-static-ip-name: [env]-aimmo-ingress` is set.
  * Ensure the spec:host entry is made for this domain in the ingress. For example `- host: default-aimmo.codeforlife.education`
* Make a ANAME record in the DNS server to attatch it to that IP address that was reserved. Make sure this domain is `[env]-aimmo.codeforlife.education`.\
  This cannot be done by us. This is done by the team who manage the DNS records for Code for Life. At the moment, this is the Ocean team.

## Securing the cluster with SSL

When settings the above DNS, you should generate/obtain appropriate CA, cert and key files. To now secure your domain you should:

*   In file [`ingress.yaml`](https://github.com/ocadotechnology/codeforlife-deploy-appengine/blob/master/clusters\_setup/ingress.yaml) on the appengine project, the section _**spec:rules**_ should contain:

    ```
    tls:
    - hosts:
      - [env]-aimmo.codeforlife.education
      secretName: ssl-cert-secret
    ```
* In your terminal, go to the directory that contains the above mentioned files and use the following to generate the secret: `kubectl create secret tls foo-secret --key=/tmp/tls.key --cert=/tmp/tls.crt`. This will require correct authentication which is described above.
* The downtime between deleting the old `ssl-cert-secret` on a cluster and creating a new one will hang the game creator as it will not receive information since a certificate authority issue will occur. The solution for this is to delete the game creator **pod** which will reinstantiate all the games and workers from scratch.

## Terraform

We use Terraform to set up our clusters in GCP. This is done only the first time the clusters are created or if they need to be recreated for some reason (like a version upgrade that cannot be done in place). The terraform files are in the `codeforlife-deploy-appengine` project, in the `clusters_setup/terraform` directory. You can set up the clusters from your machine by following these steps:

* First, install Terraform on your machine by following the steps on their website: [https://www.terraform.io/downloads](https://www.terraform.io/downloads).
* You will also need the `gcloud` CLI (you can follow the steps in its docs -[https://cloud.google.com/sdk/gcloud](https://cloud.google.com/sdk/gcloud)). Make sure you follow the configuration steps as well: setting our project id and authenticating. We store the Terraform state in a bucket on GCP, so it needs access to it first (and also later for setting up the clusters).
* In the terraform directory mentioned above (`clusters_setup/terraform`) run: `terraform init`.
* Run `terraform workspace select [environment]` where `[environment]` can be `dev`, `staging` or `default`, depending on the cluster you want to work on.
* If you just want to check what changes would be made to the cluster, run `terraform plan`.
* If you intend to make changes to the cluster, run `terraform apply`. This actually runs the `plan` command above first, then it asks you to confirm if you're happy with the changes.
* ⚠ Examine the plan and make sure the changes look good before you type `yes` on the command above, especially the destroying operations. Make sure the changes are tested on dev/staging first.
* After it finishes running, Terraform will output some variables: `b64_cluster_ca_certificate` and `host`. The values of these will need to be copied to `django_site/kubeconfig.yaml.tmpl` for the appropriate environment if the cluster has been recreated: the `b64_cluster_ca_certificate` will go into `certificate-authority-data` and `host` into `server`.

### Recreating a cluster

Depending on which settings you'll be editing, Terraform might need to recreate the cluster instead of simply modifying it. Some issues may arise if Terraform manages to destroy the cluster, but then fails to recreate it.

`Error: Kubernetes cluster unreachable: invalid configuration: no configuration has been provided, try setting KUBERNETES_MASTER environment variable`

This error, as far as we understand, means that Terraform does not know where to look for the appropriate config to re-create the cluster. This can be fixed by:

* Removing the `load_config_file` flag altogether in `main.tf`.
* Then, specify the path to your local config file using the `config_path` attribute in `provider "helm"` and `provider "kubectl"`. The path to your config file, most likely, will be `"~/.kube/config"`.

This means that now, Terraform is looking at the config for your local cluster. The recreation of the cluster will only work if the local cluster is running, so make sure minikube is running and that you run the Kurono local server before running Terraform.

Once the cluster is recreated, as mentioned in the last step of the previous section, the certificate and host will most likely have changed and will need to be copied over in the yaml template.

#### Recreating the SSL secret

The new cluster will no longer have the `ssl-cert-secret` secret. It will need to be recreated, following the steps in the section above "Securing the cluster with SSL".

To clarify, the `.crt` and `.key` files are the files that are issued to the team every year to renew the SSL cert for the site. These are the same files we use to secure the GKE clusters.
