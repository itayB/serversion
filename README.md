build locally:
```
docker build -t serversion .
```

install with helm:
```
helm install serversion -n my-nc helm/serversion
```

open access for running in localhost:
```
kubectl -n my-nc port-forward service/serversion 8080:80
```

send request:
```
$ curl http://localhost:8080/api/v1/versions | jq
{
  "kube-node-lease": {},
  "my-nc": {
    "serversion": {
      "containers": {
        "serversion": "serversion:latest"
      },
      "version": "0.1.0",
      "appVersion": "1.16.0"
    }
  },
  "kube-public": {},
  "kube-system": {
    "coredns": {
      "containers": {
        "coredns": "k8s.gcr.io/coredns:1.7.0"
      }
    },
    "etcd-docker-desktop": {
      "containers": {
        "etcd": "k8s.gcr.io/etcd:3.4.13-0"
      }
    },
    "kube-apiserver-docker-desktop": {
      "containers": {
        "kube-apiserver": "k8s.gcr.io/kube-apiserver:v1.19.3"
      }
    },
    "kube-controller-manager-docker-desktop": {
      "containers": {
        "kube-controller-manager": "k8s.gcr.io/kube-controller-manager:v1.19.3"
      }
    },
    "kube": {
      "containers": {
        "kube-proxy": "k8s.gcr.io/kube-proxy:v1.19.3"
      }
    },
    "kube-scheduler-docker-desktop": {
      "containers": {
        "kube-scheduler": "k8s.gcr.io/kube-scheduler:v1.19.3"
      }
    },
    "storage-provisioner": {
      "containers": {
        "storage-provisioner": "docker/desktop-storage-provisioner:v1.1"
      }
    },
    "vpnkit-controller": {
      "containers": {
        "vpnkit-controller": "docker/desktop-vpnkit-controller:v1.0"
      }
    }
  },
  "default": {}
}
```