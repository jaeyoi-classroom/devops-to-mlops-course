# Terraform을 이용한 인프라 관리 자동화

IaC의 효과를 제대로 맛보기 위해서는 클라우드 환경에서 진행하는 것이 좋습니다. 
이 실습에서는 로컬 환경이라는 제약 사항을 감안하고 진행하기 바랍니다.

> [!NOTE]
> 3주차에 GitHub 실습 저장소 - Settings 화면에 추가했던 
> Secrets나 Variables 값이 이번 실습에서는 쓰이지 않습니다. 
> 지난 주와 이번 주의 차이를 비교해가며 학습해 보시면 좋습니다.


## 사전 작업

- Docker Desktop을 실행해 둡니다.
- Windows 환경이라면 PowerShell을 열고 다음 명령어를 실행합니다.
```console
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```


## GitHub Self hosted Runner 추가

1. Github에 본인의 실습 저장소 > Settings > Actions > Runners 화면으로 이동합니다.
1. 'New self-hosted runner' 버튼을 누릅니다.
1. 운영 체제에 따라 사이트에 나오는 설치 및 실행 방법을 보고 따라 합니다.
1. 설치 과정에서 나오는 질문들은 그냥 엔터쳐서 지나가면 됩니다. (기본값으로 설정함)
1. 실행 후에, Runners 화면에서 본인의 컴퓨터가 Idle 상태로 표시되는지 확인합니다.

