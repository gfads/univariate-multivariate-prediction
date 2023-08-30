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
        'query': '(sum(kube_deployment_spec_replicas{namespace="$n", deployment=~"$s.*"} ' + offset + ') by ('
                                                                                                      'deployment))',
        'time_series': []
    },

    'conn-pool_jdbc_TradeDataSource': {
        'current': 0,
        'desired': 0,
        'models': {},
        'query': 'avg(avg_over_time(vendor_connectionpool_managedConnections{pod=~"$s.*", name!~".*POD.*,", '
                 'datasource="jdbc_TradeDataSource"}[1m]' + offset + '))',
        'time_series': []
    },

    'conn-pool_jms_TradeStreamerTCF': {
        'current': 0,
        'desired': 0,
        'models': {},
        'query': 'avg(avg_over_time(vendor_connectionpool_managedConnections{pod=~"$s.*", name!~".*POD.*,", '
                 'datasource="jms_TradeStreamerTCF"}[1m]' + offset + '))',
        'time_series': []
    },

    'cpu': {
        'current': 0,
        'desired': 0.8,
        'models': {},
        'query': 'sum(rate(base_cpu_processCpuTime_seconds{app="daytrader"}[1m]' + offset + '))',
        'time_series': []
    },

    'heap': {
        'current': 0,
        'models': {},
        'query': 'sum(avg_over_time(base_memory_maxHeap_bytes{pod=~"$s.*"}[1m]' + offset + '))',
        'time_series': []
    },

    'jvm_total_scavenge': {
        'current': 0,
        'models': {},
        'query': '(sum(rate(base_gc_total{name="scavenge"}[1m]' + offset + ')))',
        'time_series': []
    },

    'jvm_total_global': {
        'current': 0,
        'models': {},
        'query': '(sum(rate(base_gc_total{name="global"}[1m]' + offset + ')))',
        'time_series': []
    },

    'jvm_seconds_scavenge': {
        'current': 0,
        'models': {},
        'query': '(sum(rate(base_gc_time_seconds{name="scavenge"}[1m]' + offset + ')) / sum(deriv(base_gc_time_seconds{'
                                                                                  'name="scavenge"}[1m]' + offset + ')))',
        'time_series': []
    },

    'jvm_seconds_global': {
        'current': 0,
        'models': {},
        'query': '(sum(rate(base_gc_time_seconds{name="global"}[1m]' + offset + ')) / sum(deriv('
                                                                                'base_gc_time_seconds{name="global"}['
                                                                                '1m]' + offset + ')))',
        'time_series': []
    },

    'memory': {
        'current': 0,
        'models': {},
        'query': 'sum(max_over_time(container_memory_working_set_bytes{id=~".*kubepods.*", namespace="$n",'
                 'pod=~"$s-.*", name!~".*POD.*", container=""}[1m]' + offset + '))',
        'time_series': []
    },

    'rt': {
        'current': 0,
        'models': {},
        'query': '(sum by (app) (rate(vendor_servlet_responseTime_total_seconds{pod=~"$s.*", '
                 'servlet!~"com_ibm_ws_microprofile.*"}[1m]' + offset + ') / rate(vendor_servlet_request_total{'
                                                                        'pod=~"$s.*", '
                                                                        'servlet!~"com_ibm_ws_microprofile.*"}[1m]' +
                 offset + ') > 0))',
        'time_series': []
    },

    'tp': {
        'current': 0,
        'models': {},
        'query': 'sum(rate(vendor_servlet_request_total{pod=~"$s.*",' 'servlet!~"com_ibm_ws_microprofile.*|.*Trade'
                 '.*"}[1m]' + offset + '))',
        'time_series': []
    },

    'thread_pool': {
        'current': 0,
        'models': {},
        'query': 'avg(avg_over_time(vendor_threadpool_activeThreads{pod=~"$s.*", name!~".*POD.*"}[1m]' + offset + '))',
        'time_series': []
    },
}

deploys = {
    'daytrader-service': {'queries': deepcopy(METRICS), 'namespace': 'daytrader',
                          'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                          'stabilization': {'scale': -1},
                          'adaptation_command': '',
                          'lstm': load_model('knowledge/models/daytrader-service/' + forecasting_time + '/model.h5'),
                          'slstm': load_pickle('daytrader-service/' + forecasting_time + '/scaler'),
                          }
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
