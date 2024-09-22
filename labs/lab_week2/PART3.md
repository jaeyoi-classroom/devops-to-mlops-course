# Docker Compose

모든 과정은 실습 저장소 폴더에서 진행해 주세요.

## compose.yml 생성

```YAML
name: hello-compose

services:
  app:
    build: .
    ports:
      - 15000:5000

  db:
    image: postgres:16
    volumes:
      - db-data:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: mysecretpassword

volumes:
  db-data:
```


## Compose 실행, 중지

### 서비스 실행
```sh
docker compose up -d
```

### 실행 중인 컨테이너 확인
```sh
docker compose ps
```

### 서비스 중지
```sh
docker compose down
```