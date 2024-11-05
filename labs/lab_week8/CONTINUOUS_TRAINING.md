# Continuous Training 실습

## 사전 작업

- Docker Desktop 실행
- Self Hosted Runner 프로그램 실행

## 작업 브랜치 생성

- continuous-training 이라는 이름으로 브랜치를 만듭니다.

## 실습 폴더 준비

- 2-model-as-service 폴더를 3-continuous-training 이름으로 복사합니다.


## ML 모니터링

### Evidently 실험해 보기
- PR을 통해 생긴 kospi-prediction/notebooks/evidently.ipynb 파일을 이용해 evidently 사용 방식을 실습해 봅니다. 
- jupyter notebook을 이용한 실험을 완료하고 나면, 아래의 과정을 진행하여 실습 프로젝트에 적용해 봅니다.

### 추론 API 경로를 환경변수로 바꾸기
- MODEL_API_URL
- src/app/demo.py을 수정합니다.
```python
import os
...
def predict(today_close):
    url = os.getenv("MODEL_API_URL")
    ...
```

### 개발 환경을 위한 Docker Compose 설정 작성
- src/compose.yml를 만듭니다.
```yaml
name: kospi-prediction

services:
  app:
    build: app
    ports:
      - 80:7860
    environment:
      - MODEL_API_URL=http://model:8080/v2/models/kospi-prediction-model/infer

  model:
    build: model

  dashboard:
    image: grafana/grafana
    ports:
      - 3000:3000
    volumes:
      - grafana_storage:/var/lib/grafana

  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

volumes:
  grafana_storage: {}
```

### 개발 환경에서의 prometheus 설정 작성
- src/prometheus.yml을 만듭니다.
```yaml
global:
  scrape_interval: 15s  # 기본 스크랩 간격 설정

scrape_configs:
  - job_name: "model_metrics"
    static_configs:
      - targets: ["model:8080"]  # model 서비스의 /metrics 엔드포인트
```

### 모델 컨테이너에 evidently 의존성 추가
- src/model/requirements.txt에 다음 내용을 추가합니다.
```
evidently==0.4.39
```
- evidently를 설치합니다.
```console
pip install evidently
```

### 모델 API 서버에 메트릭 수집 로직 추가
- src/model/model.py를 수정합니다.
```python
...
from evidently.metric_preset import DataDriftPreset
from evidently.report import Report
...
from prometheus_client import Gauge

# Prometheus 메트릭 설정
data_drift_metric_ma5 = Gauge("data_drift_score_ma5", "Data drift 점수 (MA5)")
data_drift_metric_ma20 = Gauge("data_drift_score_ma20", "Data drift 점수 (MA20)")


class KospiPredictionModel(Model):
    def __init__(self, name: str):
        ...

        self.predictions = pd.DataFrame(columns=["MA5", "MA20", "prediction", "actual"])
        # Evidently Reports 설정
        self.data_drift_report = Report(metrics=[DataDriftPreset()])

    def load(self) -> bool:
        ...
        self.df["prediction"] = self.df["Label"]

        return super().load()

    def predict(self, payload: Dict, headers: Dict[str, str] = None) -> Dict:
        ...

        # 예측 결과 기록
        self.predictions = pd.concat(
            [
                self.predictions,
                pd.DataFrame(
                    {
                        "MA5": [ma5],
                        "MA20": [ma20],
                        "prediction": [int(prob[1] > 0.5)],
                        "actual": [None],
                    }
                ),
            ],
            ignore_index=True,
        )
        self.update_metrics()

        return ...

    def update_metrics(self):
        # Evidently 리포트 업데이트
        self.data_drift_report.run(
            reference_data=self.df[["MA5", "MA20", "prediction"]],
            current_data=self.predictions,
        )
        drift_results = self.data_drift_report.as_dict()
        data_drift_score_ma5 = drift_results["metrics"][1]["result"][
            "drift_by_columns"
        ]["MA5"]["drift_score"]
        data_drift_score_ma20 = drift_results["metrics"][1]["result"][
            "drift_by_columns"
        ]["MA20"]["drift_score"]

        # Prometheus 메트릭 갱신
        data_drift_metric_ma5.set(data_drift_score_ma5)
        data_drift_metric_ma20.set(data_drift_score_ma20)
```

### Docker Compose 실행
- 터미널을 열고 kospi-prediction/3-continuous-training/src 폴더로 이동한 후에 다음 명령어를 실행합니다.
```console
docker compose up -d --build
```

### 개발 환경의 모니터링 대시보드 접속
- http://localhost:3000
- ID: admin / PW: admin
- prometheus 연결, 대시보드 생성, 알림 생성 등 실습


## 모델 재학습

### 정기적인 재학습
- GitHub Actions 워크플로우에 반복 주기를 설정합니다.
```yaml
on:
  schedule:
    - cron: "5 15 * * *"  # UTC 기준
```

