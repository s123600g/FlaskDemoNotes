#!/bin/bash

# 添加nginx全域設定-關掉守護線程
# 避免一開始container啟動執行時，因啟動nginx服務是執行腳本而不是一個程序
# 當程序pid=1結束掉時，docker會判定此container工作已經結束執行，自動把container跳出執行
nginx -g 'daemon off;' | uwsgi --ini /web/web_data/uwsgi.ini