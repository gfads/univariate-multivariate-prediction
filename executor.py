class Executor:
    def execute(self, deploys):
        from kubernetes import client, config
        from time import time
        from kubernetes.client import ApiException

        configuration = config.load_kube_config()
        api_instance = client.AppsV1Api(client.ApiClient(configuration))

        for dname, deploy in deploys.items():
            if deploy['adaptation_command'] != '':
                name = dname
                replicas_neeeded = deploy['replicas']['needed']
                namespace = deploy['namespace']
                body = {'spec': {'replicas': replicas_neeeded}}
                pretty = 'true'

                try:
                    api_instance.patch_namespaced_deployment_scale(name, namespace, body, pretty=pretty)
                    deploy['stabilization'][deploy['adaptation_command']] = time()
                    print(name + ' have a scale operation', replicas_neeeded)
                except ApiException as e:
                    print("Exception when calling AppsV1Api->patch_namespaced_deployment_scale: %s\n" % e)
