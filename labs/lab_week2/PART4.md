# Kubernetes 설치

## Minikube 설치

https://minikube.sigs.k8s.io/docs/start/
Installation 부분 참고


## 클러스터 생성

- node가 2개인 클러스터를 생성합니다.

```
minikube start --nodes 2 -p multinode-demo
```

- node 목록을 확인합니다.

```
kubectl get nodes
```

