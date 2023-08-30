#!/bin/bash

kubectl apply -f ob-deployment.yaml;
sleep 3m;
kubectl delete deployment/loadgenerator;
