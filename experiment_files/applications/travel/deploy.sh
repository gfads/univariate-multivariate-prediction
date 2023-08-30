#!/bin/bash

kubectl create namespace travel-agency;
kubectl label namespace travel-agency istio-injection=enabled
kubectl apply -f deploy.yml -n travel-agency;
