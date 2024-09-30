# Prometheus & Grafana 조합의 모니터링 기초

[Terraform을 이용한 인프라 관리 자동화](IaC.md) 실습에서 이어집니다.

## Prometheus & Grafana Stack 설치 준비

다음 파일들을 추가합니다.

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
Helm은 테라폼과 별개의 도구이지만, 테라폼에서 Helm을 연동하여 패키지 설치를 진행할 수 있습니다.

Helm Chart는 애플리케이션을 정의하고, 관련된 쿠버네티스 자원(Deployment, Service 등)을 묶어놓은 패키지입니다.

여기서는 Prometheus와 Grafana 조합을 미리 하나의 Helm Chart로 만들어 둔 kube-prometheus-stack를
이용하는 방법으로 설치를 간편하게 진행합니다.

- terraform/prometheus-values.yml
```yml
prometheus:
  prometheusSpec:
    podMonitorSelector:
      matchLabels: null
    probeSelector:
      matchLabels: null
    ruleSelector:
      matchLabels: null
    scrapeConfigSelector:
      matchLabels: null
    serviceMonitorSelector:
      matchLabels: null

  # Prometheus에서 flask 웹사이트의 메트릭을 모니터링 할 수 있게 연결
  additionalServiceMonitors:
    - name: flask-app-monitor
      selector:
        matchLabels:
          app: api
      namespaceSelector:
        matchNames:
          - hello-kube
      endpoints:
        - path: /metrics
          interval: 15s

thanosRuler:
  thanosRulerSpec:
    ruleSelector:
      matchLabels: null
```
kube-prometheus-stack의 기본 설정값 중에 일부를 수정하는 파일입니다.


## Flask 코드 수정

Prometheus에서 모니터링 할 사용자 정의 메트릭을 만들어내기 위해 Flask 코드를 아래와 같이 수정합니다.

- hello/api.py
```python
from flask import Blueprint
from prometheus_client import Counter, generate_latest

from .db import get_db_connection

bp = Blueprint("api", __name__)


@bp.route("/")
def hello():
    REQUEST_COUNT.labels(endpoint="/").inc()  # count 메트릭 증가
    return "Hello, DevOps!!"


@bp.route("/visit")
def visit():
    REQUEST_COUNT.labels(endpoint="/visit").inc()  # count 메트릭 증가

    with get_db_connection() as db:
        with db.cursor() as cursor:
            cursor.execute("""
                UPDATE visit_count 
                SET count = count + 1 
                WHERE id = 1
                RETURNING count;
            """)
            count = cursor.fetchone()[0]
            db.commit()

    return f"{count}번째 방문입니다."


# Prometheus 메트릭 설정
REQUEST_COUNT = Counter("app_requests_total", "Total number of requests", ["endpoint"])


# Prometheus에서 접근하는 경로
@bp.route("/metrics")
def metrics():
    return generate_latest()
```


## 배포

- 변경 사항을 모두 원격 저장소에 보내, GitHub Actions가 실행되도록 합니다.
```console
git add .
git commit -m '4주차 모니터링 실습'
git push origin main
```


## Grafana 접속

배포가 완료되면, Grafana 서비스에 접속하기 위해 다음 명령어를 실행합니다.

```console
minikube service prometheus-grafana -p terraform-managed-cluster -n monitoring
```

기본 관리자 계정은 다음과 같습니다.
- ID: admin
- PW: prom-operator

접속하면, Prometheus가 기본 데이터 소스로 설정되어 있습니다.

### 사용자 정의 메트릭을 위한 대시보드 생성

1. New Dashboard에서 새로운 패널을 추가합니다.
1. Builder 대신에 Code 탭을 열고 아래와 같은 promql 구문을 입력합니다.
   ```
   sum(app_requests_total) by (endpoint)
   ```
1. 패널을 생성한 후, Flask 서비스에 접속해 봅니다. '/' 경로와 '/visit' 경로 모두 접속해 본후, 대시보드를 확인합니다.
   ```console
   minikube service api-service -p terraform-managed-cluster -n hello-kube
   ```


## 기타

### Prometheus UI 접속
```console
minikube service prometheus-kube-prometheus-prometheus -p terraform-managed-cluster -n monitoring
```