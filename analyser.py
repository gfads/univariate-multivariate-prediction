
class Analyser:
    stabilization_window_time: int = 300
    stabilization: bool = True
    quarantine: bool = True
    ratio: float = None
    score: float = None
    replicas: int = None
    replica_conflict: str = 'everyone'

    def __init__(self, replica_conflict: str = 'everyone', stabilization=True, stabilization_window_time: int = 300):
        self.replica_conflict = replica_conflict
        self.stabilization = stabilization
        self.stabilization_window_time = stabilization_window_time

    def __set_ratio__(self, ratio):
        self.ratio = ratio

    def __set_score__(self, score):
        self.score = score

    def proactive(self, deploys):
        for dname, deploy in deploys.items():

            if abs(deploy['replicas']['current'] - deploy['replicas']['needed']) >= 0.8:
                deploy['replicas']['needed'] = round(deploy['replicas']['needed'])

                deploy['adaptation_command'] = 'scale'

            if deploy['adaptation_command'] != '':
                self.assessment_of_the_possibility_of_adaptation(deploy)
                self.can_adapt(deploy)

    def reactive(self, deploys):
        from datetime import datetime

        for dname, deploy in deploys.items():

            d = (deploy['queries']['cpu']['current'] / deploy['queries']['pods']['current'])

            self.calculate_ratio(d, deploy['queries']['cpu']['desired'])
            self.calculate_pod_needed_by_metric(deploy['replicas']['current'])
            self.calculate_pod_needed(deploy)

            print(f'CPU % in {(datetime.now()).strftime("%H:%M:%S")} to {dname} is {d: .3}')

            if deploy['adaptation_command'] != '':
                print(f'{deploy["replicas"]["needed"]} Pods to {dname} are needed!')
                self.assessment_of_the_possibility_of_adaptation(deploy)
                self.can_adapt(deploy)

    def predict_multivariate(self, deploys):
        from numpy import array, newaxis, repeat
        from pandas import DataFrame
        for dname, deploy in deploys.items():
            input_data = {}

            for name, query in deploy['queries'].items():
                input_data[name] = query['time_series']

            try:
                df = DataFrame.from_dict(input_data).fillna(0)
                input_data_normalized = deploy['slstm'].transform(df)
                pred = deploy['lstm'].predict(array(input_data_normalized[newaxis, :, :]), verbose=0)
                pred_unormalized = deploy['slstm'].inverse_transform(repeat(pred, len(input_data.keys()), axis=-1))[:, 0]
                deploy['replicas']['needed'] = pred_unormalized[0]

                if deploy['replicas']['needed'] != deploy['replicas']['needed']:
                    self.calculate_ratio(deploy['queries']['cpu']['current'], deploy['queries']['cpu']['desired'])
                    self.calculate_pod_needed_by_metric(deploy['replicas']['current'])
                    deploy['replicas']['needed'] = float(self.replicas)
                    print('NaN Prediction')
            except BaseException as e:
                print('Error: ', e)
                deploy['replicas']['needed'] = deploy['replicas']['current']

            deploy['replicas']['needed'] = round(deploy['replicas']['needed'])
            print(f'Predicted {deploy["replicas"]["needed"]} Pods to {dname} needed in the next minute!')

    def can_adapt(self, deploy):
        replicas_min = deploy['replicas']['min']
        replicas_max = deploy['replicas']['max']
        replicas_needed = deploy['replicas']['needed']
        replicas_current = deploy['replicas']['current']

        # Se a quantidade de réplicas pedida é menor que o mínimo!  or (replicas_current == replicas_min):
        if replicas_needed < replicas_min:
            deploy['adaptation_command'] = ''

        # Se o número pedido é igual o atual.
        if replicas_current == replicas_needed:
            deploy['adaptation_command'] = ''

        if replicas_needed > replicas_max and replicas_current == replicas_max:
            deploy['adaptation_command'] = ''

        if replicas_needed > replicas_max and replicas_current != replicas_max:
            deploy['replicas']['needed'] = replicas_max

    def calculate_ratio(self, current, desired):
        self.__set_ratio__(current / desired)

    def calculate_score(self, queries):
        throughput = queries['throughput']['current']
        response_time = queries['response_time']['current']
        cpu = queries['cpu']['current']
        memory = queries['memory']['current']

        self.__set_score__(((1 / (1 + response_time)) * (throughput / (cpu + memory))))

    def calculate_pod_needed_by_metric(self, current_pods):
        from math import ceil

        if not 0.9 <= self.ratio <= 1.1:
            self.replicas = ceil(current_pods * self.ratio) if ceil(current_pods * self.ratio) != 0 else current_pods
        else:
            self.replicas = current_pods

    def calculate_pod_needed(self, deploy):
        if self.replica_conflict == 'everyone':
            self.everyone(deploy)
        elif self.replica_conflict == 'anyone':
            self.anyone(deploy)
        elif self.replica_conflict == 'only':
            self.only(deploy)

    def only(self, deploy):

        if deploy['replicas']['current'] == self.replicas:
            deploy['adaptation_command'] = ''
            return

        # print(deploy['adaptation_command'])

        deploy['replicas']['needed'] = self.replicas
        deploy['adaptation_command'] = 'scale'

    def everyone(self, deploy):
        replicas = []
        for name, query in deploy['queries'].items():
            replicas.append(query['replicas'])

            if query['replicas'] == deploy['replicas']['current']:
                deploy['adaptation_command'] = ''
                return

        deploy['replicas']['needed'] = min(replicas)

        if deploy['replicas']['current'] > deploy['replicas']['needed']:
            #            deploy['adaptation_command'] = 'scale-in'
            deploy['adaptation_command'] = 'scale'
        else:
            #            deploy['adaptation_command'] = 'scale-out'
            deploy['adaptation_command'] = 'scale'

        # print(deploy['adaptation_command'], deploy['replicas']['needed'])

    def anyone(self, deploy):
        replicas = []
        for name, query in deploy['queries'].items():
            if query['replicas'] != deploy['replicas']['current']:
                replicas.append(query['replicas'])

        if not replicas:
            deploy['adaptation_command'] = ''
        elif deploy['replicas']['current'] > min(replicas):
            deploy['adaptation_command'] = 'scale-in'
        else:
            deploy['adaptation_command'] = 'scale-out'

        deploy['replicas']['needed'] = min(replicas)

    def assessment_of_the_possibility_of_adaptation(self, deploy):
        if self.stabilization:
            self.check_stabilization(deploy)

    def check_stabilization(self, deploy):
        from time import time

        if deploy['stabilization'][deploy['adaptation_command']] != -1:
            current_stabilization_time = time() - deploy['stabilization'][deploy['adaptation_command']]

            if current_stabilization_time >= self.stabilization_window_time:
                deploy['stabilization'][deploy['adaptation_command']] = -1
            else:
                deploy['adaptation_command'] = ''
