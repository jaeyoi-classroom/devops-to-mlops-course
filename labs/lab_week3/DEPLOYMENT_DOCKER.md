# 배포 자동화 - Docker Compose 기반 인프라

## 워크플로우
쿠버네티스 기반 배포 실습 때 만든 워크플로우에서 build 부분은 동일하게 이용할 수 있습니다.

.github/workflows/deploy-docker-compose.yml
```yaml
name: Docker Compose 배포

on:
  push:
    branches:
      - main

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: 저장소 받아오기
        uses: actions/checkout@v4

      - name: Docker Buildx 설치
        uses: docker/setup-buildx-action@v3

      - name: GitHub 컨테이너 레지스트리에 로그인
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: 빌드해서 레지스트리에 전송
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest

    steps: ...
```

deploy 부분은 아래 사이트를 참고해 만들어 보시기 바랍니다.

https://www.docker.com/blog/how-to-deploy-on-remote-docker-hosts-with-docker-compose/

중요한 점은 GitHub Actions Runner에서 배포할 서버로 네트워크 접근이 가능해야 합니다.

그래서, 배포할 서버와 동일 네트워크에 속한 컴퓨터에 self hosted runner를 설치하는 방법을 고려해 볼 수 있습니다.

배포할 서버 내부에 runner를 설치할 수도 있습니다. 이 경우, 위 사이트에 나오는 docker context 설정이 굳이 필요없습니다.
단, runner의 보안 문제 등으로 프로덕션 환경에서 이 방식을 적용한다면 신중해야 합니다.