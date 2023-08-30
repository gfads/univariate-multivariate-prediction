#!/bin/bash

kubectl apply -f ns.yml;
kubectl apply -f db.yml;
kubectl apply -f cm-app.yml;
kubectl apply -f cm-jvm.yml;
kubectl apply -f deployment.yml;
kubectl apply -f svc.yml;
