# Internal kubeconfig generator

This simple controller generates a `kubeconfig` and stores it in a `Secret` for each
[`Secret` created in a specific namespace for a specific service account.](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/#manually-create-a-long-lived-api-token-for-a-serviceaccount)

## Warning

**The project is currently under development and is not ready for production use.**

## Motivation

The main motivation for developing this controller is to enable the multi-tenancy feature of Crossplane.

The crossplane kubernetes provider does not support the usage of `ServiceAccount`s resource yet to configure
a `providerConfig`. Then, the only way to configure a `providerConfig` is to use a `Secret` with a `kubeconfig`.

This is where this controller comes in.

## How it works

The controller watches for `Secret's` with a few specific annotations:

- `kubernetes.io/service-account.name`: This is the required annotation to tell the kubernetes controller which `ServiceAccount` belongs to this `Secret`.
- `x.k8spin.cloud/kubeconfig`: This is the trigger annotation to tell the controller to generate a `kubeconfig` for this `Secret`.

The controller will generate a new `Secret` with the same name as the `ServiceAccount` defined in the `kubernetes.io/service-account.name` annotation ending with `-kubeconfig` suffix.

## How to use it

```bash
$ kubectl apply -f https://raw.githubusercontent.com/angelbarrera92/internal-kubeconfig-generator/master/deploy/kubernetes/deploy.yaml
namespace/k8spin-system created
serviceaccount/internal-kubeconfig-generator created
clusterrole.rbac.authorization.k8s.io/internal-kubeconfig-generator created
clusterrolebinding.rbac.authorization.k8s.io/internal-kubeconfig-generator created
deployment.apps/internal-kubeconfig-generator created
$ kubectl wait --for=condition=available --timeout=600s deployment/internal-kubeconfig-generator -n k8spin-system
deployment.apps/internal-kubeconfig-generator condition met
```

### Demo

```bash
$ kubectl apply -f https://raw.githubusercontent.com/angelbarrera92/internal-kubeconfig-generator/master/hack/demo.yaml
clusterrole.rbac.authorization.k8s.io/provider-kubernetes-view created
clusterrolebinding.rbac.authorization.k8s.io/provider-kubernetes-view created
serviceaccount/provider-kubernetes-view created
secret/provider-kubernetes-view created
```

This creates a set of resources:
- A `ServiceAccount` named `provider-kubernetes-view`
  - [The `Secret` named `provider-kubernetes-view` that contains the `token` for the `ServiceAccount`.](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/#manually-create-a-long-lived-api-token-for-a-serviceaccount)
- `ClusterRole` and `ClusterRoleBinding` to allow the `ServiceAccount` to list the `Namespaces`.

Then, as the `secret` named `provider-kubernetes-view` has the `x.k8spin.cloud/kubeconfig` annotation, the controller will generate a new `Secret` named `provider-kubernetes-view-kubeconfig` with the `kubeconfig` for the `ServiceAccount`.

```bash
$ kubectl get secret/provider-kubernetes-view-kubeconfig -o yaml
apiVersion: v1
data:
  kubeconfig: <REDACTED>
kind: Secret
metadata:
  creationTimestamp: "2023-01-04T15:01:39Z"
  name: provider-kubernetes-view-kubeconfig
  namespace: default
  ownerReferences:
  - apiVersion: v1
    kind: Secret
    name: provider-kubernetes-view
    uid: fe338cb5-ac4e-4c7f-9e5a-6b7c68216145
  resourceVersion: "603"
  uid: 6c853730-ca5c-4e7d-bfdf-912e31b9c4ec
type: Opaque
```

#### Test

Includes a `Job` that uses the generated `kubeconfig` to list the `Namespaces` in the cluster.

```bash
$ kubectl apply -f https://raw.githubusercontent.com/angelbarrera92/internal-kubeconfig-generator/master/hack/demo-test.yaml
job.batch/list-namespaces created
$ kubectl logs -f job/list-namespaces
NAME              STATUS   AGE
default           Active   8m17s
kube-system       Active   8m17s
kube-public       Active   8m17s
kube-node-lease   Active   8m16s
k8spin-system     Active   7m43s
```

## Development

### Prerequisites

- [python3](https://www.python.org/downloads/)
- [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html)
- [docker](https://docs.docker.com/install/)


## License

[MIT](LICENSE)
