from base64 import b64decode, b64encode

import kopf
from kubernetes import client, config

KUBERNETES_SERVICE = "https://kubernetes.default.svc.cluster.local"


@kopf.on.create(
    "secrets",
    annotations={
        "kubernetes.io/service-account.name": kopf.PRESENT,
        "x.k8spin.cloud/kubeconfig": kopf.PRESENT,
    },
)
def secrets(body, logger, **_):
    logger.debug(f"Processing secret {body['metadata']['name']}")
    # Get the ca.crt from the secret
    b64CA = body["data"]["ca.crt"]
    # Get the token from the secret
    b64Token = body["data"]["token"]
    token = b64decode(b64Token).decode("utf-8")
    # Get the service account name
    name = body["metadata"]["annotations"]["kubernetes.io/service-account.name"]
    # Get the namespace
    namespace = body["metadata"]["namespace"]
    # Create the kubeconfig
    kubeconfig = f"""apiVersion: v1
kind: Config
clusters:
- cluster:
    certificate-authority-data: {b64CA}
    server: {KUBERNETES_SERVICE}
  name: in-cluster
contexts:
- context:
    cluster: in-cluster
    user: {name}
  name: in-cluster
current-context: in-cluster
users:
- name: {name}
  user:
    token: {token}
preferences: {{}}
"""
    logger.info(f"Created kubeconfig for {name}")
    # Create the secret object
    kubeconfigSecret = client.V1Secret()
    kubeconfigSecret.metadata = client.V1ObjectMeta(name=f"{name}-kubeconfig")
    kubeconfigSecret.type = "Opaque"
    kubeconfigSecret.data = {
        "kubeconfig": b64encode(kubeconfig.encode("utf-8")).decode("utf-8")
    }
    kubeconfigSecret.metadata.owner_references = [
        client.V1OwnerReference(
            api_version="v1",
            kind="Secret",
            name=body["metadata"]["name"],
            uid=body["metadata"]["uid"],
        )
    ]

    # Create the secret in the cluster
    logger.debug(f"Creating kubeconfig secret for {name}")
    config.load_incluster_config()
    kubeconfigSecret = client.CoreV1Api().create_namespaced_secret(
        namespace, kubeconfigSecret
    )
    logger.info(f"Created kubeconfig secret {kubeconfigSecret.metadata.name}")
