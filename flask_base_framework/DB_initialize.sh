# !/bin/bash
PATH=/sbin:/bin:/usr/bin

# Use source or . command by terminal.
# Ex: source script.sh  ||  . script.sh
# Not use sh command by terminal.

echo 

echo '執行更新資料庫-資料表資料欄位設定更新.'

echo

echo '移除migrations目錄'

rm -r migrations

sleep 1s

echo

echo '初始化建立migrations目錄'
echo

python3 Manage.py db init

sleep 1s

echo
echo '產生資料表結構'
echo 

python3 Manage.py db migrate

sleep 1s

echo
echo '更新資料表結構'
echo

python3 Manage.py db upgrade