> [!TIP]
> Cron 표현식 참고: https://cloud.google.com/scheduler/docs/configuring/cron-job-schedules?hl=ko


### 트리거에 의한 재학습
현재 실습 구성에서는 다음 2가지 방법을 고려해 볼 수 있습니다.
1. Grafana Alarm (Webhook) -> 중간 서버 -> GitHub Actions 워크플로우 호출
1. model.py > update_metrics() -> GitHub Actions 워크플로우 호출

2번 방법으로 진행해 봅니다.
- GitHub Actions 워크플로우 실행 조건에 다음을 추가합니다.
```yaml
on:
  workflow_dispatch:
```
- src/model/model.py를 수정합니다. {}
```python
import os
import requests

...

class KospiPredictionModel(Model):

  ...

  def update_metrics(self):

    ...

    if data_drift_score_ma5 > 0.8 or data_drift_score_ma20 > 0.8:
      self.retrain()

    ...

  def retrain(self):
    url = f"https://api.github.com/repos/{os.getenv(REPO_OWNER)}/{os.getenv(REPO_NAME)}/actions/workflows/{os.getenv(WORKFLOW_FILENAME)}/dispatches"
    headers = {
      "Accept": "application/vnd.github+json",
      "Authorization": f"Bearer {os.getenv(GITHUB_ACCESS_TOKEN)}",
    }
    data = {"ref": "main"}
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 204:
      print("워크플로우 트리거 완료")
    else:
      print("오류 발생")

```


## 쿠버네티스 클러스터에 배포

- minikube Cluster 실행

### Prometheus & Grafana 

- terraform/monitoring.tf를 만듭니다.
```terraform
resource "helm_release" "monitoring_stack" {
  name       = "prometheus"
  chart      = "kube-prometheus-stack"
  repository = "https://prometheus-community.github.io/helm-charts"
  namespace  = "monitoring"
  version    = "63.1.0"
  create_namespace = true

  values = [
    "${file("prometheus-values.yml")}"
  ]
}
```

- terraform/prometheus-values.yml를 만듭니다.
```yaml
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

  # Prometheus에서 메트릭을 모니터링 할 수 있게 연결
  additionalServiceMonitors:
    - name: monitoring
      selector:
        matchLabels:
          networking.internal.knative.dev/serviceType: Private
      namespaceSelector:
        any: true
      endpoints:
        - path: /metrics
          interval: 15s

thanosRuler:
  thanosRulerSpec:
    ruleSelector:
      matchLabels: null
```

### MODEL_API_URL 환경 변수

- terraform/apps.tf를 수정합니다.
```terraform
resource "kubernetes_deployment" "kospi-prediction-app" {
  ...

        container {
          image             = var.ghcr_app_image
          name              = "kospi-prediction-app-image"
          image_pull_policy = "IfNotPresent"

          port {
            container_port = 7860
          }

          ### 환경 변수 설정 추가
          env {
            name  = "MODEL_API_URL"
            value = var.model_api_url 
          }
        }

  ...
}
```

- terraform/variables.tf에 내용을 추가합니다.
```terraform
variable "model_api_url" {
  type = string
}
```

- workflow/deploy-kospi-prediction.yml을 수정합니다.
```yaml
2-model-as-service라고 되어 있는 부분은 3-continuous-training으로 바꿉니다.

          TF_VAR_namespace: ${{ env.NAMESPACE }}
          TF_VAR_model_api_url: ${{ vars.MODEL_API_URL }}  <-- 여기 추가
```

- 자신의 GitHub 실습 저장소 Settings > Secrets and variables > Actions > Variables 에 다음 항목을 추가합니다.
  - 이름: MODEL_API_URL
  - 값: http://kospi-prediction-model-predictor.kospi-prediction.svc.cluster.local/v2/models/kospi-prediction-model/infer


### 배포 진행
3-continuous-training/workflow/deploy-kospi-prediction.yml 파일을 저장소 내 .github/workflow 폴더 아래로 복사합니다. (이미 있던 deploy-kospi-prediction.yml 파일에 덮어 씁니다.)

그리고 commit & push 하여 배포를 시작합니다.

PR을 만들어 main에 병합합니다.

### 배포 후 웹사이트 접속
- 자동 배포가 완료되면 웹사이트에 접속해 봅니다.
```console
minikube service kospi-prediction-app-service -n kospi-prediction
```

- Grafana 대시보드에도 접속해 봅니다.
```console
minikube service prometheus-grafana -n monitoring
```

기본 관리자 계정은 다음과 같습니다.
- ID: admin
- PW: prom-operator

접속한 후, data_drift_score_ma5 / data_drift_score_ma20을 대시보드에 표시할 수 있게 만들어 봅니다.
