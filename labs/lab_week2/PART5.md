# Kubernetes 기초


## 클러스터 생성

- node가 2개인 클러스터를 생성합니다.
```
minikube start --nodes 2
```

- node 목록을 확인합니다.
```
kubectl get nodes
```


## 앱 배포
- Docker Hub에 올렸던 이미지로 클러스터에 배포합니다.
```
kubectl create deployment hello-kube --image=<DOCKER-HUB-USER-ID>/hello
kubectl get deployments
```

## Pod와 Node 확인
- Pod 내역을 확인합니다.
```
kubectl get pods
kubectl describe pods
```

- 프록시를 활성화합니다.
```
kubectl proxy
```

- 실행중인 Pod의 이름을 알아냅니다.
```
(macOS, Linux, Git Bash)
export POD_NAME="$(kubectl get pods -o go-template --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}')"
echo Name of the Pod: $POD_NAME

(Other)
kubectl get pods -o go-template --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}'
```

- 프록시를 이용해 앱에 접속해 봅니다.
```
curl http://localhost:8001/api/v1/namespaces/default/pods/$POD_NAME:5000/proxy/
```

- 컨테이너의 로그 내역을 확인합니다.
```
kubectl logs "$POD_NAME"
```

- 컨테이너 내부 셸로 명령어를 실행해 봅니다.
```
kubectl exec -ti $POD_NAME -- bash
ls
cat requirements.txt
...
exit
```

## 앱 접속 개방

- 서비스를 생성해 앱을 외부에서 접속 가능하도록 만듭니다.
```
kubectl expose deployment/hello-kube --type="NodePort" --port 5000
kubectl get services
kubectl describe services/hello-kube
```

- minikube를 Docker Desktop 기반으로 실행할 때는 터널이 필요합니다. 
다음 명령어를 실행하고, 결과로 나오는 주소를 브라우저에서 접속해 봅니다.
```
minikube service hello-kube --url
```
Docker Desktop 기반이 아닐 때는
```
export NODE_PORT="$(kubectl get services/hello-kube -o go-template='{{(index .spec.ports 0).nodePort}}')"
echo NODE_PORT=$NODE_PORT
curl http://"$(minikube ip):$NODE_PORT"
```

- 서비스를 삭제합니다.
```
kubectl delete service -l app=hello-kube
```

## 스케일링
- 서비스를 LoadBalancer 타입으로 생성합니다.
```
kubectl expose deployment/hello-kube --type="LoadBalancer" --port 5000
```

- 스케일링을 해 봅니다.
```
kubectl get rs
kubectl scale deployments/hello-kube --replicas=3
kubectl get deployments
kubectl get pods -o wide
```

- 로드 밸런싱 동작을 확인합니다.
```
kubectl describe services/hello-kube
minikube service hello-kube --url
kubectl logs <POD_NAME> -> Pod별로 확인
```

- Scale Down
```
kubectl scale deployments/hello-kube --replicas=2
kubectl get deployments
kubectl get pods -o wide
```


## 클러스터 제거 

```
kubectl delete service hello-kube
kubectl delete deployment hello-kube
minikube stop
```