from time import sleep
from analyser import Analyser
from executor import Executor
from monitor import Monitor
from planner import Planner
from copy import deepcopy
from keras.models import load_model
from common_methods import load_pickle


forecasting_time = '5m'
offset = ''

METRICS = {
    'pods': {
        'current': 0,
        'models': {},
        'query': 'sum(kube_deployment_spec_replicas{namespace="$n", deployment=~"$s.*"}'+offset+') by ('
                 'deployment)',
        'time_series': []
    },

    'cpu': {
        'current': 0,
        'desired': 0.5,
        'models': {},
        'query': 'sum(rate(container_cpu_usage_seconds_total{id=~".*kubepods.*", namespace="$n", '
                 'pod=~"$s.*", name!~".*POD.*", container!=""}[1m]'+offset+'))',

        'query1': 'avg(rate(container_cpu_usage_seconds_total{id=~".*kubepods.*", namespace="$n", '
                 'pod=~"$s.*", name!~".*POD.*", container!=""}[1m]'+offset+'))',

        'time_series': []
    },

    'heap': {
        'current': 0,
        'models': {},
        'query': '(sum(avg_over_time(base_memory_usedHeap_bytes{pod=~"$s.*"}[1m]'+offset+')))',
        'time_series': []
    },

    'jvm_total_MarkSweepCompact': {
        'current': 0,
        'models': {},
        'query': '(sum(rate(base_gc_total{name="MarkSweepCompact"}[1m]' + offset + ')))',
        'time_series': []
    },

    'jvm_total_Copy': {
        'current': 0,
        'models': {},
        'query': '(sum(rate(base_gc_total{name="Copy"}[1m]' + offset + ')))',
        'time_series': []
    },

    'jvm_seconds_Copy': {
        'current': 0,
        'models': {},
        'query': '(sum(rate(base_gc_time_total_seconds{name="Copy"}[1m]' + offset + ')) / sum(deriv('
                                                                                    'base_gc_time_total_seconds{name="Copy"}[1m]' + offset + ')))',
        'time_series': []
    },

    'jvm_seconds_MarkSweepCompact': {
        'current': 0,
        'models': {},
        'query': '(sum(rate(base_gc_time_total_seconds{name="MarkSweepCompact"}[1m]' + offset + ')) / sum(deriv('
                                                                                                'base_gc_time_total_seconds{name="MarkSweepCompact"}[1m]' + offset + ')))',
        'time_series': []
    },

    'memory': {
        'current': 0,
        'models': {},
        'query': 'sum(max_over_time(container_memory_working_set_bytes{id=~".*kubepods.*", namespace="$n",'
                 'pod=~"$s-.*", name!~".*POD.*", container=""}[1m]'+offset+'))',
        'time_series': []
    },

    'rt': {
        'current': 0,
        'models': {},
        'query': 'avg(deriv(base_REST_request_elapsedTime_seconds{pod=~"$s.*",name!~".*POD.*", '
                 'class="com.acme.crud.FruitResource"}[1m]'+offset+'))',
        'time_series': []
    },

    'tp': {
        'current': 0,
        'models': {},
        'query': 'sum(rate(base_REST_request_total{pod=~"$s.*",name!~".*POD.*",'
                 'class="com.acme.crud.FruitResource"}[1m]'+offset+'))',
        'time_series': []
    },
}

deploys = {
    'quarkus-service': {'queries': deepcopy(METRICS), 'namespace': 'quarkus',
                        'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                        'stabilization': {'scale': -1},
                        'adaptation_command': '',
                        'lstm': load_model('knowledge/models/quarkus/' + forecasting_time + '/model.h5'),
                        'slstm': load_pickle('quarkus/' + forecasting_time + '/scaler'),
                        },

}

URL_PROMETHEUS = 'http://10.66.66.53:30000/'

enable_proactive = 68

m1 = None
if forecasting_time == '1m':
    m1 = Monitor(URL_PROMETHEUS, end_time='now', start_time='19m', step='60')  # 1m
elif forecasting_time == '3m':
    m1 = Monitor(URL_PROMETHEUS, end_time='now', start_time='20m', step='180')  # 3m
elif forecasting_time == '5m':
    m1 = Monitor(URL_PROMETHEUS, end_time='now', start_time='19m', step='300')  # 5m

m2 = Monitor(URL_PROMETHEUS, end_time='now', start_time='1m', step='60')

analyser = Analyser(replica_conflict='only')
planner = Planner()
executor = Executor()

a = 0
while True:
    print('Iteration: ', a)
    if a >= enable_proactive:
        m1.proactive(deploys)
        analyser.predict_multivariate(deploys)
        analyser.proactive(deploys)
    else:
        m2.reactive(deploys)
        analyser.reactive(deploys)

    executor.execute(deploys)
    a += 1
    sleep(15)
