@Echo off

:: 設置當前bat執行區塊
Setlocal

:: 執行更新資料庫Schema結構腳本檔，使用flask-script、flask-migrate
:: 透過'Manage.py'程式執行flask-script和flask-migrate
:: 使用flask-script管理資料庫更動，命令如下
:: 1. python manage.py db init
:: 2. python manage.py db migrate
:: 3. python mange.py db upgrade

:: 設置所在位置目錄
Set DirPath=E:\Project\IKEA_Project\System_Demo\CASY_Project\

:: 設置migrations目錄名稱
Set DirectoryName=migrations\

:: 判斷 'migrations' 完整路徑是否存在
IF NOT EXIST %DirPath%%DirectoryName% (
    echo The [ %DirPath%%DirectoryName% ] is not exists.
    echo Skip remove action.

) else (
    echo The [ %DirPath%%DirectoryName% ] is exists.
    echo Remove 'migrations' directory.
    rmdir /s /q %DirPath%%DirectoryName%

)

:: 初始化建立migrations目錄
echo Create Initialize 'migrations' Directory , by Run SQLAlchemy init.
python Manage.py db init

:: 產生資料表結構
echo Run SQLAlchemy migrate.
python Manage.py db migrate

:: 更新資料表結構
echo Run SQLAlchemy upgrade.
python Manage.py db upgrade

Endlocal

pause
