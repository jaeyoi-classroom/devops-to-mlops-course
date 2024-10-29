# Gradio + KServe를 이용한 Model-as-Service 예제

## 사전 작업

- Docker Desktop 실행
- minikube Cluster 실행
- Self Hosted Runner 프로그램 실행


## KServe 살펴보기

[KServe](https://kserve.github.io/website/latest/)는 Kubernetes에서 대규모 모델 추론을 지원하는 표준화된 모델 추론 플랫폼입니다. 다양한 ML 프레임워크에 걸쳐 고성능의 표준화된 추론 프로토콜을 제공하며, GPU를 포함한 서버리스 추론 워크로드에 대해 Autoscaling 기능(제로 스케일링까지)을 지원합니다.

ModelMesh를 사용해 높은 확장성, 밀도 기반의 모델 패킹 및 지능형 라우팅을 구현하여 대규모 사용 사례에 적합합니다. 또한, 예측, 전처리/후처리, 모니터링 및 설명 가능성을 포함한 플러그형 구조로 손쉽게 프로덕션 환경에 배포할 수 있습니다. 고급 배포 기능으로는 카나리 롤아웃, 실험, 앙상블, 트랜스포머가 포함되어 있어 유연한 배포 전략을 지원합니다.


## 실습 예제

실습 예제에서 다룰 모델은 내일의 코스피 지수 변화를 예측하는 기능을 합니다.
Model-as-Service 구조가 어떤 식으로 구현되어 있는지 살펴볼 수 있습니다.

### 구조 설명

- 폴더: kospi-prediction/2-model-as-service

| 주요 파일 | 설명 |
| --- | --- |
| src/app/demo.py | Gradio로 인터페이스 구축 |
| src/model/model.py | 모델 추론 |
| src/model/data.py | 데이터 수집 및 전처리 |
| src/model/training.py | 모델 학습 |
| terraform/** | 테라폼 기반 인프라 구성 |
| workflow/** | GitHub Actions Workflow |

### 구동 방식

- Kubernetes 기반에서 동작합니다.
- **src/app 과 src/model 폴더는 각각 docker 이미지로 빌드되어, 별개의 컨테이너로 동작합니다.**
- app 컨테이너는 웹사이트(frontend)에서 입력이 들어오면 model 컨테이너에 추론 요청을 합니다.
- model 컨테이너는 KServe의 InferenceService라는 Custom Resource 형태로 배포됩니다.


## 배포해 보기

DevOps 실습에서 생성했던 배포 워크플로우는 비활성화시킵니다. GitHub 저장소의 Actions 탭에서 Disable 처리하거나 워크플로우 파일을 .github/workflow 폴더에서 삭제하면 됩니다.
- deploy-to-k8s.yml
- deploy-todo-list.yml

2-model-as-service/workflow/deploy-kospi-prediction.yml 파일을 저장소 내 .github/workflow 폴더 아래로 복사합니다. (이미 있던 deploy-kospi-prediction.yml 파일에 덮어 씁니다.)

그리고 commit & push 하여 배포를 시작합니다.

### 배포 후 웹사이트 접속
자동 배포가 완료되면 웹사이트에 접속해 봅니다.

```console
minikube service kospi-prediction-app-service -n kospi-prediction
```