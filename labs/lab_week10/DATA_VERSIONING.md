# DVC를 이용한 데이터 버전 관리

- DVC 사이트: https://dvc.org

## 사전 작업

- Docker Desktop 실행

### 작업 브랜치 생성

- main에서 data-management 라는 이름으로 브랜치를 만듭니다.

### 실습 폴더 준비

- 4-model-management 폴더를 5-data-management 이름으로 복사합니다.


## DVC 설치

- 터미널을 열고, pip를 이용해 DVC를 설치합니다. minio와 연동하기 위해 dvc-s3 확장이 필요합니다.
```console
pip install dvc[s3]
```


## DVC 프로젝트 초기화

DVC 프로젝트는 기본적으로 git 저장소 내에서 사용하도록 되어 있습니다.
- 초기화를 하고 나면, .dvc 폴더가 생깁니다. 해당 폴더를 commit합니다.

### 최상위 폴더에서 초기화 할 경우
```console
dvc init
```

### 하위 폴더에서 초기화 할 경우
```console
cd kospi-prediction/5-data-management/src
dvc init --subdir
```

아래의 모든 터미널 명령어는 kospi-prediction/5-data-management/src 아래에서 실행하세요.


## 데이터 추적
- src/data 폴더를 만듭니다.
- src/model/data.py를 src/data 폴더로 옮깁니다.
- data.py에 다음 내용을 추가합니다.
```python
if __name__ == "__main__":
    df = get_kospi_data(3 * 365)
    df.to_csv(Path(__file__).parent / "kospi.csv")
```
- data.py를 실행합니다.
- 저장한 데이터셋을 DVC가 추적하도록 추가합니다.
```console
dvc add data/kospi.csv
```
- DVC는 추가된 파일에 대한 정보를 담은 .dvc 파일( data/kospi.csv.dvc)을 생성합니다.
이 파일은 크기가 작고 사람이 읽을 수 있는 형태의 메타데이터 파일로, 원본 데이터 대신 Git에서 추적할 수 있는 역할을 합니다.

- git에 commit합니다.
```console
git add data/kospi.csv.dvc data/.gitignore
git commit -m "KOSPI 지수 데이터 추가"
```

## 데이터 저장

### 로컬 저장소 경로 설정
```console
mkdir .../dvcstore
dvc remote add -d localstore .../dvcstore
```

### 원격 저장소 경로 설정
- minio 컨테이너를 실행해 둡니다.
```console
docker compose up -d minio
```

- 접속 정보 및 경로를 설정합니다.
```console
dvc remote add -d minio s3://bucket/dvcstore
```

### 데이터 보내기
```console
dvc push
```

### 데이터 받기
```console
dvc pull
```


## 데이터 변경 실험
- src/data/data.py를 수정합니다.
```python
if __name__ == "__main__":
    df = get_kospi_data(2 * 365)
    ...
```
- data.py를 실행합니다.
- DVC에 최신 데이터셋을 추가합니다.
```console
dvc add data/kospi.csv
dvc push
git commit data/kospi.csv.dvc -m "KOSPI 지수 데이터 갱신'
```

### 버전 바꿔보기
```console
git checkout <...>
dvc checkout
```

## 마무리

실습 결과물은 main에 병합합니다.