from copy import deepcopy
from time import sleep

from keras.models import load_model

from analyser import Analyser
from common_methods import load_pickle
from executor import Executor
from monitor import Monitor
from planner import Planner

forecasting_time = '3m'
offset = ''

METRICS = {
    'pods': {
        'current': 0,
        'models': {},
        'query': '(sum(kube_deployment_spec_replicas{namespace="$n", deployment=~"$s.*"}) by ('
                 'deployment))',
        'time_series': []
    },

    'cpu': {
        'current': 0,
        'desired': 0.16,
        'models': {},
        'query': 'sum(rate(container_cpu_usage_seconds_total{id=~".*kubepods.*", namespace="$n", '
                 'pod=~"$s.*", name!~".*POD.*"}[1m]' + offset + '))',
        'query1': 'avg(rate(container_cpu_usage_seconds_total{id=~".*kubepods.*", namespace="$n", '
                  'pod=~"$s.*", name!~".*POD.*"}[1m]' + offset + '))',
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
        'query': '((histogram_quantile(0.95, sum(irate(istio_request_duration_milliseconds_bucket{reporter="destination", '
                 'destination_workload_namespace=~"$n", destination_workload=~"$s.*"}[1m]' + offset + ')) by '
                                                                                                      '(le, destination_workload))) / 1000)',
        'time_series': []
    },

    'tp': {
        'current': 0,
        'models': {},
        'query': 'round(sum(irate(istio_requests_total{reporter="destination", destination_workload=~"$s.*"}[1m]' + offset + ')) by ('
                                                                                                                             'destination_workload), 0.001)',
        'time_series': []
    }
}

deploys = {
    'discounts-v1': {'queries': deepcopy(METRICS), 'namespace': 'travel-agency',
                'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                'stabilization': {'scale': -1},
                'adaptation_command': '',
                'lstm': load_model('knowledge/models/travels/discounts/' + forecasting_time + '/model.h5'),
                'slstm': load_pickle('travels/discounts/' + forecasting_time + '/scaler')},
    'cars-v1': {'queries': deepcopy(METRICS), 'namespace': 'travel-agency',
                'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                'stabilization': {'scale': -1},
                'adaptation_command': '',
                'lstm': load_model('knowledge/models/travels/cars/' + forecasting_time + '/model.h5'),
                'slstm': load_pickle('travels/cars/' + forecasting_time + '/scaler')},

    'flights-v1': {'queries': deepcopy(METRICS), 'namespace': 'travel-agency',
                   'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                   'stabilization': {'scale': -1},
                   'adaptation_command': '',
                   'lstm': load_model(
                       'knowledge/models/travels/flights/' + forecasting_time + '/model.h5'),
                   'slstm': load_pickle('travels/flights/' + forecasting_time + '/scaler')},

    'hotels-v1': {'queries': deepcopy(METRICS), 'namespace': 'travel-agency',
                  'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                  'stabilization': {'scale': -1},
                  'adaptation_command': '',
                  'lstm': load_model(
                      'knowledge/models/travels/hotels/' + forecasting_time + '/model.h5'),
                  'slstm': load_pickle('travels/hotels/' + forecasting_time + '/scaler')},

    'insurances-v1': {'queries': deepcopy(METRICS), 'namespace': 'travel-agency',
                      'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                      'stabilization': {'scale': -1},
                      'adaptation_command': '',
                      'lstm': load_model(
                          'knowledge/models/travels/insurances/' + forecasting_time + '/model.h5'),
                      'slstm': load_pickle('travels/insurances/' + forecasting_time + '/scaler')},

    'travels-v1': {'queries': deepcopy(METRICS), 'namespace': 'travel-agency',
                   'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 100},
                   'stabilization': {'scale': -1},
                   'adaptation_command': '',
                   'lstm': load_model(
                       'knowledge/models/travels/travels/' + forecasting_time + '/model.h5'),
                   'slstm': load_pickle('travels/travels/' + forecasting_time + '/scaler')},

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
