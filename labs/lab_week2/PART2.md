# Docker 기본기

## 기본 명령어

```bash
docker info    # Docker 데몬의 상태 확인
docker images  # 로컬에 저장된 이미지 목록 확인
docker ps      # 현재 실행 중인 컨테이너 확인
docker ps -a   # 종료된 컨테이너 포함 모든 컨테이너 확인
```


## 저장소 최신 버전 받아오기 

2주차 실습 진행을 위해 이 저장소를 clone하거나 pull해서 로컬 컴퓨터에 최신 복사본이 있도록 만듭니다. 로컬에 다음 폴더가 존재해야 합니다.

- labs/lab_week2/hello_server


## Dockerfile 작성

hello_server 폴더 밑에 Dockerfile을 새로 만듭니다.

```Dockerfile
FROM python:3.12-slim

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["flask", "--app", "main", "run", "--host=0.0.0.0"]
```


## 이미지 빌드
```bash
$ cd /path/to/hello_server
$ docker build -t hello .
```

## 컨테이너 시작
```bash
$ docker run -p 5000:5000 hello_server
```
http://localhost:5000 접속해서 내용을 확인합니다.

## 소스 코드 갱신
main.py를 수정합니다.
```diff
    - return "<p>Hello, Docker!</p>"
    + return "<p>Hello, DevOps!</p>"
```

## 이미지 재빌드 및 컨테이너 실행
```bash
$ docker build -t hello .
$ docker run -p 5000:5000 hello_server
```

## 기존 컨테이너 제거 및 새 컨테이너 실행
```sh
$ docker ps
$ docker stop <container-id>
$ docker rm <container-id>
$ docker run -dp 5000:5000 hello_server
```
http://localhost:5000 접속해서 변경한 내용을 확인합니다.