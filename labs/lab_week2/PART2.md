# Docker 기초

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


## 이미지, 컨테이너 실습

### Dockerfile 작성

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


### 이미지 빌드
```bash
$ cd /path/to/hello_server
$ docker build -t hello .
```

### 컨테이너 시작
```bash
$ docker run -p 5000:5000 hello_server
```
http://localhost:5000 접속해서 내용을 확인합니다.

### 소스 코드 갱신
main.py를 수정합니다.
```diff
    - return "<p>Hello, Docker!</p>"
    + return "<p>Hello, DevOps!</p>"
```

### 이미지 재빌드 및 컨테이너 실행
```bash
$ docker build -t hello .
$ docker run -p 5000:5000 hello_server
```

### 기존 컨테이너 제거 및 새 컨테이너 실행
```sh
$ docker ps
$ docker stop <container-id>
$ docker rm <container-id>
$ docker run -dp 5000:5000 hello_server
```
http://localhost:5000 접속해서 변경한 내용을 확인합니다.

## 볼륨, 네트워크 실습

### 네트워크 생성
```sh
$ docker network create hello-net
```

### 앱 컨테이너 재실행
생성한 네트워크에 연동하여 재실행합니다.
```sh
$ docker ps
$ docker stop <app-container-id>
$ docker rm <app-container-id>
$ docker run --name app --network hello-net -p 5000:5000 -d hello_server
```

### 데이터베이스 컨테이너 실행
```sh
$ docker run --rm --name db --network hello-net -e POSTGRES_PASSWORD=mysecretpassword -d postgres
```

### 방문 횟수 확인 실험
1. http://localhost:5000/visit 접속 후, 새로고침을 여러번 해 봅니다.
1. 창을 닫았다가 다시 접속해 봅니다.
1. 데이터베이스 컨테이너를 재실행합니다.
1. 웹페이지에 다시 접속해 봅니다.

### 데이터베이스에 볼륨 추가
```sh
$ docker volume create db-data
$ docker stop db
$ docker run --rm --name db --network hello-net -v db-data:/var/lib/postgresql/data -e POSTGRES_PASSWORD=mysecretpassword -d postgres
```
위의 방문 횟수 확인 실험을 다시 해봅니다.

> [!TIP]
> 로컬 컴퓨터에 실행중인 웹사이트를 외부에서 접속할 수 있게 만들어 주는 도구
> Cloudflare Tunnel (https://developers.cloudflare.com/pages/how-to/preview-with-cloudflare-tunnel/)

## 레지스트리 실습

### Docker Hub에 저장소 생성

1. [Docker Hub](https://hub.docker.com/)에 가입/로그인
1. Create Repository를 이용해서 원하는 이름으로 저장소 생성(예: hello)

### 이미지 배포

```sh
$ docker login -u <DOCKER-HUB-USER-ID>
$ docker tag hello_server <DOCKER-HUB-USER-ID>/hello
$ docker push <DOCKER-HUB-USER-ID>/hello
```
[Play with Docker](https://labs.play-with-docker.com)에서 실행해 봅니다.



## (선택 사항) 추가 실습


### 내 컴퓨터에 JupyterLab 환경 구축

https://docs.docker.com/guides/use-case/jupyter/


### 개발 환경에 컨테이너 이용하기

https://docs.docker.com/get-started/workshop/06_bind_mounts/#development-containers

- VSCode Dev Containers: https://code.visualstudio.com/docs/devcontainers/containers