#!/bin/bash

db2 connect to tradedb;

while true; do \
    db2 "DELETE FROM (SELECT * FROM HOLDINGEJB FETCH FIRST $(($(db2 connect to tradedb 2>&1 > /dev/null ; db2 "select count (*) HOLDINGEJB from HOLDINGEJB" | grep -E "[0-9]+" | tail -n 2 | head -n 1) - 2596)) ROWS ONLY) AS A"; \

    db2 "DELETE FROM (SELECT * FROM ORDEREJB FETCH FIRST $(($(db2 connect to tradedb 2>&1 > /dev/null ; db2 "select count (*) ORDEREJB from ORDEREJB" | grep -E "[0-9]+" | tail -n 2 | head -n 1) - 2596)) ROWS ONLY) AS A"; \
sleep 1; 
done;
