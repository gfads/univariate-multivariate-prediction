#!/bin/bash

kubectl delete -f deploy.yml -n travel-agency;
kubectl delete namespace travel-agency;