![Runners](https://media.licdn.com/dms/image/v2/D4D12AQHSfAKrfK_ujg/article-inline_image-shrink_1000_1488/article-inline_image-shrink_1000_1488/0/1670186830641?e=1731542400&v=beta&t=UFT5L-LdlBIqibLqGNnV968h0UpgL2uqstsxiTzpKXc)


## GitHub Actions Workflow 수정

- 3주차 실습 때 만든 .github/workflows/deploy-to-k8s.yml을 아래 내용으로 수정합니다.
```yaml
name: IaC 실습

on:
  push:
    branches:
      - main

env:
  REGISTRY: ghcr.io
  CLUSTER_NAME: terraform-managed-cluster

jobs:
  build:
    runs-on: ubuntu-latest  # GitHub hosted Runner에서 실행

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
          tags: ${{ env.REGISTRY }}/${{ github.repository }}:latest

  deploy:
    needs: build
    runs-on: self-hosted  # Self hosted Runner에서 실행

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
        working-directory: ./terraform # terraform 폴더 아래 tf 읽어드리기 위해 경로 지정
        run: terraform init

      - name: Terraform Apply
        working-directory: ./terraform # terraform 폴더 아래 tf 읽어드리기 위해 경로 지정
        env: # TF_VAR_로 시작하는 환경 변수를 만들면 tf 파일 내부에서 variable로 값을 이용할 수 있음
          TF_VAR_github_username: ${{ github.actor }}
          TF_VAR_github_token: ${{ secrets.GITHUB_TOKEN }}
          TF_VAR_ghcr_image: ${{ env.REGISTRY }}/${{ github.repository }}:latest
          TF_VAR_cluster_name: ${{ env.CLUSTER_NAME }}
        run: |
          terraform apply -auto-approve
```
build Job 내용은 3주차 실습때와 동일합니다.

deploy Job에서 `terraform init`, `terraform apply` 명령어가 핵심입니다.
- init은 테라폼 프로젝트의 초기화 작업을 진행합니다.
- apply는 tf 파일에 정의된 내용을 바탕으로 실제 인프라를 생성, 수정, 삭제합니다.


## Terraform 구성 파일 생성
terraform 폴더를 생성한 후, 테라폼 구성 파일을 만드는 작업입니다.

- terraform/variables.tf (main.tf에서 쓸 변수를 정의합니다.)
```terraform
# GitHub Actions workflow에서 TF_VAR_github_username으로 환경 변수 설정
variable "github_username" {
  type = string
}

# GitHub Actions workflow에서 TF_VAR_github_token으로 환경 변수 설정
variable "github_token" {
  type      = string
  sensitive = true
}

# GitHub Actions workflow에서 TF_VAR_ghcr_image로 환경 변수 설정
variable "ghcr_image" {
  type = string
}

# GitHub Actions workflow에서 TF_VAR_cluster_name으로 환경 변수 설정
variable "cluster_name" {
  type = string
}

# namespace 이름: hello-kube
variable "namespace" {
  type        = string
  description = "Kubernetes namespace"
  default     = "hello-kube"
}
```

- terraform/main.tf
```terraform
terraform {
  # terraform으로 minikube를 관리하기 위한 provider
  required_providers {
    minikube = {
      source  = "scott-the-programmer/minikube"
    }
  }
}

provider "minikube" {
  kubernetes_version = "v1.30.0"
}

# minikube cluster를 docker 기반으로 생성
resource "minikube_cluster" "docker" {
  driver       = "docker"
  cluster_name = var.cluster_name
  addons = [
    "default-storageclass",
    "storage-provisioner",
    "dashboard"
  ]
}

provider "kubernetes" {
  host = minikube_cluster.docker.host

  client_certificate     = minikube_cluster.docker.client_certificate
  client_key             = minikube_cluster.docker.client_key
  cluster_ca_certificate = minikube_cluster.docker.cluster_ca_certificate
}

# Namespace 정의
resource "kubernetes_namespace" "namespace" {
  metadata {
    name = var.namespace
  }
}

# GitHub Container Registry에 접근하기 위한 시크릿 정보 
resource "kubernetes_secret" "ghcr_secret" {
  metadata {
    name      = "ghcr"
    namespace = var.namespace
  }

  data = {
    ".dockerconfigjson" = jsonencode({
      "auths" = {
        "ghcr.io" = {
          "username" = var.github_username
          "password" = var.github_token
          "auth"     = base64encode("${var.github_username}:${var.github_token}")
        }
      }
    })
  }

  type = "kubernetes.io/dockerconfigjson"

  depends_on = [ 
    kubernetes_namespace.namespace
  ]
}

# hello api server 배포 정보
resource "kubernetes_deployment" "api" {
  metadata {
    name      = "api-deployment"
    namespace = var.namespace
    labels = {
      app = "api"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "api"
      }
    }

    template {
      metadata {
        labels = {
          app = "api"
        }
      }

      spec {
        container {
          image             = var.ghcr_image
          name              = "labs-image"
          image_pull_policy = "Always"

          port {
            container_port = 5000
          }
        }

        image_pull_secrets {
          name = "ghcr"
        }
      }
    }
  }

  depends_on = [
    kubernetes_namespace.namespace,
    kubernetes_secret.ghcr_secret,
    kubernetes_service.db,
  ]
}

# hello api server 서비스 정보
resource "kubernetes_service" "api" {
  metadata {
    name      = "api-service"
    namespace = var.namespace
  }

  spec {
    type = "NodePort"

    selector = {
      app = "api"
    }

    port {
      port        = 5000
      target_port = 5000
      node_port   = 30000
    }
  }

  depends_on = [
    kubernetes_namespace.namespace,
    kubernetes_deployment.api,
  ]
}

# db server 배포 정보
resource "kubernetes_deployment" "db" {
  metadata {
    name      = "db-deployment"
    namespace = var.namespace
    labels = {
      app = "postgres"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "postgres"
      }
    }

    template {
      metadata {
        labels = {
          app = "postgres"
        }
      }

      spec {
        container {
          name  = "postgres"
          image = "postgres:16"

          port {
            container_port = 5432
          }

          env {
            name  = "POSTGRES_PASSWORD"
            value = "mysecretpassword"
          }

          volume_mount {
            name       = "db-data"
            mount_path = "/var/lib/postgresql/data"
          }
        }

        volume {
          name = "db-data"

          persistent_volume_claim {
            claim_name = "db-data-pvc"
          }
        }
      }
    }
  }

  depends_on = [
    kubernetes_namespace.namespace,
    kubernetes_persistent_volume_claim.db_data
  ]
}

# db server 서비스 정보
resource "kubernetes_service" "db" {
  metadata {
    name      = "db"
    namespace = var.namespace
  }

  spec {
    type = "ClusterIP"

    selector = {
      app = "postgres"
    }

    port {
      port        = 5432
      target_port = 5432
    }
  }

  depends_on = [
    kubernetes_namespace.namespace,
    kubernetes_deployment.db,
  ]
}

# db server에서 사용할 볼륨 정보
resource "kubernetes_persistent_volume_claim" "db_data" {
  metadata {
    name      = "db-data-pvc"
    namespace = var.namespace
  }

  spec {
    access_modes = ["ReadWriteOnce"]

    resources {
      requests = {
        storage = "1Gi"
      }
    }
  }

  depends_on = [
    kubernetes_namespace.namespace,
  ]
}
```
3주차 수업에서는 쿠버네티스 내부에 생성할 자원(Deployment, Service 등)을 쿠버네티스 manifest 파일로 작성했습니다.

테라폼에서 쿠버네티스 매니페스트를 대신하여 자원을 관리할 수 있는 방법을 제공하기 때문에
테라폼 구성 파일에 모든 필요 자원(Resource)을 정의했습니다.

이렇게 하면서, GitHub Workflow에서도 kubectl 대신에 terraform 명령어만으로 배포가 가능해집니다.

테라폼은 클러스터 생성도 해주기 때문에, 자동으로 관리할 수 있는 범위가 kubectl 명령어를 쓸 때보다 넓습니다.


## GitHub에 변경 내용 Push

- 변경 사항을 모두 원격 저장소에 보내, GitHub Actions가 실행되도록 합니다.
```console
git add .
git commit -m '4주차 IaC 실습'
git push origin main
```

## 서비스 동작 확인

- Actions가 완료되고 나면, 터미널에서 다음 명령어를 실행해 서비스 동작을 확인합니다.
```console
minikube service api-service -p terraform-managed-cluster -n hello-kube
```