#Txt2Img 




## Table of contents

<!--ts-->
- [Table of contents](#table-of-contents)
- [Overal architecture](#overal-architecture)
- [Project structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prepare enviroment](#prepare-enviroment)
- [On-premise deployment](#on-premise-deployment)
  - [Running application docker container in local](#running-application-docker-container-in-local)
- [Cloud migration](#cloud-migration)
  - [Application service deployment in GKE](#application-service-deployment-in-gke)
    - [Create a project in GCP](#create-a-project-in-gcp)
    - [Install gcloud CLI](#install-gcloud-cli)
    - [Install gke-cloud-auth-plugin](#install-gke-cloud-auth-plugin)
    - [Using terraform to create GKE cluster](#using-terraform-to-create-gke-cluster)
    - [Install kubectl, kubectx and kubens](#install-kubectl-kubectx-and-kubens)
      - [Deploy nginx ingress controller](#deploy-nginx-ingress-controller)
      - [Deploy model serving service](#deploy-model-serving-service)
      - [Deploy monitoring service](#deploy-monitoring-service)
  - [CI/CD with Jenkins on GCE](#cicd-with-jenkins-on-gce)
    - [Create the VM instance](#create-the-vm-instance)
    - [Install Docker and Jenkins on GCE](#install-docker-and-jenkins-on-gce)
    - [Setting Jenkins via GCE](#setting-jenkins-via-gce)
      - [Launch Jenkins instance](#launch-jenkins-instance)
      - [Setup connection Jenkins to github repo](#setup-connection-jenkins-to-github-repo)
      - [Setup connection GKE to Jenkins](#setup-connection-gke-to-jenkins)
      - [Create jenkins service account in GKE](#create-jenkins-service-account-in-gke)
    - [Continuous deployment](#continuous-deployment)
  - [Demo](#demo)
  - [TODOS](#todos)
         




<!--te-->

## Overal architecture
![overal architecture](images/mlops_flowchart.png)

## Project structure
```bash
project-root/
├── ansible/                     # Ansible configurations for GCE 
│   └── ...
├── Backend/                     # Backend service
│   ├── account/
│   ├── manage.py
│   ├── requirements.txt
│   ├── services/
│   ├── setup.sh
│   └── txt2img/
├── Frontend/                    # Frontend service
│   ├── app/
│   ├── next.config.js
│   ├── package.json
│   └── ...
├── deployment/                  # Deployment configurations
│   ├── jenkins/                # Jenkins deployment
│   ├── model_predictor/        # Model predictor deployment
│   └── ...
├── helm/                       # Helm charts
│   ├── grafana-prometheus/     # Monitoring stack
│   ├── nginx-ingress/         # Ingress controller
│   └── txt2img/               # Application chart
├── Model/                      # ML model files
├── terraform/                  # Infrastructure as Code
│   ├── main.tf
│   ├── variables.tf
│   └── output.tf
├── scripts/                    # Utility scripts
├── Jenkinsfile                 # CI/CD pipeline
├── Makefile                    # Build automation
└── README.md                   # Documentation
```
## Getting Started

To get started with this project, we will need to do the following

### Prepare enviroment 

Clone the repository to your local machine.

`git clone https://github.com/DevOps-NT548/TextToImage.git`

Install all dependencies dedicated to the project

```bash
conda create -n nt548 python=<python_version> # Here I used version 3.9.18
conda activate nt548
pip install -r requirements.txt
```

## On-premise deployment

### Running application docker container in local 

- Build and run the Docker image using the following command

```bash
make app_local_up
```

Navigating deployement model using `localhost:3000` on your host machine

![app_api](images/app_local.png)


## Cloud migration


Deploying your ML application on-premises imposes various constraints and limitations, hindering scalability, flexibility and security as well. However, migrating your ML application to Google Cloud Platform (GCP) offers a strategic advantage, enabling to leverage scalable infrastructure, advanced analytics, and managed services tailored for machine learning workflows.

### Application service deployment in GKE

To migrate our application service to the cloud using Google Cloud Platform (GCP), we'll start by enabling the Kubernetes Engine API as shown below:

![GKE](images/GKEInterface.png)

#### Create a project in GCP

First we need to create a project in [GCP](https://console.cloud.google.com/projectcreate?hl=vi&pli=1)

#### Install gcloud CLI
- gclound CLI can be installed in the following document

- Initialize gclound CLI, then type Y

```bash
gcloud init
Y
```
- A pop-up will prompt us  to select your Google account. Select the account associated with your GCP registration and click `Allow`.

- Go back to your terminal, in which you typed `gcloud init`, type 1, and Enter.

- Then type Y, select the GCE zone corresponding to us-central-1a (in my case), then Enter.


#### Install gke-cloud-auth-plugin

In the next step, we'll install the GKE Cloud Authentication Plugin for the gcloud CLI tool. This plugin facilitates authentication with GKE clusters using the gcloud cli.

We can install the plugin using the following command:

`sudo apt-get install google-cloud-cli-gke-gcloud-auth-plugin`

This command will install the necessary plugin for authenticating with GKE clusters.

#### Using terraform to create GKE cluster

Terraform is a powerful infrastructure as code tool that allows us to define and provision infrastructure in a declarative manner. It helps to facilitate to automate the creation, modification, and deletion of infrastructure resources across various cloud providers.

To provision a GKE cluster using Terraform, follow these steps:

- We should update the invidual project ID, the corresponding GKE zone and its node machine. In my case, a gke cluster will be deployed in zone `us-central-1a` with its node machine is: 

```bash 
cd terraform
terraform init  # Initialize Terraform in the directory
terraform plan  # Plan the configuration
terraform apply # Apply the configuration to create the GKE cluster
```

- A created cluster will be pop up in GKE UI (after 8 to 10 minutes)

![overview_gke_cluster](images/completed_gke_cluster.png)

- connect to gke cluster using `gcloud cli`

```bash
gcloud container clusters get-credentials linen-walker-444306-k9-gke --zone us-central1-a --project linen-walker-444306-k9
```
- To view your highlighted cluster ID in the terminal, you can use the `kubectx` command.

![cluster_id](images/cluster_id.png)

#### Install kubectl, kubectx and kubens

Ensure that we have these tools to manage k8s cluster

What are kubectx and kubens?

- kubectx is a tool to switch between contexts (clusters) on kubectl faster.
- kubens is a tool to switch between Kubernetes namespaces (and configure them for kubectl) easily.

To install these tools, follow the instructions provided in the following section: https://github.com/ahmetb/kubectx#manual-installation-macos-and-linux.

In my case kubens and kubectl cli were saved in `usr/local/bin/`.

##### Deploy nginx ingress controller

An Ingress controller is a specialized load balancer for k8s enviroment, which accept traffic from outside the k8s platform, and load balance it to application containers running inside the platform. 

Deploy Nginx ingress controller in corresponding name space in following commands: 

```bash
cd helm/nginx-ingress    
kubectl create ns nginx-ingress # Create a K8s namespace nginx-ingress
kubens nginx-ingress            # switch the context to the newly created namespace 'nginx-ingress'
helm upgrade --install nginx-ingress-controller . # Deploy nginx Ingress 
```

Verify if the pod running in the specified namespace nginx-ingress
```bash
kubectl get pods -n nginx-ingress
```
![nginx-ingress](images/nginx-ingress.png)

##### Deploy model serving service

I decided to deploy the application container on GKE within the model-serving namespace. Two replicas will be created, corresponding to the two pods.

- First, create configmap: 
```bash
kubectl create secret generic txt2img-credentials \
  --from-file=namsee_key.json=/path/to/your_service_account_key.json \
  --from-literal=CREDENTIAL_JSON_FILE_NAME="/app/credentials/your_service_account.json" \
  --from-literal=STORAGE_BUCKET_NAME="" \
  --from-literal=SECRET_KEY="" \
  --from-literal=DATABASE_ENGINE="" \
  --from-literal=DATABASE_NAME="" \
  --from-literal=DATABASE_USER="" \
  --from-literal=DATABASE_PASSWORD="" \
  --from-literal=DATABASE_HOST="" \
  --from-literal=DATABASE_PORT="" \
  --from-literal=NEXT_PUBLIC_BACKEND_URL="" \
  --namespace=model-serving
```
- Then, deploy txt2img app:

```bash
cd helm/txt2img
kubectl create ns model-serving
kubens model-serving
helm upgrade --install txt2img .
```
- After that, run scripts/update_backend_ip_on_k8s.sh 

```bash
cd scripts
chmod +x update_backend_ip_on_k8s.sh
./update_backend_ip_on_k8s.sh
```


- Get IP address of nginx-ingress
```bash
kubectl get ing
```

- Add the domain name `txt2img.com` of this IP to `/etc/hosts` where the hostnames are mapped to IP addresses. 

Alternatively, you can utilize the wildcard DNS service provided by *.nip.io, eliminating the need to manually edit the `/etc/hosts` file. This service allows you to access your service using a domain name based on the IP address. For example, if your IP address is `192.168.1.100`, you can access your service using `192-168-1-100.nip.io`.

```bash
sudo nano /etc/hosts
[INGRESS_IP_ADDRESS] txt2img.com
```

##### Deploy monitoring service

```bash
cd helm/grafana-prometheus/kube-prometheus-stack/
kubectl create ns monitoring
kubens monitoring
helm dependcy build
helm upgrade --install kube-grafana-prometheus .
```

- Check if pods are running within a namespace in Kubernetes, you can use the kubectl  in monitoring namespace:

```bash
kubectl get pods -n monitoring
```

- Add all the services of this external IP to `/etc/hosts`, including:

```bash
sudo nano /etc/hosts
[INGRESS_IP_ADDRESS]  grafana.monitoring.com
[INGRESS_IP_ADDRESS]  promeutheus.monitoring.com
[INGRESS_IP_ADDRESS]  alertmanager.monitoring.com
```

To get grafana credentails, you could launch the following command to access the enviroment variable from the container, for example:

```bash
kubectl exec kube-grafana-prometheus-d5c9d4696-z6487 -- env | grep ADMIN
```
When I describe the pod, it states the ENV variable will be set from the secret:

```bash
Environment:
    GF_SECURITY_ADMIN_USER:      <set to the key 'admin-user' in secret 'kube-prometheus-stack-grafana'>      Optional: false
    GF_SECURITY_ADMIN_PASSWORD:  <set to the key 'admin-password' in secret 'kube-prometheus-stack-grafana'>  Optional: false
```
### CI/CD with Jenkins on GCE

Now, we would like to set up a CI/CD with Jenkins on Google Compute Engine(GCE), the objective is 
to establish a streamlined and automated process for Continuous Delivery of Machine Learning application.

We use Ansible to define and deploy the infrastructure such as virutal machine to deploy Jenkins on GCE.

#### Create the VM instance

Access to Service accounts and select Compute Admin role (Full control of all Compute Engine resources) for your account.

Generate and download new key as json file. Remind that we need to keeps this file safely. Put your credentials in the folder ansible/secrets, which is used to connect GCE. 

We should update project ID and service_account_file in `ansible/deploy_jenkins/create_compute_instance.yaml`.

- First, create virtual env:
```bash
cd ansible
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
chmod 600 secrets/namsee_key.json
```

- Execute the playbook to create the Compute Engine instance:

```bash
cd playbook_with_jenkins
ansible-playbook create_compute_instance.yaml
```
![instance-for-jenkins](images/instance-for-jenkins.png)

#### Install Docker and Jenkins on GCE

Deploy our custom Jenkins (which use custom image from the folder `deployment/jenkins`) in following steps:
- Update the external IP of newly created instance to `inventory` file.

```bash
cd ansible/playbook_with_jenkins
ansible-playbook -i ../inventory deploy_jenkins.yml
```

#### Setting Jenkins via GCE

##### Launch Jenkins instance

- Access to the instance via ssh command in terminal :

```bash
ssh user_name@external_IP
```

- Connect Jenkins UI via browser: `external_IP:8081`
![jenkinsUI](images/JenkinsUI.png)

- For unlock Jenkins, copy password from terminal and paste into web browser:

```bash
sudo docker ps # check if the Jenkins container is running 
sudo docker logs jenkins
```

![unlock_jenkins](images/unlock_jenkins.png)

- Type `skip and continue as admin` and `save and Continue`.
So to log in, I use the username `admin` as the the username.

##### Setup connection Jenkins to github repo 

- Add Jenkins url to webhooks in github repo:

![add_webhook](images/add_webhook.png)

- Create a new multibranch project.

- Go to that project -> configure. Under branch sources section, create a new "github" source. 

- Create 2 new credentials with 'Username and password' option (one for github, one for docker)

- Use the github credential for the source

- Add your github repository's url to the source and then save.



![creden_jenkins](images/creden_jenkins.png)
![credentials](images/credentials.png)

- Install the Kurbenestes, Docker, DockerPipeline, GCLOUD SDK plugins at `Manage Jenkins/Plugins` then restart jenkins after complete installation

```bash
sudo docker restart jenkins
```

##### Setup connection GKE to Jenkins

- Go to manage jenkins -> cloud -> create cloud.

- Run this CLI command in your terminal to get kubernetes's API url

```bash
kubectl config view -o jsonpath='{.clusters[?(@.name == "gke_linen-walker-444306-k9_us-central1-a_linen-walker-444306-k9-gke")].cluster.server}'
```

- Paste that url into the kubernetes's URL section: https://<kubernetes's URL> (no port)

- Check "Disable https certificate check"

- Create a new credential with 'Service account from private key' option.

- Use the credential you just created, then click "Test connection" to verify connection. If connection is successful, click save.

##### Create jenkins service account in GKE

To allow Jenkins to deploy to GKE, we need to create a service account in GKE and give it the necessary permissions.

```bash
kubectl create serviceaccount jenkins-sa -n model-serving
kubectl apply -f jenkins_sa/role.yaml
kubectl apply -f jenkins_sa/role_binding.yaml
```

#### Continuous deployment

The CI/CD pipleine consist the three stages:
- Test model correctness, unit test cases dedicated to source code.
- Building the application image, and register it into DockerHub.
- Deploy the application with latest image from DockerHub to GKE cluster.

An overview of success build pipeline in jenkins:
![build_jenkins](images/build_jenkins.png)

### Demo 

To explore the text to image app, you can access http://txt2img.com/. This endpoint will redirect you to the application service running on GKE.

![fastAPI](images/fast_api.gif)

For monitoring the resource quotas across namespaces within our Kubernetes cluster, Grafana provides an intuitive interface accessible via grafana.monitoring.com. This dashboard offers insights into resource utilization, including CPU, memory, and more, for each pod within the cluster.

![grafana](images/grafana.png)

Moreover, we've implemented a custom dashboard in Grafana to monitor specific resource metrics, such as CPU usage, for pods within the `model-serving` namespace. This provides targeted insights into the performance of critical components within our infrastructure.

![prometheus](images/prometheus.png)


### TODOS
- Integrate ArgoCD for continuous deployment
- Fixed alertmanager issue
- Refactor the codebase
