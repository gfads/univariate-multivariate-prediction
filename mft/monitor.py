from prometheus_api_client.utils import parse_datetime
from prometheus_api_client import PrometheusConnect


class Prometheus:
    end_time: parse_datetime = None
    start_time: parse_datetime = None
    step: str = None
    prometheus_endpoint: str = None
    prometheus: PrometheusConnect = None

    def __init__(self, prometheus_endpoint: str, step=None):
        self.prometheus_endpoint = prometheus_endpoint
        self.step = step
        self.connect_prometheus()

    def __set_time__(self, end_time, start_time):
        self.end_time = parse_datetime(end_time)
        self.start_time = parse_datetime(start_time)

    def connect_prometheus(self):
        from prometheus_api_client import PrometheusConnect

        self.prometheus = PrometheusConnect(url=self.prometheus_endpoint, disable_ssl=True)

    def collect_query(self, end_time, query, start_time):
        from prometheus_api_client import MetricRangeDataFrame
        self.__set_time__(end_time, start_time)

        bo = MetricRangeDataFrame(self.prometheus.custom_query_range(query=query, start_time=self.start_time,
                                                                     end_time=self.end_time, step=self.step)
                                  )

        return bo['value'].values.astype(float)


class Monitor:
    end_time: str = None
    query: None
    prometheus: Prometheus = None
    start_time: str = None

    def __init__(self, prometheus_endpoint: str, end_time: str = None, start_time: str = None, step: str = None,
                 query: str = None):
        self.query = query
        self.end_time = end_time
        self.start_time = start_time
        self.prometheus = Prometheus(prometheus_endpoint, step)

    def __set_query__(self, query):
        self.query = query

    def reactive(self, deploys):
        from math import isnan

        self.collect_replicas(deploys)

        for k_deploy, deploy in deploys.items():
            for qn, query in deploy['queries'].items():
                if qn == 'cpu':
                    self.__set_query__(
                        query['query'].replace('$s', k_deploy).replace('$n', deploy['namespace']))
                else:
                    self.__set_query__(
                        query['query'].replace('$s', k_deploy).replace('$n', deploy['namespace']))

                query['current'] = self.prometheus.collect_query(self.end_time, self.query, self.start_time)[-1]

                if isnan(query['current']):
                    query['current'] = 0.01

    def proactive(self, deploys):
        self.collect_replicas(deploys)

        for k_deploy, deploy in deploys.items():
            for qn, query in deploy['queries'].items():
                if query != 'pods':
                    self.__set_query__(
                        query['query'].replace('$s', k_deploy).replace('$n', deploy['namespace']))

                if qn == 'pods':
                    query['time_series'] = self.prometheus.collect_query(self.end_time, self.query,
                                                                         str(int(self.start_time[:-1])) + 'm')

                query['time_series'] = self.prometheus.collect_query(self.end_time, self.query, self.start_time)
                query['current'] = query['time_series'][-1]

    def collect_replicas(self, deploys):
        from kubernetes.client.rest import ApiException
        from kubernetes import config, client

        configuration = config.load_kube_config()
        api_instance = client.AppsV1Api(client.ApiClient(configuration))

        for name, deploy in deploys.items():
            namespace = deploy['namespace']

            try:
                api_response = api_instance.read_namespaced_deployment_scale(name, namespace)
                deploy['replicas']['current'] = api_response.spec.replicas
            except ApiException as e:
                print("Exception when calling AppsV1Api->read_namespaced_deployment_scale: %s\n" % e.reason)
