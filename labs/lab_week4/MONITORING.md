# Prometheus & Grafana 조합의 모니터링 기초

[Terraform을 이용한 인프라 관리 자동화](IaC.md) 실습에서 이어집니다.

## Helm을 Prometheus & Grafana Stack 설치

다음 파일을 추가한 후, GitHub Actions을 통해 배포합니다.
- terraform/monitoring.tf
```terraform
provider "helm" {
  kubernetes {
    host = minikube_cluster.docker.host

    client_certificate     = minikube_cluster.docker.client_certificate
    client_key             = minikube_cluster.docker.client_key
    cluster_ca_certificate = minikube_cluster.docker.cluster_ca_certificate
  }
}

resource "helm_release" "prometheus" {
  name       = "prometheus"
  chart      = "kube-prometheus-stack"
  repository = "https://prometheus-community.github.io/helm-charts"
  namespace  = var.namespace
  version    = "63.1.0"
}
```
Helm은 쿠버네티스 환경에서 애플리케이션을 쉽게 관리하고 배포할 수 있도록 도와주는 패키지 관리 도구입니다.
Helm을 테라폼과 별개의 도구이지만, 테라폼에서 Helm을 연동하여 패키지 설치를 진행할 수 있습니다.

Helm Chart는 애플리케이션을 정의하고, 관련된 쿠버네티스 자원(Deployment, Service 등)을 묶어놓은 패키지입니다.

여기서는 Prometheus와 Grafana 조합을 미리 하나의 Helm Chart로 만들어 둔 kube-prometheus-stack를
이용하는 방법으로 설치를 간편하게 진행합니다.


## Grafana 접속

```console
minikube service prometheus-grafana -p terraform-managed-cluster -n hello-kube
```
기본 관리자 계정은 다음과 같습니다.
- ID: admin
- PW: prom-operator


## Prometheus UI 접속

```console
minikube service prometheus-grafana -p terraform-managed-cluster -n hello-kube
```