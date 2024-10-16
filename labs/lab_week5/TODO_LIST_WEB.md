# REST API를 활용한 TODO List 웹페이지 제작


## 사전 작업

- Docker Desktop 실행
- Self Hosted Runner 프로그램 실행


## TODO List 웹사이트 살펴보기

### 구조 설명
| 폴더 | 설명 |
| -- | -- |
| todo-list/frontend | React로 만들어진 Client Side 코드 |
| todo-list/backend | Flask로 만들어진 Server Side 코드 (REST API 구현) |
| todo-list/terraform | Terraform을 이용한 인프라 생성 및 배포 정의 |

### 아키텍쳐
- 쿠버네티스 클러스터에서 동작합니다. (클러스트명: terraform-managed-cluster)
- todo-list라는 네임스페이스로 묶여 있습니다.
- React 코드를 빌드한 후 생기는 HTML, CSS, JS 파일 등은 nginx로 동작하는 컨테이너 안에 들어갑니다.
- nginx 컨테이너는 NodePort 형식의 쿠버네티스 Service로 노출됩니다.
- Flask 코드는 별도의 컨테이너로 배포됩니다.
- nginx는 Flask 컨테이너로의 네트워크 접속을 중개하는 Reverse Proxy 역할도 합니다.
- PostgreSQL도 별도의 컨테이너로 배포됩니다.
- Client Side Rendering 방식입니다.

### 자동 배포를 위한 workflow 파일 생성
.github/workflows/deploy-todo-list.yml을 생성합니다.
```yml
name: 할일 관리 웹사이트 배포

on:
  push:
    branches:
      - main
    paths:
      - "todo-list/**"

env:
  REGISTRY: ghcr.io
  CLUSTER_NAME: terraform-managed-cluster
  NAMESPACE: todo-list

jobs:
  build:
    # runs-on: ubuntu-latest # GitHub hosted Runner에서 실행
    runs-on: self-hosted # Self hosted Runner에서 실행
    strategy:
      matrix:
        layer: [frontend, backend]

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
          context: ./${{ env.NAMESPACE }}/${{ matrix.layer }}
          push: true
          tags: ${{ env.REGISTRY }}/${{ github.repository }}-${{ env.NAMESPACE }}-${{ matrix.layer }}:latest

  deploy:
    needs: build
    runs-on: self-hosted # Self hosted Runner에서 실행

    steps:
      - name: 저장소 받아오기
        uses: actions/checkout@v4

      # setup-terraform을 self hosted runner에서 실행할 때 필요
      - name: nodejs 설치
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Terraform 설치
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_wrapper: false

      # terraform과 minikube 연동 시 발생할 수 있는 오류를 방지하기 위한 임시 조치
      - name: minikube cluster 삭제
        run: minikube delete -p ${{ env.CLUSTER_NAME }}

      - name: Terraform Init
        id: init
        working-directory: ./${{ env.NAMESPACE }}/terraform # terraform 폴더 아래 tf 읽어드리기 위해 경로 지정
        run: terraform init

      - name: Terraform Apply
        working-directory: ./${{ env.NAMESPACE }}/terraform # terraform 폴더 아래 tf 읽어드리기 위해 경로 지정
        env: # TF_VAR_로 시작하는 환경 변수를 만들면 tf 파일 내부에서 variable로 값을 이용할 수 있음
          TF_VAR_github_username: ${{ github.actor }}
          TF_VAR_github_token: ${{ secrets.GITHUB_TOKEN }}
          TF_VAR_ghcr_frontend_image: ${{ env.REGISTRY }}/${{ github.repository }}-${{ env.NAMESPACE }}-frontend:latest
          TF_VAR_ghcr_backend_image: ${{ env.REGISTRY }}/${{ github.repository }}-${{ env.NAMESPACE }}-backend:latest
          TF_VAR_cluster_name: ${{ env.CLUSTER_NAME }}
          TF_VAR_namespace: ${{ env.NAMESPACE }}
        run: |
          terraform apply -auto-approve
```

### 배포 후 웹사이트 접속
추가한 workflow 파일을 github에 push한 후, 자동 배포가 완료되면 다음 명령어를 통해 웹사이트에 접속해 봅니다.
```console
minikube service todo-list-service -n todo-list -p terraform-managed-cluster
```


## TODO 삭제 기능 구현하기

todo-list/backend/app.py 내부에 있는
삭제 REST API의 기능을 구현해 봅니다.

### 수정할 부분
```python
def delete_todo(todo_id):
    ...

    # TODO 삭제
    return jsonify({"message": "Not Implemented"}), 501
```
