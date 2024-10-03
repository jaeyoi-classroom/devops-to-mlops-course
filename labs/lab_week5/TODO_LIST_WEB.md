# REST API를 활용한 TODO List 웹페이지 제작


## 사전 작업

- Docker Desktop 실행
- Self Hosted Runner 프로그램 실행


## TODO List 웹사이트 살펴보기

### 배포 후 웹사이트 접속
```console
minikube service todo-list-service -n todo-list -p terraform-managed-cluster
```

### 구조 설명
| 폴더 | 설명 |
| -- | -- |
| frontend | React로 만들어진 Client Side 코드 |
| backend | Flask로 만들어진 Server Side 코드 (REST API 구현) |
| terraform | Terraform을 이용한 인프라 생성 및 배포 정의 |

### 아키텍쳐
- 쿠버네티스 클러스터에서 동작합니다. (클러스트명: terraform-managed-cluster)
- todo-list라는 네임스페이스로 묶여 있습니다.
- React 코드를 빌드한 후 생기는 HTML, CSS, JS 파일 등은 nginx로 동작하는 컨테이너 안에 들어갑니다.
- nginx 컨테이너는 NodePort 형식의 쿠버네티스 Service로 노출됩니다.
- Flask 코드는 별도의 컨테이너로 배포됩니다.
- nginx는 Flask 컨테이너로의 네트워크 접속을 중개하는 Reverse Proxy 역할도 합니다.
- PostgreSQL도 별도의 컨테이너로 배포됩니다.
- Client Side Rendering 방식입니다.


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
