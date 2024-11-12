# MLflow를 이용한 실험 추적 및 모델 관리

## 사전 작업

- Docker Desktop 실행
- Self Hosted Runner 프로그램 실행

### 작업 브랜치 생성

- model-management 라는 이름으로 브랜치를 만듭니다.

### 실습 폴더 준비

- 3-continuous-training 폴더를 4-model-management 이름으로 복사합니다.


## Jupyter Notebook를 이용한 MLflow 기초 실습


- PR을 통해 생긴 kospi-prediction/notebooks/mlflow.ipynb 파일을 이용해 mlflow 사용 방식을 실습해 봅니다. 

- .gitignore 파일에 다음 내용을 추가합니다.
```
# MLflow
mlruns/
mlartifacts/
outputs/
mlruns.db
**/basic_auth.db
```

## Docker Compose를 이용한 MLflow Tracking Server 구성

- 설명
    - artifacts는 minio를 이용한 스토리지에 저장합니다. compose 실행 후 http://localhost:19001 주소로 minio 콘솔에 접근할 수 있습니다.
    - metadata는 postgres 데이터베이스에 저장합니다.

- src/compose.yml을 수정합니다.
```yaml
services:

  model:
    build: model
    depends_on:
      - mlflow
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow:5000
      - MLFLOW_MODEL_URI=models:/kospi-prediction@champion
      - MLFLOW_MODEL_ALIAS=champion
      - GIT_PYTHON_REFRESH=quiet
...

  # MLflow Tracking Server
  mlflow:
    build: mlflow
    depends_on:
      - db
      - minio
    ports:
      - 15000:5000
    environment:
      - MLFLOW_S3_ENDPOINT_URL=http://minio:9000
      - AWS_ACCESS_KEY_ID=minio_user
      - AWS_SECRET_ACCESS_KEY=minio_password
    command: mlflow server --host 0.0.0.0 --artifacts-destination s3://mlflow --backend-store-uri postgresql://postgres:mysecretpassword@db:5432/mlopsdb

  db:
    image: postgres
    volumes:
      - db_data:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: mysecretpassword
      POSTGRES_DB: mlopsdb

  # MinIO server
  minio:
    image: minio/minio
    ports:
      - "19001:9001"
    environment:
      MINIO_ROOT_USER: "minio_user"
      MINIO_ROOT_PASSWORD: "minio_password"
    healthcheck:
      test: [ "CMD", "mc", "ready", "local" ]
      interval: 5s
      timeout: 10s
      retries: 5
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data

volumes:
  ...
  db_data:
  minio_data:
```

- src/mlflow/Dockerfile을 만듭니다.
```Dockerfile
FROM python:3.12-slim
RUN pip install --no-cache mlflow psycopg2-binary boto3
```

- 터미널을 열고 kospi-prediction/4-model-management/src 폴더로 이동한 후에 다음 명령어를 실행합니다.
```console
docker compose up -d --build mlflow
```

- minio 콘솔(http://localhost:19001)에 접근해서 ```mlflow```라는 이름으로 저장 공간을 만듭니다.
   - ID: minio_user
   - PW: minio_password


## 실험 추적 및 모델 관리

- model/Dockerfile에서 다음 내용을 삭제합니다.
```Dockerfile
# 모델 피클 생성
RUN python training.py
```

- model/requirements.txt에 다음 내용을 추가합니다.
```
mlflow==2.17.2
```

- model/training.py을 수정합니다.
```python
import os

...

if __name__ == "__main__":
    name="kospi-prediction"

    mlflow.autolog()
    with mlflow.start_run() as run:
        model = train_model()

    mv = mlflow.register_model(
        model_uri=f"runs:/{run.info.run_id}/model",
        name=name
    )

    client = mlflow.MlflowClient()
    client.set_registered_model_alias(name, os.getenv("MLFLOW_MODEL_ALIAS"), mv.version)
```

- model/model.py를 수정합니다.
```python
import os
import mlflow

...

    def load(self) -> bool:
        self.model = mlflow.sklearn.load_model(os.getenv("MLFLOW_MODEL_URI"))
        self.df = get_kospi_data(60)
        self.df["prediction"] = self.df["Label"]
```


## 워크플로우를 이용해 모델 학습

- .github/workflow 폴더에 train-model.yml를 만듭니다.
```yaml
name: KOSPI 지수 예측 모델 학습

on:
  push:
    branches:
      - model-management
    paths:
      - ".github/workflows/train-model.yml"
      - "kospi-prediction/4-model-management/model/**"
  workflow_dispatch:

env:
  NAMESPACE: kospi-prediction
  STAGE: 4-model-management

jobs:
  train_and_deploy:
    runs-on: self-hosted # Self hosted Runner에서 실행

    steps:
      - name: 저장소 받아오기
        uses: actions/checkout@v4

      - name: 모델 학습 및 저장
        working-directory: ./${{ env.NAMESPACE }}/${{ env.STAGE }}/src
        run: docker compose run --build model python training.py

      - name: 컨테이너 실행
        working-directory: ./${{ env.NAMESPACE }}/${{ env.STAGE }}/src
        run: docker compose up -d --build --remove-orphans
```

commit & push 하여 동작을 확인합니다.

- MLflow (http://localhost:15000)
- minio (http://localhost:19001)
- app (http://localhost)