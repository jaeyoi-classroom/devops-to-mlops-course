# Terraform을 이용한 인프라 관리 자동화

IaC의 효과를 제대로 맛보기 위해서는 클라우드 환경에서 진행하는 것이 좋습니다. 
이 실습에서는 로컬 환경이라는 제약 사항을 감안하고 진행하기 바랍니다.


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
1. Runners 화면에 본인의 컴퓨터가 Idle 상태로 표시되는지 확인합니다.

![Runners](https://media.licdn.com/dms/image/v2/D4D12AQHSfAKrfK_ujg/article-inline_image-shrink_1000_1488/article-inline_image-shrink_1000_1488/0/1670186830641?e=1731542400&v=beta&t=UFT5L-LdlBIqibLqGNnV968h0UpgL2uqstsxiTzpKXc)


## Terraform 설정 파일 생성

- terraform/main.tf 파일을 만듭니다.
```yaml
```

- terraform/variables.tf 파일을 만듭니다.
```yaml
```

## GitHub Actions Workflow 수정

- 3주차 실습 때 만든 .github/workflows/deploy-to-k8s.yml을 아래 내용으로 수정합니다.
```yaml
```


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
minikube service api-service -p terraform-managed-cluster
```