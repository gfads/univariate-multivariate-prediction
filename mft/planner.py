class Planner:
    stabilization_window_time: int = 300

    def planner(self, deploys):
        from math import ceil

        for _, deploy in deploys.items():
            for name, query in deploy['queries'].items():
                ratio = query['ratio']

                if not 0.9 <= ratio <= 1.1:
                    query['replicas'] = ceil(deploy['replicas']['current'] * ratio)
                    deploy[name + 'adapt'] = True
                else:
                    deploy[name + 'adapt'] = False

            deploy['replicas']['needed'] = self.better_two(deploy)

    def better_two(self, deploy):
        adapt = True

        replicas = []
        for name, query in deploy['queries'].items():
            replicas.append(query['replicas'])
            if not deploy[name + 'adapt']:
                adapt = False

        if adapt:
            return min(replicas)
        else:
            self.is_it_blocked_by_quarantine(deploy)
            return 0

    def is_it_blocked_by_quarantine(self, deploy):
        from time import time

        if deploy['quarantine']:
            time_in_quarantine = time() - deploy['quarantine_time']
            if time_in_quarantine >= self.stabilization_window_time:
                deploy['quarantine'] = False
                deploy['quarantine_time'] = 0
                return False
            else:
                return True
        else:
            return False
