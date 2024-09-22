# 배포 자동화 - Kubernetes 기반 인프라

## 인프라 준비

1. 터미널(윈도우는 PowerShell)을 열어 실습 저장소 폴더 위치로 이동합니다.
1. Docker Desktop을 실행합니다.
1. minikube 클러스터를 가동시킵니다.
```console
minikube start --driver=docker
```
- 터미널을 하나 더 열어서 dashboard를 실행해 둡니다.
```console
minikube dashboard
```

## Dockerfile 작성
2주차 실습에서 만들었던 파일과 동일합니다.

1. 실습 저장소 폴더를 편집기(IDE)로 엽니다.
1. 최상위 위치에 Dockerfile를 만듭니다.
```Dockerfile
FROM python:3.12-slim

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["flask", "--app", "hello", "run", "--host=0.0.0.0"]
```


## 워크플로우 작성

1. 실습 저장소에 .github/workflows/ 폴더를 만듭니다.

1. 그 폴더에 deploy-to-k8s.yml과 같은 이름으로 워크플로우 설정 파일을 만듭니다.
```yaml
name: K8S 클러스터에 배포

on:
  push:
    branches:
      - main
    tags:
      - "v*"

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

    steps:
      - name: 저장소 받아오기
        uses: actions/checkout@v4

      - name: kubectl 설치
        uses: azure/setup-kubectl@v4
        id: install

      - name: 원격 클러스터 접속을 위한 설정 파일 생성
        run: |
          mkdir -p $HOME/.kube
          echo "${{ secrets.KUBECONFIG }}" > $HOME/.kube/config

      - name: 배포
        run: kubectl apply -f kubernetes/deployment.yml -n ${{ vars.NAMESPACE }}
```

위의 워크플로우는 두가지 조건에서 실행됩니다.
- main 브랜치에 push가 일어날 때
- v로 시작하는 tag가 생길 때

크게 두 개의 작업(Job)으로 나뉘어 진행됩니다.
1. build
   - Docker Image를 빌드한 후, GitHub Container Registry(ghcr)에 전송
2. deploy
   - build가 성공해야 시작함
   - kubectl를 이용해 내 컴퓨터의 minikube 클러스터에 배포 실행

