# Docker 기초

터미널을 열고, 실습 저장소 폴더에서 진행합니다.
```
cd /path/to/your-labs-folder
```

## 기본 명령어

```console
docker info    # Docker 데몬의 상태 확인
docker images  # 로컬에 저장된 이미지 목록 확인
docker ps      # 현재 실행 중인 컨테이너 확인
docker ps -a   # 종료된 컨테이너 포함 모든 컨테이너 확인
```


## 이미지, 컨테이너 실습

### Dockerfile 작성

Dockerfile을 새로 만듭니다.

```Dockerfile
FROM python:3.12-slim

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["flask", "--app", "hello", "run", "--host=0.0.0.0"]
```


### 이미지 빌드
```console
docker build -t hello_server .
```

### 컨테이너 시작
```console
docker run -p 15000:5000 hello_server
```
http://localhost:15000 접속해서 내용을 확인합니다.

### 소스 코드 갱신
main.py를 수정합니다.
```diff
    - return "<p>Hello, DevOps!</p>"
    + return "<p>Hello, DevOps to MLOps!</p>"
```
http://localhost:15000 접속해서 내용을 확인합니다.

### 이미지 재빌드 및 컨테이너 실행
터미널을 하나 더 열어서 실습 저장소 폴더로 이동한 후, 다음 명령어를 실행합니다.
```console
docker build -t hello_server .
docker run -p 15000:5000 hello_server
```

오류 발생
```
docker: Error response from daemon: ...
```

### 기존 컨테이너 제거 및 새 컨테이너 실행
```console
docker ps
docker stop <container-id>
docker ps
docker ps -a
docker rm <container-id>
docker run --rm --name app -p 15000:5000 -d hello_server
```
http://localhost:15000 접속해서 변경한 내용을 확인합니다.


## 볼륨, 네트워크 실습

### 네트워크 생성
```console
docker network create hello-net
```

### 앱 컨테이너 재실행
생성한 네트워크에 연동하여 재실행합니다.
```console
docker stop app
docker run --rm --name app --network hello-net -p 15000:5000 -d hello_server
```

### 데이터베이스 컨테이너 실행
```console
docker run --rm --name db --network hello-net -e POSTGRES_PASSWORD=mysecretpassword -d postgres
```

### 방문 횟수 확인 실험
1. http://localhost:15000/visit 접속 후, 새로고침을 여러번 해 봅니다.
1. 창을 닫았다가 다시 접속해 봅니다.
1. 데이터베이스 컨테이너를 재실행합니다.
```console
docker stop db
docker run --rm --name db --network hello-net -e POSTGRES_PASSWORD=mysecretpassword -d postgres
```
1. 웹페이지에 다시 접속해 봅니다.

### 데이터베이스에 볼륨 추가
```console
docker volume create db-data
docker stop db
docker run --rm --name db --network hello-net -v db-data:/var/lib/postgresql/data -e POSTGRES_PASSWORD=mysecretpassword -d postgres
```
위의 방문 횟수 확인 실험을 다시 해봅니다.


> [!TIP]
> 로컬 컴퓨터에 실행중인 웹사이트를 외부에서 접속할 수 있게 만들어 주는 도구
> Cloudflare Tunnel (https://developers.cloudflare.com/pages/how-to/preview-with-cloudflare-tunnel/)
```console
docker run --rm cloudflare/cloudflared:latest tunnel --no-autoupdate --url http://host.docker.internal:15000
```


## 레지스트리 실습

### Docker Hub에 저장소 생성

1. [Docker Hub](https://hub.docker.com/)에 가입/로그인
1. Create Repository를 이용해서 원하는 이름으로 저장소 생성(예: hello)

### 이미지 배포

```console
docker login -u <DOCKER-HUB-USER-ID>
docker tag hello_server <DOCKER-HUB-USER-ID>/hello
docker push <DOCKER-HUB-USER-ID>/hello
```
[Play with Docker](https://labs.play-with-docker.com)에서 실행해 봅니다.
ADD NEW INSTANCE를 한 후에 다음 명령어를 웹 터미널에서 실행합니다.
```console
docker run --rm --name app -p 15000:5000 <DOCKER-HUB-USER-ID>/hello
```

## 뒷정리

```console
docker stop app
docker stop db
docker volume rm db-data
docker network rm hello-net
```