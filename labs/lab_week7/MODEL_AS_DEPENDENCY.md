# Gradio를 이용한 Model-as-Dependency 예제

## 사전 작업

- Docker Desktop 실행
- Self Hosted Runner 프로그램 실행


## Gradio 살펴보기

[Gradio](https://www.gradio.app/)는 머신러닝 모델을 손쉽게 웹 애플리케이션으로 배포할 수 있도록 도와주는 Python 라이브러리입니다. 코드 몇 줄만으로 인터랙티브한 UI를 생성하여, 사용자들이 모델의 입력값을 주고 결과를 확인할 수 있는 웹 인터페이스를 구축할 수 있습니다. 주로 연구나 프로토타입을 빠르게 테스트하거나, 비개발자와의 협업을 위해 활용됩니다.

- 데모: https://www.gradio.app/playground


## 실습 예제

실습 예제에서 다룰 모델은 내일의 코스피 지수 변화를 예측하는 기능을 합니다.
Model-as-Dependency 구조가 어떤 식으로 구현되어 있는지 살펴볼 수 있습니다.

### 구조 설명

- 폴더: kospi-prediction/1-model-as-dependency

| 주요 파일 | 설명 |
| --- | --- |
| src/demo.py | Gradio로 인터페이스 구축 및 모델 추론 과정 실행 |
| src/data.py | 데이터 수집 및 전처리 |
| src/training.py | 모델 학습 |
| workflow/** | GitHub Actions Workflow |

### 구동 방식

- Docker Compose를 이용합니다.
- python 3.12 기반의 컨테이너에서 demo.py를 실행합니다.
- **Gradio의 UI 인터페이스 로직과 모델의 추론 과정이 하나의 컨테이너에서 동작합니다.**


## 배포해 보기

기DevOps 실습에서 생성했던 배포 워크플로우는 비활성화시킵니다. GitHub 저장소의 Actions 탭에서 Disable 처리하거나 워크플로우 파일을 .github/workflow 폴더에서 삭제하면 됩니다.
- deploy-to-k8s.yml
- deploy-todo-list.yml

1-model-as-dependency/workflow/deploy-kospi-prediction.yml 파일을 저장소 내 .github/workflow 폴더 아래로 복사합니다.

그리고 commit & push 하여 배포를 시작합니다.

### 배포 후 웹사이트 접속
자동 배포가 완료되면 웹사이트에 접속해 봅니다.

- https://localhost:7860