`${{ ... }}`로 표현된 구문은 GitHub Actions내에서 정의된 여러 종류의 값들을 의미합니다. ([참고](https://docs.github.com/ko/actions/writing-workflows/choosing-what-your-workflow-does/store-information-in-variables))
- 기본으로 Actions에서 생성해주는 값
- env, vars로 정의된 환경 변수
- secrets로 정의된 비밀 변수
- 기타

## 배포 환경 준비

### 매니페스트 모음 폴더 생성
kubernetes라는 이름으로 폴더를 만듭니다.

### 클러스터 네임스페이스 생성
네임스페이스는 쿠버네티스 클러스터 내에서 리소스를 논리적으로 분리하고 조직화하기 위한 가상적인 공간입니다. 이를 통해 여러 사용자나 팀이 동일한 클러스터를 공유하면서도 리소스 충돌을 방지하고, 접근 권한을 세분화할 수 있습니다.

```YAML
apiVersion: v1
kind: Namespace
metadata:
  name: hello-kube
```
위의 내용을 kubernetes/namespace.yml 파일로 저장합니다.

다음 명령어로 네임스페이스를 생성합니다.
```console
kubectl apply -f kubernetes/namespace.yml
```

> [!TIP]
> 위의 선언적 방식 대신에 다음과 같은 명령형 방식을 사용해서 네임스페이스를 생성할 수도 있습니다.
```console
kubectl create namespace hello-kube
```

### GitHub Personal Access Token 생성
이후 과정에 사용할 Personal Access Token을 만듭니다.
1. https://github.com/settings/tokens
1. Generate new token (Classic) 
1. Note에 적당한 이름을 지정
1. Expiration은 앞으로의 강의 일정을 고려해서 길게 설정
1. scope은 read:packages만 선택

생성된 token 값을 복사해 둡니다.

### 클러스터에 컨테이너 레지스트리 접속 정보 저장
Secrets은 민감한 정보를 안전하게 저장하고 관리하기 위한 쿠버네티스 오브젝트입니다. 예를 들어, 비밀번호, OAuth 토큰, SSH 키 등과 같은 민감한 데이터를 저장할 때 사용됩니다.
```console
kubectl create secret docker-registry ghcr --namespace=hello-kube --docker-server=ghcr.io --docker-username=<github-username> --docker-password=<token>
```
- github-username: GitHub 계정 이름
- token: 앞에서 생성한 GitHub Personal Access Token

### manifests 파일 생성
kubernetes/deployment.yml 파일을 생성합니다.
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-deployment
  labels:
    app: hello-kube
spec:
  replicas: 1
  selector:
    matchLabels:
      app: hello-kube
  template:
    metadata:
      labels:
        app: hello-kube
    spec:
      containers:
        - image: ghcr.io/jaeyoi-classroom/labs-jaeyoi:latest
          imagePullPolicy: Always
          name: labs-jaeyoi
          ports:
            - containerPort: 5000
      imagePullSecrets:
        - name: ghcr
---
apiVersion: v1
kind: Service
metadata:
  name: app-service
spec:
  type: NodePort
  selector:
    app: hello-kube
  ports:
    - port: 5000
      targetPort: 5000
      nodePort: 30000
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: db-deployment
  labels:
    app: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:16
          ports:
            - containerPort: 5432
          env:
            - name: POSTGRES_PASSWORD
              value: "mysecretpassword"
          volumeMounts:
            - name: db-data
              mountPath: /var/lib/postgresql/data
      volumes:
        - name: db-data
          persistentVolumeClaim:
            claimName: db-data-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: db
spec:
  type: ClusterIP
  selector:
    app: postgres
  ports:
    - port: 5432
      targetPort: 5432
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: db-data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```
하나의 YAML 파일 안에 필요한 리소스를 모두 포함시켰습니다. 작은 프로젝트에서는 하나의 파일에 정의해서 쓰는 것이 편리합니다. 하지만 필요한 리소스가 많아지고, 프로젝트가 커질 수록 매니페스트 파일을 분리하거나 helm 차트와 템플릿 도구를 사용하는 것이 좋습니다.

### 외부에서 클러스터 API 서버 접근할 수 있게 터널 생성
워크플로우의 마지막에 보면 kubectl 명령어가 보입니다. 실습을 진행하는 동안 github에서 제공하는 runner를 사용하기 때문에, 해당 runner에서 내 컴퓨터의 쿠버네티스 API 서버에 접근할 수 있게 해줘야 합니다.

이를 위해, 임의로 터널을 생성하는 방식으로 실습을 진행합니다.

**프로덕션 환경에서는 이와 같은 형태로 진행하는 것을 _권장하지 않습니다_.**

클라우드 플랫폼의 경우, 자체적인 보안 체계에 맞춰 진행할 수 있는 방법을 제공합니다.
온프레미스로 구축할 때는 GitOps 등의 대안을 고려하는 것이 낫습니다.

kubernetes/api-tunnel.yml을 만듭니다.
```YAML
apiVersion: v1
kind: ServiceAccount
metadata:
  name: api-tunnel-admin
  namespace: hello-kube
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: hello-kube-api-tunnel-admin
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
  - kind: ServiceAccount
    name: api-tunnel-admin
    namespace: hello-kube
---
apiVersion: v1
kind: Secret
metadata:
  name: api-tunnel-admin-token
  namespace: hello-kube
  annotations:
    kubernetes.io/service-account.name: api-tunnel-admin
type: kubernetes.io/service-account-token
---
apiVersion: v1
kind: Pod
metadata:
  name: api-tunnel
  namespace: hello-kube
spec:
  serviceAccountName: api-tunnel-admin
  automountServiceAccountToken: false
  containers:
    - name: api-tunnel
      image: cloudflare/cloudflared:latest
      args:
        - tunnel
        - --no-autoupdate
        - --no-tls-verify
        - --url
        - https://kubernetes.default.svc
``` 
```console
kubectl apply -f kubernetes/api-tunnel.yml
```
- 클러스터 내에서 cloudflare tunnel Pod를 만듭니다.
- 그 터널을 통해 쿠버네티스 API에 접근할 수 있게 합니다.
- 클러스터 관리자 권한을 가진 서비스 어카운트도 만듭니다.
- 터널 Pod에 서비스 어카운트를 연결합니다.


### API 서버 접근 정보를 저장소 설정에 추가
```YAML
apiVersion: v1
clusters:
- cluster:
    server: <Cloudflared Tunnel 주소>
  name: minikube
contexts:
- context:
    cluster: minikube
    user: minikube
  name: minikube
current-context: minikube
kind: Config
preferences: {}
users:
- name: minikube
  user:
    token: <Service Account Token>
```
위의 내용을 빈 파일에 붙여넣기 합니다.
미리 띄워 둔 dashboard를 이용해 아래 값들을 확인하여 수정합니다.
- server
   1. 상단에서 hello-kube 네임스페이스 선택
   1. 왼쪽 메뉴에서 파드(Pod) 선택
   1. api-tunnel Pod의 로그 확인 메뉴 선택
   1. 로그에서 Cloudflare Tunnel 주소 값 복사하여 매니페스트 내용에 붙여넣기
- token
   1. 왼쪽 메뉴에서 시크릿(Secrets) 선택
   1. api-tunnel-admin-token 선택
   1. 데이터 > token 옆이 보기 아이콘 클릭
   1. 값 복사하여 매니페스트 내용에 붙여넣기

수정한 내용을 다시 클립보드에 복사합니다.

브라우저에서 내 실습 Github 저장소로 접속합니다. 다음 경로의 화면으로 들어갑니다.

Repository > Settings > Security > Secrets and variables > Actions

- Secrets 탭 > New repository secret
   - Name: KUBECONFIG
   - Secret: 클립보드 내용 붙여넣기
   - Add 클릭!
- Variables 탭 > New repository variable
   - Name: NAMESPACE
   - Value: hello-kube
   - Add 클릭!


## 자동 배포 실행

### 변경 내역을 원격 저장소로 보내기
위의 과정을 거쳐 만든 파일을 commit하고, github에 push합니다.
```console
git add .
git commit -m '3주차 실습'
git push origin main
```

### Actions 실행 모니터링
github 저장소 화면에서 Actions 메뉴로 이동합니다.
워크플로우가 잘 실행중인지 확인합니다.


### 대시보드 확인
minikube 대시보드에서 배포가 잘 이뤄지고 있는지 확인합니다.

### 서비스 접속 테스트
```console
minikube service app-service -n hello-kube
```


## 뒷정리
```console
kubectl delete namespace hello-kube
minikube stop
```