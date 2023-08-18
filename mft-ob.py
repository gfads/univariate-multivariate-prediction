from time import sleep
from analyser import Analyser
from executor import Executor
from monitor import Monitor
from planner import Planner
from copy import deepcopy
from keras.models import load_model
from common_methods import load_pickle

forecasting_time = '3m'
offset = ''

METRICS = {
    'pods': {
        'current': 0,
        'models': {},
        'query': 'sum(kube_deployment_spec_replicas{namespace="$n", deployment=~"$s.*"}) by ('
                 'deployment)',
        'time_series': []
    },

    'cpu': {
        'current': 0,
        'desired': 0.08,
        'models': {},
        'query': 'sum(rate(container_cpu_usage_seconds_total{id=~".*kubepods.*", namespace="$n", '
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
        'desired': 0.8,
        'models': {},
        'query': '((histogram_quantile(0.95, sum(irate(istio_request_duration_milliseconds_bucket{reporter="destination", '
                 'destination_workload_namespace=~"$n", destination_workload=~"$s.*"}[1m]' + offset + ')) by '
                                                                                                      '(le, destination_workload))) / 1000)',
        'time_series': []
    },

    'tp': {
        'current': 0,
        'desired': 0.8,
        'models': {},
        'query': 'round(sum(irate(istio_requests_total{reporter="destination", destination_workload=~"$s.*"}[1m]' + offset + ')) by ('
                                                                                                                             'destination_workload), 0.001)',
        'time_series': []
    }
}

deploys = {
    'adservice': {'queries': deepcopy(METRICS), 'namespace': 'default',
                  'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                  'stabilization': {'scale': -1},
                  'adaptation_command': '',
                  'lstm': load_model('knowledge/models/ob/adservice/' + forecasting_time + '/model.h5'),
                  'slstm': load_pickle('ob/adservice/' + forecasting_time + '/scaler')},

    'cartservice': {'queries': deepcopy(METRICS), 'namespace': 'default',
                    'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                    'stabilization': {'scale': -1},
                    'adaptation_command': '',
                    'lstm': load_model('knowledge/models/ob/cartservice/' + forecasting_time + '/model.h5'),
                    'slstm': load_pickle('ob/cartservice/' + forecasting_time + '/scaler')},

    'checkoutservice': {'queries': deepcopy(METRICS), 'namespace': 'default',
                        'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                        'stabilization': {'scale': -1},
                        'adaptation_command': '',
                        'lstm': load_model('knowledge/models/ob/checkoutservice/' + forecasting_time + '/model.h5'),
                        'slstm': load_pickle('ob/checkoutservice/' + forecasting_time + '/scaler')},

    'currencyservice': {'queries': deepcopy(METRICS), 'namespace': 'default',
                        'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                        'stabilization': {'scale': -1},
                        'adaptation_command': '',
                        'lstm': load_model('knowledge/models/ob/currencyservice/' + forecasting_time + '/model.h5'),
                        'slstm': load_pickle('ob/currencyservice/' + forecasting_time + '/scaler')},

    'emailservice': {'queries': deepcopy(METRICS), 'namespace': 'default',
                     'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                     'stabilization': {'scale': -1},
                     'adaptation_command': '',
                     'lstm': load_model('knowledge/models/ob/emailservice/' + forecasting_time + '/model.h5'),
                     'slstm': load_pickle('ob/emailservice/' + forecasting_time + '/scaler')},

    'frontend': {'queries': deepcopy(METRICS), 'namespace': 'default',
                 'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                 'stabilization': {'scale': -1},
                 'adaptation_command': '',
                 'lstm': load_model('knowledge/models/ob/frontend/' + forecasting_time + '/model.h5'),
                 'slstm': load_pickle('ob/frontend/' + forecasting_time + '/scaler')},

    'paymentservice': {'queries': deepcopy(METRICS), 'namespace': 'default',
                       'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                       'stabilization': {'scale': -1},
                       'adaptation_command': '',
                       'lstm': load_model('knowledge/models/ob/paymentservice/' + forecasting_time + '/model.h5'),
                       'slstm': load_pickle('ob/paymentservice/' + forecasting_time + '/scaler')},

    'productcatalogservice': {'queries': deepcopy(METRICS), 'namespace': 'default',
                              'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                              'stabilization': {'scale': -1},
                              'adaptation_command': '',
                              'lstm': load_model(
                                  'knowledge/models/ob/productcatalogservice/' + forecasting_time + '/model.h5'),
                              'slstm': load_pickle('ob/productcatalogservice/' + forecasting_time + '/scaler')},

    'recommendationservice': {'queries': deepcopy(METRICS), 'namespace': 'default',
                              'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                              'stabilization': {'scale': -1},
                              'adaptation_command': '',
                              'lstm': load_model(
                                  'knowledge/models/ob/recommendationservice/' + forecasting_time + '/model.h5'),
                              'slstm': load_pickle('ob/recommendationservice/' + forecasting_time + '/scaler')},
    'shippingservice': {'queries': deepcopy(METRICS), 'namespace': 'default',
                        'replicas': {'current': 0, 'needed': 0, 'min': 1, 'max': 10},
                        'stabilization': {'scale': -1},
                        'adaptation_command': '',
                        'lstm': load_model('knowledge/models/ob/shippingservice/' + forecasting_time + '/model.h5'),
                        'slstm': load_pickle('ob/shippingservice/' + forecasting_time + '/scaler')},
}

deploys['adservice']['queries']['cpu']['desired'] = 0.08
deploys['cartservice']['queries']['cpu']['desired'] = 0.08
deploys['checkoutservice']['queries']['cpu']['desired'] = 0.08
deploys['currencyservice']['queries']['cpu']['desired'] = 0.08
deploys['emailservice']['queries']['cpu']['desired'] = 0.08
deploys['frontend']['queries']['cpu']['desired'] = 0.08
deploys['paymentservice']['queries']['cpu']['desired'] = 0.08
deploys['productcatalogservice']['queries']['cpu']['desired'] = 0.08
deploys['recommendationservice']['queries']['cpu']['desired'] = 0.16
deploys['shippingservice']['queries']['cpu']['desired'] = 0.08

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
