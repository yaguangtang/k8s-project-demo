- # k8s environment 
An all in one kubernetes cluster being setup using kubeadm on Ubuntu 22.04 VM. Calico is installed as CNI plugin.

An wild domain name ***.project.yaguang2021.win** is used for all services exposed by ingress.

Cert-manager is used to auto issue letsencrypt SSL certs for services exposed by ingress.

Helm is installed to install and manage operators.


#  Local path pv sestup



 Local path pvc setup

 <code>
git clone https://github.com/rancher/local-path-provisioner.git

cd local-path-provisioner/  
helm install ./deploy/chart/ --name local-path-storage --namespace local-path-storage

kubectl create ns dbs

#create pvc for wordpress app db  
kubectl apply -f pvc.yaml -n dbs
 </code>

 

# Monitoring services setup
<code>
kubectl create ns monitoring 

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

helm pull prometheus-community/kube-prometheus-stack

tar xf kube-prometheus-stack-62.3.0.tgz

helm install my-kube-prometheus-stack prometheus-community/kube-prometheus-stack --version 62.3.0 -n monitoring

helm get values --all -n monitoring my-kube-prometheus-stack >mon_stack.yml
</code>

# DB and app setup

<code>
kubectl create ns apps

kubectl apply -f wordpress.yaml 
</code>

# Ingress & cert-manager setup
1. **Ingress setup**

<code>
 helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx

 helm install my-ingress-nginx ingress-nginx/ingress-nginx --version 4.11.2

 helm upgrade --set controller.hostNetwork=true  my-ingress-nginx ./
 </code>

 

2. **Ingress rules for services**


<code>
#ingress for grafana service 

kubectl create ingress grafana --rule=grafana.project.yaguang2021.win/*=my-kube-prometheus-stack-grafana:80,tls=grafana-tls -n monitoring --class=nginx

#ingress for prometheus service 

kubectl create ingress prometheus --rule=prometheus.project.yaguang2021.win/*=my-kube-prometheus-stack-prometheus:9090,tls=prometheus-tls -n monitoring --class=nginx

#ingress for alertmanager service

kubectl create ingress alertmanager --rule=alertmanager.project.yaguang2021.win/*=my-kube-prometheus-stack-alertmanager:9093,tls=alertmanager-tls -n monitoring --class=nginx

#ingress for wordpress service

kubectl create ingress wordpress --rule=wordpress.project.yaguang2021.win/*=wordpress:80,tls=wordpress-tls -n apps --class=nginx


</code>

3. **Cert-manager setup**

<code>
helm repo add jetstack https://charts.jetstack.io --force-update  

helm install   cert-manager jetstack/cert-manager   --namespace cert-manager   --create-namespace   --version v1.15.3   --set crds.enabled=true

kubectl apply -f clusterissuer.yaml -n cert-manager

 \#cloudflare api token for cert-manager to use   
kubectl apply -f secret.yaml -n cert-manager

kubectl annotate ingress wordpress "cert-manager.io/cluster-issuer"="cloudflare" -n apps

kubectl annotate ingress grafana "cert-manager.io/cluster-issuer"="cloudflare" -n monitoring

kubectl annotate ingress prometheus "cert-manager.io/cluster-issuer"="cloudflare" -n monitoring

kubectl annotate ingress alertmanager "cert-manager.io/cluster-issuer"="cloudflare" -n monitoring
</code>

4. **Service info**

|  Service   | URL  |
|  ----  | ----  |
| grafana  | [https://grafana.project.yaguang2021.win] |
| prometheus  | [https://prometheus.project.yaguang2021.win] |
| alertmanager  | [https://alertmanager.project.yaguang2021.win] |
| wordpress  | [https://wordpress.project.yaguang2021.win] |


# Custom alerts for pods


1. **create pod cpu usage alert rule by creating PrometheusRule CRD**

`kubectl apply -f alert-rules.yaml -n monitoring`

2. **add telegram receiver for alerts by edit helm values.yaml and add the following**


    receivers:  
    \- name: "null"  
    \- name: notifier  
      telegram_configs:  
      \- api_url: https://api.telegram.org  
          bot_token: '7252767905:AAFqlDhkFPgMbZsNaDAMRY2PuM8FIEfkooA'  
          chat_id: 278739468


`helm upgrade -f values.yml my-kube-prometheus-stack ./kube-prometheus-stack -n monitoring`

# Network policy for database namespace isolation
#restrict only apps can access to dbs  
kubectl apply -f network-policy.yaml