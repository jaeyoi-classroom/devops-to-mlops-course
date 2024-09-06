# Kubernetes 기초

## 앱 배포
```
kubectl create deployment kubernetes-bootcamp --image=gcr.io/google-samples/kubernetes-bootcamp:v1
kubectl get deployments
```

## Pod와 Node 확인
```
kubectl get pods
kubectl describe pods
```


```
kubectl proxy
export POD_NAME="$(kubectl get pods -o go-template --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}')"
echo Name of the Pod: $POD_NAME
curl http://localhost:8001/api/v1/namespaces/default/pods/$POD_NAME:8080/proxy/
```

```
kubectl logs "$POD_NAME"
```

```
kubectl exec -ti $POD_NAME -- bash
exit
```

## 앱 접속 개방

```
kubectl expose deployment/kubernetes-bootcamp --type="NodePort" --port 8080
kubectl get services
kubectl describe services/kubernetes-bootcamp
```

```
kubectl delete service -l app=kubernetes-bootcamp
```

## 스케일링
```
kubectl expose deployment/kubernetes-bootcamp --type="LoadBalancer" --port 8080
```

```
kubectl get rs
kubectl scale deployments/kubernetes-bootcamp --replicas=4
kubectl get deployments
kubectl get pods -o wide
```

- 로드 밸런싱
```
kubectl describe services/kubernetes-bootcamp
export NODE_PORT="$(kubectl get services/kubernetes-bootcamp -o go-template='{{(index .spec.ports 0).nodePort}}')"
echo NODE_PORT=$NODE_PORT
curl http://"$(minikube ip):$NODE_PORT"
```

- Scale Down
```
kubectl scale deployments/kubernetes-bootcamp --replicas=2
kubectl get deployments
kubectl get pods -o wide
```

## 롤링 업데이트

## 클러스터 제거 

```
kubectl delete service hello-node
kubectl delete deployment hello-node
minikube stop
```