# -*- coding: utf-8 -*-

from flask import request, redirect, session ,flash ,send_from_directory, make_response,Response,render_template,Flask, url_for, jsonify, g
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from Config import config
from datetime import timedelta
from DataProcess import DataProcess
from datetime_format import datetime_format
from random import randrange

import datetime as dtime
import os
import time
import shutil
import codecs

app = Flask(__name__,
            static_url_path='/',
            static_folder='static',
            template_folder='templates')

# 載入 Flask Config Setting Values，模式為 developermentConfig
app.config.from_object(config['developermentConfig'])

# 載入 Flask Config Setting Values，模式為 productionConfig
# app.config.from_object(config['productionConfig'])

# Create Flask-RESTful API Instance
api = Api(app)

# Create SQLAlchemy Instance
db = SQLAlchemy(app)

# Flask Login Packge Config
login_manager = LoginManager()
login_manager.login_view = 'login'  # 設置當需要登入要求時，預設轉址的頁面
login_manager.init_app(app=app)

'''
----------------------------------------------------------------------
從Model中匯入資料表模型
----------------------------------------------------------------------
'''
from Model import Base_Data

'''-------------------------------------------------------------------'''

'''
----------------------------------------------------------------------
載入Module模組
----------------------------------------------------------------------
'''

'''-------------------------------------------------------------------'''

'''
----------------------------------------------------------------------
Flask-RESTful API
----------------------------------------------------------------------
'''

'''-------------------------------------------------------------------'''

'''
----------------------------------------------------------------------
通用功能實作區塊
----------------------------------------------------------------------
'''
def get_current_splitdtime(dtime): # 取得分割的時間格式
    '''
    分割時間格式為兩筆清單，分別為[年 月 日]與[時 分 秒]
    '''

    split_dtime = str(dtime).split(" ")

    split_date = str(split_dtime[0]).split("-") # 年 月 日
    split_time = str(split_dtime[1]).split(":") # 時 分 秒

    # print("[get_current_splitdtime]Year: {} , Month: {} , Day: {}".format(split_date[0],split_date[1],split_date[2]))
    # print("[get_current_splitdtime]Hour: {} , Min: {} , Sec: {}".format(split_time[0],split_time[1],split_time[2]))

    return split_date , split_time

def get_current_datetime(): # 取得當前系統時間

    get_CurrentTime =  dtime.datetime.now().strftime(time_format)

    # split_dtime = str(get_CurrentTime).split(" ")

    # split_date = str(split_dtime[0]).split("-") # 年 月 日
    # split_time = str(split_dtime[1]).split(":") # 時 分 秒

    split_date , split_time = get_current_splitdtime(get_CurrentTime)

    # print("[get_current_datetime]Year: {} , Month: {} , Day: {}".format(split_date[0],split_date[1],split_date[2]))
    # print("[get_current_datetime]Hour: {} , Min: {} , Sec: {}".format(split_time[0],split_time[1],split_time[2]))

    return get_CurrentTime


def allowed_img_file(filename): # 允許的附件上傳圖片類型
    # print("filename.rsplit('.', 1)[1].lower(): {}".format(filename.rsplit('.', 1)[1].lower()))
    return '.' in filename and \
           str(filename.rsplit('.', 1)[1].lower()) in ALLOWED_IMAGE_EXTENSIONS


def allowed_file_file(filename): # 允許的附件上傳檔案類型
    # print("filename.rsplit('.', 1)[1].lower(): {}".format(filename.rsplit('.', 1)[1].lower()))
    return '.' in filename and \
           str(filename.rsplit('.', 1)[1].lower()) in ALLOWED_File_EXTENSIONS


def check_unable_page(get_page): # 驗證該網站頁面是否開放
    '''
    驗證該網站頁面是否開放
    '''

    is_Unable = False

    if get_page in list_unable_page:

        is_Unable = True

        print("[check_unable_page]該網站[{}]目前不開放.".format(get_page))

    else:

        is_Unable = False

        print("[check_unable_page]該網站[{}]目前開放.".format(get_page))
    
    return is_Unable


def check_programs_authority(): # 驗證使用者程式使用權限
    '''
    驗證使用者程式使用權限
    '''

    # 產生程式權限目錄清單
    list_programs_authority =[]

    # 查詢SYS_Authority
    select_SYS_Authority = T_SA.query.filter_by(UserID = session['UserID']).all()

    for read_row in select_SYS_Authority:

        # print("[check_programs_authority] {}".format(read_row))

        # 取得指定Programs資訊
        programs_list = get_programs_list(PID=read_row.PID)

        if programs_list.Class == "Main":

            list_programs_authority.append(
                {
                    "ProgramsName":programs_list.ProgramsName,
                    "Run":read_row.Run,
                    "Append":read_row.Append,
                    "Edit":read_row.Edit,
                    "Report":read_row.Report,
                    "list_URL":programs_list.list_URL,
                    "add_URL":programs_list.add_URL,
                    "edit_URL":programs_list.edit_URL,
                    "report_URL":programs_list.report_URL
                }
            )

    # print("UserID: {} , list_programs_authority: \n{}".format(
    #     session['UserID'],
    #     list_programs_authority
    # ))

    return list_programs_authority

@login_required  
def initialize_URL():  # 初始化URL參數
    '''
    初始化URL參數
    '''

    list_URL = dict()

    list_URL['Index'] = url_for(
        'index', UserID=session['UserID'], UserName=session['UserNameEn'])

    list_URL['addUser'] = url_for(
        'addUser', UserID=session['UserID'], UserName=session['UserNameEn'])

    list_URL['usermanage'] = url_for(
        'usermanage', UserID=session['UserID'], UserName=session['UserNameEn'])

    list_URL['edituser'] = url_for(
        'edituser', UserID=session['UserID'], UserName=session['UserNameEn'])

    list_URL['sql_test'] = url_for(
        'sql_test', UserID=session['UserID'], UserName=session['UserNameEn'])
    
    list_URL['report_sql'] = url_for(
        'report_sql', UserID=session['UserID'], UserName=session['UserNameEn'])

    list_URL['add_report_sql'] = url_for(
        'add_report_sql', UserID=session['UserID'], UserName=session['UserNameEn'])

    list_URL['login'] = url_for('login')

    list_URL['logout'] = url_for('logout')  

    return list_URL

def initialize_session():  # 初始化Session參數
    
    session.clear() # 清空所有Session

def verify_login_status():  # 驗證是否為登入核准狀態

    # print("[verify_login_status]: verify time: {}".format(get_current_datetime()))
    # print("[verify_login_status]: session['UserID']: {}".format(session['UserID']))
    # print("[verify_login_status]: request.args.get('UserID'): {}".format(request.args.get('UserID')))
    # print("session['UserID']: {}".format(session['UserID']))
    # print("[verify_login_status]: session['UserNameEn']: {}".format(session['UserNameEn']))
    # print("[verify_login_status]: request.args.get('UserName'): {}".format(request.args.get('UserName')))
    # print("session['UserNameEn']: {}".format(session['UserNameEn']))

    # 判斷URL是否沒有user參數 或 網頁參數user跟session不一致
    if ((request.args.get('UserID') is None or request.args.get('UserID') != str(session['UserID'])) or (request.args.get('UserName') is None or request.args.get('UserName') != session['UserNameEn'])) or session['UserID'] == 'DBAdmin' :

        # print("[verify_login_status]: 驗證到登入狀態異常.")
        print("[verify_login_status] verify login status is unauthed.")

        # 初始化Session參數
        # initialize_session()

        logout_user()

        return redirect(url_for('.login'))

def Insert_SysLog(UserID,UserNameEn,UserNameCh,StoreID,StoreNO,DPID,DpName,PageName,log_class,log_content,InertDate): # 寫入系統紀錄至Sys_Log資料表
    '''
    Arguments:
    UserID,UserNameEn,UserNameCh,SID,store_name,DPID,DpName,PageName,log_class,log_content,InertDate
    '''
    db.session.add(
        T_SL(
            UserID = UserID,
            UserNameEn = UserNameEn,
            UserNameCh = UserNameCh,
            StoreID = StoreID,
            StoreNO = StoreNO,
            DPID = DPID,
            DpName = DpName,
            PageName = PageName,
            log_class = log_class,
            log_content = log_content,
            InertDate = InertDate,
        )
    )

    db.session.commit()

def get_programs_list(PID=None,ProgramsName=None):
    '''
    查詢資料庫取得指定Programs資訊\n
    PID：系統編號\n
    ProgramsName：系統名稱\n
    PID != None and ProgramsName = None：只有PID(系統編號)作為查詢條件\n
    PID = None and ProgramsName != None：只有ProgramsName(系統名稱)作為查詢條件\n
    PID != None and ProgramsName!= None：PID(系統編號)與ProgramsName(系統名稱)兩者作為查詢條件\n
    '''
    if PID != None and ProgramsName == None: # 只有PID(系統編號)作為查詢條件
        select_SYS_Programs = T_SP.query.filter_by(PID=PID).first()
    elif PID == None and ProgramsName != None:
        select_SYS_Programs = T_SP.query.filter_by(ProgramsName=ProgramsName).first()
    elif PID != None and ProgramsName!= None:
        select_SYS_Programs = T_SP.query.filter_by(PID=PID,ProgramsName=ProgramsName).first()
    else:
        select_SYS_Programs = T_SP.query.filter_by(Class='Main').all()

    return select_SYS_Programs

def get_DP_list(StoreID):
    '''
    產生查詢部門資訊資料清單
    '''
    select_DP = T_DP.query.filter_by(StoreID = StoreID).all()
    
    list_DP = list()

    for read_row in select_DP:

        temp_dict = dict()

        if read_row.DPID != 1 and read_row.DpName != "Admin":
           
            temp_dict['DpName'] = read_row.DpName
            temp_dict['DPID'] = read_row.DPID
            list_DP.append(temp_dict)

    return list_DP

def get_all_Programs_data():
    '''
    查詢所有程式資訊
    '''
    return T_SP.query.filter_by(Class='Main').all()

def get_Programs_OpenStatus(Program):
    '''
    取得目前程式模組啟用狀態 \n
    Args:  \n
    Program --> 程式模組名稱  \n

    Return:  \n
    A bolean value
    '''

    # 判斷回傳結果是True，代表室啟用狀態回傳False，反之回傳True
    if T_SPO.query.filter_by(ProgramsName=Program).first().OpenStatus:
        return False
    else:    
        return True

def get_PRInfo_data(PID):
    '''
    查詢指定程式選單資料
    '''

    return T_PIS.query.filter_by(PID = PID).all()

def get_all_PRInfo(PID,TageName):
    '''
    產生查詢指定程式選單資料清單
    '''

    select_PRInfo = T_PIS.query.filter_by(PID = PID,TageName=TageName).order_by(T_PIS.index.asc()).all()
    
    list_PRinfo_set = list()

    for read_row in select_PRInfo:

        temp_dict = dict()
         
        temp_dict['Bid'] = read_row.Bid
        temp_dict['Value'] = read_row.Value
        
        list_PRinfo_set.append(temp_dict)

    # print("[get_all_PRInfo] TageName: {}".format(list_PRinfo_set))

    return list_PRinfo_set

def get_Program_CaseQty(ProgramsName):
    
    return T_PCQ.query.filter_by(ProgramsName=ProgramsName).first().quantity

@app.before_request
def before_request():
    g.user = current_user

# https://stackoverflow.com/questions/34795798/flask-sqlalchemy-user-query-basequery-object-has-no-attribute-password
@login_manager.user_loader
def load_user(UserID):  # 取得當前登入者的帳戶編號(UserID)
    return T_USER.query.filter_by(UserID=UserID).first()

# 碰到帳戶授權失效情況處理，會自動轉載到請求登入頁面
@login_manager.unauthorized_handler
def unauthorized():
    # # 初始化URL List
    # list_URL = initialize_URL()
    return render_template('page_relogin.html',Http_Title=login_page_title)
    # return "帳戶登入授權失效，請在重新進行登入. <p> <a href='{}'>click come to login</a> </p>".format(url_for('login'))
'''-------------------------------------------------------------------'''

'''
----------------------------------------------------------------------
Flask-admin views initialize
----------------------------------------------------------------------
'''
from Module.Flask_Admin.AdminView import AdminView
from Module.Flask_Admin.ModelView import AdminModelView
from Module.Flask_Admin.ModelView import Custom_TDPModelView
from Module.Flask_Admin.ModelView import Custom_TSTModelView
from Module.Flask_Admin.ModelView import Custom_TUSERModelView
from Module.Flask_Admin.ModelView import Custom_TSPModelView
from Module.Flask_Admin.ModelView import Custom_TSLModelView
from Module.Flask_Admin.ModelView import Custom_TPISModelView
from Module.Flask_Admin.ModelView import Custom_TPCQModelView
from Module.Flask_Admin.ModelView import Custom_T_RSTModelView
from Module.Flask_Admin.ModelView import Custom_T_RSPModelView
from Module.Flask_Admin.ModelView import Custom_T_SPOModelView
# Add administrative views here
admin = Admin(app=app, index_view= AdminView(), name='Ikea RS System DBM', template_mode="bootstrap3") # Flask-admin init_app()
admin.add_link(MenuLink(name='Logout', category='', url="/logout")) # 在Menu之中加入登出按鈕Link
admin.add_view(Custom_TDPModelView(T_DP, db.session,name="部門")) # 在Flask-Admin 加入部門(Department)-ModelView
admin.add_view(Custom_TUSERModelView(T_USER, db.session,name="帳戶")) # 在Flask-Admin 加入帳戶權限(UserAuthority)-ModelView
admin.add_view(Custom_TSTModelView(T_ST, db.session,name="分店")) # 在Flask-Admin 加入SYS_Store-ModelView
admin.add_view(Custom_TSPModelView(T_SP, db.session,name="程式模組")) # 在Flask-Admin 加入SYS_Programs-ModelView
admin.add_view(Custom_T_SPOModelView(T_SPO, db.session,name="程式模組啟用")) # 在Flask-Admin 加入SYS_Programs_OpenStatus
admin.add_view(Custom_TPISModelView(T_PIS, db.session,name="程式模組下拉選單")) # 在Flask-Admin 加入PR_InformationSetting-ModelView
admin.add_view(Custom_TPCQModelView(T_PCQ, db.session,name="程式模組紀錄筆數")) # 在Flask-Admin 加入PR_CaseQuantity-ModelView
admin.add_view(Custom_T_RSTModelView(T_RST, db.session,name="Report_SQL Type選單")) # 在Flask-Admin 加入Report_SQL_SQLTYPE-ModelView
admin.add_view(Custom_T_RSPModelView(T_RSP, db.session,name="Report_SQL Program選單")) # 在Flask-Admin 加入Report_SQL_Program-ModelView
admin.add_view(Custom_TSLModelView(T_SL, db.session,name="系統紀錄")) # 在Flask-Admin 加入SYS_System_Log-ModelView
'''-------------------------------------------------------------------'''

# time format settings
time_format = time_format_config['time_format']
# time_format_ckupload_img = time_format_config['time_format_ckupload_img']

# print("time_format : {}".format(time_format))
# print("time_format_m_id : {}".format(time_format_m_id))
# print("time_format_ckupload_img : {}".format(time_format_ckupload_img))

# Create Ckeditor Instance && Initialize 
ckeditor = CKEditor()
ckeditor.init_app(app)

# 設定專案預設編碼格式
codecs.register(lambda name: codecs.lookup(
    'utf8') if name == 'utf8mb4' else None)


# 設置上傳檔案類型控制
# http://flask.pocoo.org/docs/1.0/patterns/fileuploads/
ALLOWED_IMAGE_EXTENSIONS = allow_file_config['ALLOWED_IMAGE_EXTENSIONS']
ALLOWED_File_EXTENSIONS = allow_file_config['ALLOWED_File_EXTENSIONS']
# print("ALLOWED_IMAGE_EXTENSIONS : {}".format(ALLOWED_IMAGE_EXTENSIONS))
# print("ALLOWED_File_EXTENSIONS : {}".format(ALLOWED_File_EXTENSIONS))


'''
----------------------------------------------------------------------
Datatables實作區塊 
----------------------------------------------------------------------
'''
@app.route('/get_user_datatable', methods=['GET', 'POST'])
@login_required
def get_user_datatable():  # 帳戶管理瀏覽清單Datatables呼叫請求資料

    # 取得網頁URL位址參數
    get_web_arg_store_id = request.args.get('StoreID')  # 所屬分店
    get_web_arg_filter = request.args.get('filter')  # 所屬部門編號

    # Datatables Server-side processing
    # https://datatables.net/manual/server-side#Returned-data
    '''取得當前datatables透過Ajax回傳的計數，用來做後端回傳資料驗證'''
    get_datatables_verifyCounter = request.form.get('draw')
    '''取得當前datatables透過Ajax回傳的頁面顯示筆數，用來做取查詢結果取出資料筆數'''
    get_showDataLength = request.form.get('length')
    '''
    取得當前datatables透過Ajax回傳的資料取用的開始位置，用來做取查詢結果取出資料位置起始值
    Datatables 回傳的start參數起始值是從0開始
    '''
    get_startDataPosition = request.form.get('start')

    # ''' 取得當前Datatables Search欄位值 '''
    # get_search_value = request.form.get('search[value]') 
    # print("[get_user_datatable] search: {}".format(get_search_value))

    json_result = jsonify(dict())

    if request.method == 'POST':

        json_result = Admin_Datatable.gen_userlist_tabledata(
            T_USER=T_USER,
            T_DP=T_DP,
            filter=get_web_arg_filter,
            get_datatables_verifyCounter=get_datatables_verifyCounter,
            get_showDataLength=get_showDataLength,
            get_startDataPosition=get_startDataPosition,
            UserID=session["UserID"],
            StoreID=get_web_arg_store_id,
            UserName=session['UserNameEn'],
            DPID=session['DPID']
        )

    return json_result

@app.route('/get_auth_datatable', methods=['GET', 'POST'])
@login_required
def get_auth_datatable():  # 系統權限瀏覽清單Datatables呼叫請求資料

    # 取得網頁URL位址參數
    get_web_arg_EU = request.args.get('EU')  # 被編輯帳戶ID

    json_result = jsonify(dict())

    if request.method == 'POST':

        json_result = Admin_Datatable.gen_authlist_tabledata(
            T_SA=T_SA,
            T_SP=T_SP,
            UserID=get_web_arg_EU
        )

    return json_result

@app.route('/get_casy_datatable', methods=['GET', 'POST'])
@login_required
def get_casy_datatable():  # CASY瀏覽清單Datatables呼叫請求資料

    # 取得網頁URL位址參數
    get_web_arg_filter = request.args.get('filter')
    get_web_arg_filter_input1 = request.args.get('filter_input1')
    get_web_arg_filter_input2 = request.args.get('filter_input2')
    get_web_arg_filter_input3 = request.args.get('filter_input3')
    get_web_arg_filter_input4 = request.args.get('filter_input4')
    get_web_arg_P_name = request.args.get('P_name')
   
    json_result = jsonify(dict())

    # print("[get_casy_datatable] get_web_arg_filter: {}, get_web_arg_filter_input1: {} , get_web_arg_filter_input2: {}, get_web_arg_filter_input3: {}, get_web_arg_filter_input4: {}".format(
    #     get_web_arg_filter,
    #     get_web_arg_filter_input1,
    #     get_web_arg_filter_input2,
    #     get_web_arg_filter_input3,
    #     get_web_arg_filter_input4
    # ))

    if request.method == 'POST': 

        data_list = list()
        # BaseOnStoreDepartment=""

        # if str(get_web_arg_filter) != "0":                    

        #     BaseOnStoreDepartment=(get_PRInfo_data(PID=get_web_arg_filter).Value)  

        json_result = Casy_Datatable.gen_casylist_tabledata(
            T_ST=T_ST,
            T_CCI=T_CCI,
            T_PIS=T_PIS,
            filter=get_web_arg_filter,
            filter_input1=get_web_arg_filter_input1,
            filter_input2=get_web_arg_filter_input2,
            filter_input3=get_web_arg_filter_input3,
            filter_input4=get_web_arg_filter_input4,
            P_name=get_web_arg_P_name,
            PID=get_programs_list(ProgramsName=get_web_arg_P_name).PID,
            StoreID=session["StoreID"],
            UserID=session["UserID"],
            UserName = session['UserNameEn'],
        )

    return json_result

@app.route('/get_casy_productInfo_datatable', methods=['GET', 'POST'])
@login_required
def get_casy_productInfo_datatable():  # CASY瀏覽清單Datatables呼叫請求資料

    # 取得網頁URL位址參數
    get_web_arg_InStoreCaseNo = request.args.get('InStoreCaseNo')
    get_web_arg_P_name = request.args.get('P_name')

    json_result = jsonify(dict())

    if request.method == 'POST':

        json_result = Casy_Datatable.gen_productinfolist_tabledata(
            T_CPI=T_CPI,
            InStoreCaseNo=get_web_arg_InStoreCaseNo,
            P_name=get_web_arg_P_name,
            UserID=session["UserID"],
            UserName = session['UserNameEn'],
            sub_name="CASY_ProductInformation"
        )

    return json_result

@app.route('/get_casy_locationInfor_datatable', methods=['GET', 'POST'])
@login_required
def get_casy_locationInfor_datatable():  # CASY瀏覽清單Datatables呼叫請求資料

    # 取得網頁URL位址參數
    get_web_arg_InStoreCaseNo = request.args.get('InStoreCaseNo')
    get_web_arg_ProductsInformationNO = request.args.get('ProductsInformationNO')
    get_web_arg_P_name = request.args.get('P_name')

    json_result = jsonify(dict())

    if request.method == 'POST':

        json_result = Casy_Datatable.gen_locationinforlist_tabledata(
            T_CLI=T_CLI,
            ProductsInformationNO=get_web_arg_ProductsInformationNO,
            InStoreCaseNo=get_web_arg_InStoreCaseNo,
            P_name=get_web_arg_P_name,
            UserID=session["UserID"],
            UserName = session['UserNameEn'],
            sub_name="CASY_LocationInformation"
        )

    return json_result

@app.route('/get_casy_ActionInfor_datatable', methods=['GET', 'POST'])
@login_required
def get_casy_ActionInfor_datatable():  # CASY瀏覽清單Datatables呼叫請求資料

    # 取得網頁URL位址參數
    get_web_arg_InStoreCaseNo = request.args.get('InStoreCaseNo')
    get_web_arg_ProductsInformationNO = request.args.get('ProductsInformationNO')
    get_web_arg_ProductsLocationNo = request.args.get('ProductsLocationNo')
    get_web_arg_P_name = request.args.get('P_name')

    json_result = jsonify(dict())

    if request.method == 'POST':

        json_result = Casy_Datatable.gen_actioninforlist_tabledata(
            T_CAI=T_CAI,
            ProductsInformationNO=get_web_arg_ProductsInformationNO,
            InStoreCaseNo=get_web_arg_InStoreCaseNo,
            ProductsLocationNo=get_web_arg_ProductsLocationNo,
            P_name=get_web_arg_P_name,
            UserID=session["UserID"],
            UserName = session['UserNameEn'],
            sub_name="CASY_ActionInformation"
        )

    return json_result


@app.route('/get_report_sql_datatable', methods=['GET', 'POST'])
@login_required
def get_report_sql_datatable():  # Report_SQL瀏覽清單Datatables呼叫請求資料

    # 取得網頁URL位址參數
    get_web_arg_filter_all = request.args.get('filter_all')
    # get_web_arg_filter_StoreID = request.args.get('filter_StoreID')
    get_web_arg_filter_Program = request.args.get('filter_Program')
    get_web_arg_filter_SQLTYPE = request.args.get('filter_SQLTYPE')

    json_result = jsonify(dict())

    print("[get_casy_datatable] get_web_arg_filter_all: {}, get_web_arg_filter_Program：{}, get_web_arg_filter_SQLTYPE：{}".format(
        get_web_arg_filter_all,
        get_web_arg_filter_Program,
        get_web_arg_filter_SQLTYPE,
    ))

    if request.method == 'POST': 

        json_result = Report_SQL.get_report_sql_datatable(
            filter_all = get_web_arg_filter_all, 
            StoreID = session['StoreID'], 
            filter_Program = get_web_arg_filter_Program, 
            filter_SQLTYPE = get_web_arg_filter_SQLTYPE,
            UserID = session["UserID"],
            UserName = session["UserNameEn"]
        )

    return json_result

'''-------------------------------------------------------------------'''

'''
----------------------------------------------------------------------
網站頁面-404 Not Found實作區塊 
----------------------------------------------------------------------
'''
@app.errorhandler(404)
def page_not_found(e): # 404 Not Found頁面
    return render_template('NotFound404.html'), 404
'''-------------------------------------------------------------------'''


'''
----------------------------------------------------------------------
pyecharts dashboard 實作區塊 
----------------------------------------------------------------------
'''
@app.route("/barChart", methods=['GET'])
def get_bar_chart() -> Bar:

    # pyecharts demo
    ec = (
        Bar()
        .add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "裙子"])
        .add_yaxis("商家A", [randrange(0, 100) for _ in range(6)])
        .add_yaxis("商家B", [randrange(0, 100) for _ in range(6)])
        .set_global_opts(title_opts=opts.TitleOpts(title="Bar-基本範例", subtitle="我是副標题"))
    )

    return ec.dump_options_with_quotes()

'''-------------------------------------------------------------------'''


'''
----------------------------------------------------------------------
系統頁面-index實作區塊 
----------------------------------------------------------------------
'''
@app.route("/", methods=['GET', 'POST'])
@login_required
def index():  # 系統首頁

    # 驗證登入狀態是否異常
    verify_login_status()

    # 頁面名稱
    page_name = "/"
  
    # 驗證該網站頁面是否開放
    is_Unable = check_unable_page("index")

    # 驗證使用者程式使用權限
    list_programs_authority = check_programs_authority()

    # 初始化URL List
    list_URL = initialize_URL()

    return render_template('index.html', UserID = session['UserID'], UserName = session['UserNameEn'],
        DPID = session['DPID'], DpName = session['DpName'], UserNameCh = session['UserNameCh'], store_name = session['StoreNO'],
        role_rank = session['RoleRank'], StoreNameC = session['StoreNameC'], StoreID = session['StoreID'], 
        list_URL=list_URL,
        list_programs_authority = list_programs_authority,
        is_Unable = is_Unable,     
    )
'''-------------------------------------------------------------------'''

'''
----------------------------------------------------------------------
系統頁面-addUser 新增使用者頁面 實作區塊 
----------------------------------------------------------------------
'''
@app.route("/addUser", methods=['GET', 'POST'])
@login_required
def addUser():  # 新增使用者頁面

    # 驗證登入狀態是否異常
    verify_login_status()

    # 頁面名稱
    page_name = "/addUser"
  
    # 驗證該網站頁面是否開放
    is_Unable = check_unable_page("addUser")

    # 驗證使用者程式使用權限
    list_programs_authority = check_programs_authority()

    # 初始化URL List
    list_URL = initialize_URL()

    ''' 產生查詢部門資訊選項資料 '''
    list_DP = get_DP_list(session['StoreID'])

    ''' ---------------------------------------------------------------------- '''

    ''' 實作AJAX請求處理 '''
    if request.method == 'POST':

        # 獲取json數據
        data = request.get_json(force=True)
        get_js_action = data['action']

        # print("[addUser] data: {}".format(data))

        if get_js_action == 'adduser': # 判斷是否為執行增加使用者帳戶狀態
            
            add__staus = True
            add_err_log = "None"

            get_js_DP = data['DP']
            get_js_UserNameEn = data['UserNameEn']
            get_js_UserNameCh = data['UserNameCh']
            get_js_UserID = data['UserID']
            get_js_Password = data['Password']

            print("[addUser] New User DP:{} , UserNameEn:{} , UserNameCh:{} , UserID:{} , ".format(
                get_js_DP,
                get_js_UserNameEn,
                get_js_UserNameCh,
                get_js_UserID,
            ))

            # 判斷長度
            if len(get_js_DP) == 0:
                add__staus = False
                add_err_log += "未選擇部門分類"

            # 判斷長度
            if len(get_js_UserNameEn) == 0:
                add__staus = False
                add_err_log += "未輸入帳戶英文姓名"

            # 判斷長度
            if len(get_js_UserNameCh) == 0:
                add__staus = False
                add_err_log += "未輸入帳戶中文姓名"

            # 判斷長度
            if len(get_js_UserID) == 0:
                add__staus = False
                add_err_log += "未輸入帳戶編號"

            # 判斷長度
            if len(get_js_Password) == 0:
                add__staus = False
                add_err_log += "未輸入帳戶密碼"

            # 判斷上列檢查條件是否都不成立，如果都不成立 add__staus 會等於True
            if add__staus == True:

                get_curtime = get_current_datetime() # 取得當前系統時間(年 月 日 時 分 秒)
                
                # 新增記錄進去使用者資料表(SYS_User)
                db.session.add(
                    T_USER(
                        UserID = get_js_UserID,
                        StoreID = session['StoreID'],
                        DPID = get_js_DP,
                        UserNameEn = get_js_UserNameEn,
                        UserNameCh = get_js_UserNameCh,
                        Password = get_js_Password,
                        ActivationStatus = False,
                        RoleRank = "User",
                        CreateDate = get_curtime
                    )                    
                )

                for read_row in get_all_Programs_data():
                    # 新增使用者預設程式權限Data,全都預設無權限
                    db.session.add(
                        T_SA(
                            UserID = get_js_UserID,
                            PID = read_row.PID,
                            Run = False,
                            Append = False,
                            Edit = False,
                            Report = False
                        )
                    )       

                # 確認寫入DB
                db.session.commit()

                return jsonify(dict(redirect = list_URL['usermanage'], add__staus = add__staus , add_err_log=add_err_log))
    ''' ---------------------------------------------------------------------- '''
   
    return render_template('admin/signup.html', UserID = session['UserID'], UserName = session['UserNameEn'],
        DPID = session['DPID'], DpName = session['DpName'], UserNameCh = session['UserNameCh'], store_name = session['StoreNO'],
        role_rank = session['RoleRank'], StoreNameC = session['StoreNameC'], StoreID = session['StoreID'],
        page_name = page_name,
        list_URL=list_URL,
        list_DP = list_DP,
        list_programs_authority = list_programs_authority,
        is_Unable = is_Unable,        
    )
'''-------------------------------------------------------------------'''

'''
----------------------------------------------------------------------
帳戶管理瀏覽清單頁面-usermanage實作區塊 
----------------------------------------------------------------------
'''
@app.route("/usermanage", methods=['GET', 'POST'])
@login_required
def usermanage():  # 帳戶管理瀏覽清單頁面

    # 驗證登入狀態是否異常
    verify_login_status()

    # 頁面名稱
    page_name = "/usermanage"
  
    # 驗證該網站頁面是否開放
    is_Unable = check_unable_page("usermanage")

    # 驗證使用者程式使用權限
    list_programs_authority = check_programs_authority()

    # 初始化URL List
    list_URL = initialize_URL()

    ''' 產生查詢部門資訊選項資料 '''
    list_DP = get_DP_list(session['StoreID'])

    ''' 實作AJAX請求處理 '''
    if request.method == 'POST':

        # 獲取json數據
        data = request.get_json(force=True)
        get_js_action = data['action']

        # print("[usermanage] data: {}".format(data))

        if get_js_action == 'deluser': # 判斷是否為執行刪除使用者帳戶狀態
            
            del_staus = True
            err_log = "None"

            get_js_delUserID = data['delUserID']

            # 查詢UserID是否存在
            check_User_exists = T_USER.query.filter_by(UserID=get_js_delUserID).count()
            
            # 判斷查詢結果
            if check_User_exists == 0 :

                del_staus = False
                err_log = "該位使用者ID並不存在，請重新載入頁面確認資料更新，如果還是存在有問題，請聯絡系統管理員。"
                print("[usermanage]Error msg: Delete User is faild. The UserID [{}] is not exists.".format(get_js_delUserID))

            # 判斷是否要執行假刪除
            if del_staus:

                # 查詢UserID資訊
                select_User_info = T_USER.query.filter_by(UserID=get_js_delUserID).first()

                print("[usermanage] Delete UserID:{} , UserName:{}({}) , StoreID:{}  {}".format(
                    select_User_info.get_id(),
                    select_User_info.UserNameEn,
                    select_User_info.UserNameCh,
                    select_User_info.StoreID,
                    get_current_datetime()
                ))

                # 停用該帳戶
                select_User_info.ActivationStatus = False

                # select_User_Authority = T_SA.query.filter_by(UserID=select_User_info.get_id()).all()

                # 刪除該User權限
                # db.session.delete(select_User_Authority)

                # if  T_CCI.query.filter_by(UserID=select_User_info.get_id()).count() != 0:
                #     pass

                # 刪除該User資訊
                # db.session.delete(select_User_info)

                # 進行commit DB
                db.session.commit()

            return jsonify(dict(redirect = list_URL['usermanage'], del_staus = del_staus , err_log=err_log))
    ''' ---------------------------------------------------------------------- '''

    return render_template('admin/admin_usermanage.html', UserID = session['UserID'], UserName = session['UserNameEn'],
        DPID = session['DPID'], DpName = session['DpName'], UserNameCh = session['UserNameCh'], store_name = session['StoreNO'],
        role_rank = session['RoleRank'], StoreNameC = session['StoreNameC'], StoreID = session['StoreID'], 
        page_name = page_name,
        list_URL=list_URL,
        list_DP=list_DP,
        list_programs_authority = list_programs_authority,
        is_Unable = is_Unable,
    )

'''-------------------------------------------------------------------'''

'''
----------------------------------------------------------------------
帳戶管理編輯設定頁面-edituser實作區塊
----------------------------------------------------------------------
'''
@app.route("/edituser", methods=['GET', 'POST'])
@login_required
def edituser():  # 帳戶管理編輯設定頁面

    # 驗證登入狀態是否異常
    verify_login_status()

    # 頁面名稱
    page_name = "/edituser"
  
    # 驗證該網站頁面是否開放
    is_Unable = check_unable_page("edituser")

    # 驗證使用者程式使用權限
    list_programs_authority = check_programs_authority()

    # 初始化URL List
    list_URL = initialize_URL()

    # 取得網頁URL位址參數
    get_web_arg_EU = request.args.get('EU')  # 取得被編輯帳戶ID

    # print("[edituser] EU: {}".format(get_web_arg_EU))

    log_class = "No Class"
    log_content = ""
    log_is_add = False

    ''' 產生查詢被編輯帳戶資料 '''
    select_EU_data = T_USER.query.filter_by(UserID=get_web_arg_EU).first()

    # 被編輯帳戶-帳戶英文姓名
    EU_UserNameEn = select_EU_data.UserNameEn

    # 被編輯帳戶-帳戶中文姓名
    EU_UserNameCh = select_EU_data.UserNameCh

    # 被編輯帳戶-啟用狀態
    EU_ActivationStatus = select_EU_data.ActivationStatus

    # 被編輯帳戶-部門ID資訊
    EU_DPID = select_EU_data.DPID

    # 被編輯帳戶-部門名稱資訊
    EU_DpName = T_DP.query.filter_by(DPID=EU_DPID,StoreID = select_EU_data.StoreID).first().DpName

    # 被編輯帳戶-密碼
    EU_Password = select_EU_data.Password

    # 被編輯帳戶-密碼
    EU_Update = select_EU_data.Update
    
    ''' 產生查詢部門資訊選項資料 '''
    list_DP = get_DP_list(session['StoreID'])   
    
    ''' 實作AJAX請求處理 '''
    if request.method == 'POST':

        run_status = True
        auth_change = False
        err_log = "None"

        # 獲取json數據
        data = request.get_json(force=True)
        get_js_action = data['action']

        if get_js_action == 'edituser': # 判斷是否為修改使用者帳戶狀態
            
            log_class = log_class_list[page_name]
            get_js_DP = data['DP']
            get_js_UserNameEn = data['UserNameEn']
            get_js_UserNameCh = data['UserNameCh']
            get_js_Password = data['Password']
            get_js_EUID = data['EUID']
            get_js_auth = data['auth']
            get_js_enable = data['enable_status']

            print("[edituser] Edit User , UserID: {} , ".format(
                get_js_EUID,
            ))

            # print("[edituser] get_js_auth: {} , ".format(
            #     get_js_auth,
            # ))

            # 判斷是否無值
            run_log, run_status = DataProcess.check_data_null(
                {
                    "UserNameEn":get_js_UserNameEn,
                    "UserNameCh":get_js_UserNameCh,
                    "Password":get_js_Password,
                }
            )

            err_log += run_log
            
            # 判斷上列檢查條件是否都不成立，如果都不成立 run__staus 會等於True
            if run_status:

                get_curtime = get_current_datetime() # 取得當前系統時間(年 月 日 時 分 秒)

                edit_status = False

                # 查詢UserID資訊
                select_User_info = T_USER.query.filter_by(UserID=get_js_EUID).first()

                # 檢查帳戶英文姓名是否不一樣
                if DataProcess.check_data_NoEqual(select_User_info.UserNameEn, get_js_UserNameEn):
                    print("[edituser] Edit User , UserID: {} ,  UserNameEn: {} --> [{}]".format(
                        get_js_EUID,
                        select_User_info.UserNameEn,
                        get_js_UserNameEn
                    ))

                    edit_status = True

                    log_content += "UserNameEn: {} --> [{}] , " .format(
                        select_User_info.UserNameEn,
                        get_js_UserNameEn
                    )

                    select_User_info.UserNameEn = get_js_UserNameEn                             

                # 檢查帳戶中文姓名是否不一樣
                if DataProcess.check_data_NoEqual(select_User_info.UserNameCh, get_js_UserNameCh):
                    print("[edituser] Edit User , UserID: {} ,  UserNameCh: {} --> [{}]".format(
                        get_js_EUID,
                        select_User_info.UserNameCh,
                        get_js_UserNameCh
                    ))
                    edit_status = True
                    log_content += "UserNameCh: {} --> [{}] , " .format(
                        select_User_info.UserNameCh,
                        get_js_UserNameCh
                    )   
                    select_User_info.UserNameCh = get_js_UserNameCh

                # 檢查帳戶密碼是否不一樣
                if DataProcess.check_data_NoEqual(select_User_info.Password, get_js_Password):
                    print("[edituser] Edit User , UserID: {} ,  Password: {} --> [{}]".format(
                        get_js_EUID,
                        select_User_info.Password,
                        get_js_Password
                    ))
                    edit_status = True
                    log_content += "Password: {} --> [{}] , " .format(
                        select_User_info.Password,
                        get_js_Password
                    )   
                    select_User_info.Password = get_js_Password
                
                # 檢查部門編號是否不一樣
                if DataProcess.check_data_NoEqual(str(select_User_info.DPID), str(get_js_DP)):
                    # print("get_js_DP type:{}".format(type(get_js_DP)))
                    print("[edituser] Edit User , UserID: {} ,  DPID: {} --> [{}]".format(
                        get_js_EUID,
                        select_User_info.DPID,
                        get_js_DP
                    ))
                    edit_status = True
                    log_content += "DPID: {} --> [{}] , " .format(
                        select_User_info.DPID,
                        get_js_DP
                    ) 
                    select_User_info.DPID = int(get_js_DP)
                
                # 檢查帳戶啟用狀態是否不一樣
                if DataProcess.check_data_NoEqual(select_User_info.ActivationStatus, get_js_enable):
                    print("[edituser] Edit User , UserID: {} ,  ActivationStatus: {} --> [{}]".format(
                        get_js_EUID,
                        select_User_info.ActivationStatus,
                        get_js_enable
                    ))
                    edit_status = True
                    log_content += "ActivationStatus: {} --> [{}] , ".format(
                        select_User_info.ActivationStatus,
                        get_js_enable
                    ) 
                    select_User_info.ActivationStatus = get_js_enable

                def check_auth(db,auth,Run,Append,Edit,Report):
                    '''
                    內建檢查帳戶授權資訊方法
                    '''

                    is_auth_edit = False
                    log_content = ""               

                    if db.Run != Run:
                        print("[edituser] Edit User , UserID: {} ,  auth: {} , Run: {} --> [{}]".format(
                            get_js_EUID,
                            auth,
                            db.Run,
                            Run
                        ))
                        is_auth_edit = True
                        log_content += "auth: {} , Run: {} --> [{}] , " .format(
                            auth,
                            db.Run,
                            Run
                        ) 
                        db.Run = Run

                    if db.Append != Append:
                        print("[edituser] Edit User , UserID: {} ,  auth: {} , Append: {} --> [{}]".format(
                            get_js_EUID,
                            auth,
                            db.Append,
                            Append
                        ))
                        is_auth_edit = True
                        log_content += "auth: {} , Append: {} --> [{}] , " .format(
                            auth,
                            db.Append,
                            Append
                        ) 
                        db.Append = Append

                    if db.Edit != Edit:
                        print("[edituser] Edit User , UserID: {} ,  auth: {} , Edit: {} --> [{}]".format(
                            get_js_EUID,
                            auth,
                            db.Edit,
                            Edit
                        ))
                        is_auth_edit = True
                        log_content += "auth: {} , Edit: {} --> [{}] , " .format(
                            auth,
                            db.Edit,
                            Edit
                        ) 
                        db.Edit = Edit

                    if db.Report != Report:
                        print("[edituser] Edit User , UserID: {} ,  auth: {} , Report: {}--> [{}]".format(
                            get_js_EUID,
                            auth,
                            db.Report,
                            Report
                        ))
                        is_auth_edit = True
                        log_content += "auth: {} , Report: {} --> [{}] , " .format(
                            auth,
                            db.Report,
                            Report
                        ) 
                        db.Report = Report
                    
                    # print("is_auth_edit: {}".format(is_auth_edit))

                    return is_auth_edit , log_content

                temp_auth_list = list()

                print("[edituser] {}".format(get_js_auth))

                # 讀取系統授權清單，檢查是否有做更改
                for read_auth in get_js_auth:

                    # 查詢指定程式授權資訊
                    select_auth_data = T_SA.query.filter_by(
                        UserID=select_User_info.UserID,
                        PID=(get_programs_list(ProgramsName=read_auth["SysName"]).PID)
                    ).first()

                    # print("[edituser] select_auth_data count: {}".format(
                    #     T_SA.query.filter_by(
                    #     UserID=select_User_info.UserID,
                    #     PID=(get_programs_list(ProgramsName=read_auth["SysName"]).PID)
                    #     ).count()
                    # ))
                    
                    #檢查權限是否有做更改
                    is_auth_edit , temp_log_content = check_auth(
                        select_auth_data,
                        get_programs_list(PID=select_auth_data.PID).ProgramsName,
                        read_auth['Run'],
                        read_auth['Append'],
                        read_auth['Edit'],
                        read_auth['Report']
                    )

                    if is_auth_edit:
                        log_content += temp_log_content
                        temp_auth_list.append(is_auth_edit)                            

                # print("auth_change: {}".format(auth_change))
                # print("edit_status: {}".format(edit_status))
                # print("{}".format(temp_auth_list))

                # 如果有任何系統權限有做更改，一定會存在一個True，代表要進行寫入動作
                if True in temp_auth_list:
                    # print("author is change.")
                    auth_change = True

                print("auth_change: {}".format(auth_change))

                if edit_status or auth_change: 
                    if  edit_status:
                        select_User_info.Update = get_curtime
                    db.session.commit()
                    log_is_add = True                    

            print("[edituser] get_curtime: {}".format(get_curtime))

            # 判斷是否需要寫入系統紀錄
            if log_is_add:
                Insert_SysLog(
                    UserID = session['UserID'],
                    UserNameEn = session['UserNameEn'],
                    UserNameCh = session['UserNameCh'],
                    StoreID = session['StoreID'],
                    StoreNO = session['StoreNO'],
                    DPID = session['DPID'],
                    DpName = session['DpName'],
                    PageName = page_name,
                    log_class = log_class,
                    log_content = log_content,
                    InertDate = get_curtime
                )               

            return jsonify(dict(redirect = url_for('edituser', UserID=session['UserID'], UserName=session['UserNameEn'],EU=get_web_arg_EU), run_stauts = run_status , err_log=err_log))

    ''' ---------------------------------------------------------------------- '''

    return render_template('admin/admin_edituser.html', UserID = session['UserID'], UserName = session['UserNameEn'],
        DPID = session['DPID'], DpName = session['DpName'], UserNameCh = session['UserNameCh'], store_name = session['StoreNO'],
        role_rank = session['RoleRank'], StoreNameC = session['StoreNameC'], StoreID = session['StoreID'], 
        page_name = page_name,
        list_URL=list_URL,
        list_DP=list_DP,
        list_programs_authority = list_programs_authority,
        is_Unable = is_Unable,
        EU_UserNameEn = EU_UserNameEn, EU_UserNameCh = EU_UserNameCh,
        EU_DPID = EU_DPID, EU_DpName = EU_DpName,
        EU_Password = EU_Password,EU_UserID = get_web_arg_EU,
        EU_ActivationStatus = EU_ActivationStatus, EU_Update= EU_Update,
    )
'''-------------------------------------------------------------------'''

'''
----------------------------------------------------------------------
CASE瀏覽清單頁面-caselist 
----------------------------------------------------------------------
'''
@app.route("/caselist/<string:P_name>", methods=['GET', 'POST'])
@login_required
def caselist(P_name):  # CASE瀏覽清單頁面

    # 驗證登入狀態是否異常
    verify_login_status()

    # 頁面名稱
    page_name = "/caselist"
  
    # 驗證該網站頁面是否開放
    is_Unable = get_Programs_OpenStatus(P_name)
    # is_Unable = check_unable_page("caselist")
    # print("P_name: {} , is_Unable: {}".format(P_name,is_Unable))

    # 驗證使用者程式使用權限
    list_programs_authority = check_programs_authority()

    # 初始化URL List
    list_URL = initialize_URL()

    # ''' 產生BaseOnStoreDepartment選項資料 '''
    # list_BaseOnStoreDepartment = get_all_PRInfo(PID=(get_programs_list(ProgramsName=P_name).PID),TageName="BaseOnStoreDepartment")
    
    ''' 產生Status選項資料 '''
    list_Status = get_all_PRInfo(PID=(get_programs_list(ProgramsName=P_name).PID),TageName="Status")
    
    ''' 取得目前該程式所屬html file 配置 '''
    html_file = str(get_programs_list(ProgramsName=P_name).list_html)

    # 產生 addcase連結參數
    caseadd_URL = get_programs_list(ProgramsName=P_name).add_URL

    return render_template(html_file, UserID = session['UserID'], UserName = session['UserNameEn'],
        DPID = session['DPID'], DpName = session['DpName'], UserNameCh = session['UserNameCh'], store_name = session['StoreNO'],
        role_rank = session['RoleRank'], StoreNameC = session['StoreNameC'], StoreID = session['StoreID'], 
        page_name = page_name, P_name = P_name, caseadd_URL = caseadd_URL,
        list_URL=list_URL,
        list_Status = list_Status,
        list_programs_authority = list_programs_authority,
        is_Unable = is_Unable,
    )
'''-------------------------------------------------------------------'''

'''
----------------------------------------------------------------------
CASE新增工單頁面-addcase實作區塊 
----------------------------------------------------------------------
'''
@app.route("/addcase/<string:P_name>", methods=['GET', 'POST'])
@login_required
def addcase(P_name):  # CASE新增工單頁面

    # 驗證登入狀態是否異常
    verify_login_status()

    # 頁面名稱
    page_name = "/addcase"
  
    # 驗證該網站頁面是否開放
    is_Unable = get_Programs_OpenStatus(P_name)

    # 驗證使用者程式使用權限
    list_programs_authority = check_programs_authority()

    # 初始化URL List
    list_URL = initialize_URL()

    ''' 產生BaseOnStoreDepartment選項資料 '''
    list_BaseOnStoreDepartment = get_all_PRInfo(PID=(get_programs_list(ProgramsName=P_name).PID),TageName="BaseOnStoreDepartment")

    ''' 產生BaseOn選項資料 '''
    list_BaseOn = get_all_PRInfo(PID=(get_programs_list(ProgramsName=P_name).PID),TageName="BaseOn")

    ''' 產生Defect選項資料 '''
    list_Defect = get_all_PRInfo(PID=(get_programs_list(ProgramsName=P_name).PID),TageName="Defect")

    ''' 取得目前該程式所屬html file 配置 '''
    html_file = str(get_programs_list(ProgramsName=P_name).add_html)

    # 產生 caselist URL連結
    caselist_URL = url_for("caselist",UserID = session['UserID'], UserName = session['UserNameEn'],P_name=P_name)

    # 初始化產生editcase URL連結實體
    editcase_URL = ""

    ''' 產生目前該程式Case統計數量資訊 '''
    quantity_total = get_Program_CaseQty(ProgramsName=P_name)

    #  取得資料庫程式實體
    db_T_SP = get_programs_list(ProgramsName=P_name)

    # Start Time 參數
    sys_start_time = datetime_format.get_current_datetime(time_format_config["casetime_format"])

    ''' 實作AJAX請求處理 '''
    if request.method == 'POST':

        # 獲取json數據
        data = request.get_json(force=True)

        if P_name == "CASY":

            # 調用 Module: Casy_Process - Insert_CaseInfo_Data
            run_staus, run_log ,get_FlowNum = Casy_Process.Insert_CaseInfo_Data(T_CCI,T_PCQ,T_PIS ,db_T_SP.PID ,session['UserID'],session['StoreID'],session['StoreNO'],data)
            # 產生caselist URL連結 - CASY
            redirect_URL = url_for("caselist",UserID=session['UserID'], UserName = session['UserNameEn'],P_name=P_name)
            # 產生editcase URL連結 - CASY
            editcase_URL = url_for("editcase", UserID=session['UserID'], UserName=session['UserNameEn'], InStoreCaseNo=get_FlowNum, P_name=P_name)
            return jsonify(dict(redirect = redirect_URL, run_staus = run_staus , run_log=run_log,editcase_URL=editcase_URL))

    return render_template(html_file, UserID = session['UserID'], UserName = session['UserNameEn'],
        DPID = session['DPID'], DpName = session['DpName'], UserNameCh = session['UserNameCh'], store_name = session['StoreNO'],
        role_rank = session['RoleRank'], StoreNameC = session['StoreNameC'], StoreID = session['StoreID'], 
        page_name = page_name, html_file = html_file, P_name=P_name, caselist_URL = caselist_URL,
        list_URL=list_URL,
        list_programs_authority = list_programs_authority,
        is_Unable = is_Unable,
        list_BaseOnStoreDepartment = list_BaseOnStoreDepartment,
        list_BaseOn = list_BaseOn,
        list_Defect = list_Defect,
        quantity_total = quantity_total,
        sys_start_time=sys_start_time,
    )

'''-------------------------------------------------------------------'''

'''
----------------------------------------------------------------------
CASE編輯工單頁面-editcase實作區塊 
----------------------------------------------------------------------
'''
@app.route("/editcase/<string:P_name>", methods=['GET', 'POST'])
@login_required
def editcase(P_name):  # CASE編輯工單頁面

    # 驗證登入狀態是否異常
    verify_login_status()

    # 頁面名稱
    page_name = "/editcase"
  
    # 驗證該網站頁面是否開放
    is_Unable = check_unable_page("editcase")

    # 初始化產生網頁URL位址參數實體
    get_web_arg_one = ""

    # 驗證使用者程式使用權限
    list_programs_authority = check_programs_authority()

    # 初始化URL List
    list_URL = initialize_URL()

    ''' 產生BaseOnStoreDepartment選項資料 '''
    list_BaseOnStoreDepartment = get_all_PRInfo(PID=(get_programs_list(ProgramsName=P_name).PID),TageName="BaseOnStoreDepartment")

    ''' 產生BaseOn選項資料 '''
    list_BaseOn = get_all_PRInfo(PID=(get_programs_list(ProgramsName=P_name).PID),TageName="BaseOn")

    ''' 產生Defect選項資料 '''
    list_Defect = get_all_PRInfo(PID=(get_programs_list(ProgramsName=P_name).PID),TageName="Defect")

    ''' 取得目前該程式所屬html file 配置 '''
    html_file = str(get_programs_list(ProgramsName=P_name).edit_html)

    # # 產生 caselist連結參數
    # caselist_URL = get_programs_list(ProgramsName=P_name).list_URL

    # 產生 caselist URL連結
    caselist_URL = url_for("caselist",UserID = session['UserID'], UserName = session['UserNameEn'],P_name=P_name)

    #  取得資料庫程式實體
    db_T_SP = get_programs_list(ProgramsName=P_name)
    # 初始化產生form_data實體
    form_data = dict()
    # 初始化產生editcase URL連結實體
    editcase_URL = ""
    # 初始化產生addcasesub URL連結實體
    addcasesub_url=""
        
    ''' 實作AJAX-POST請求處理 '''
    if request.method == 'POST':
        # 獲取json數據
        data = request.get_json(force=True)
        if P_name == "CASY": # 判斷目前程式頁面名稱
            # 調用 Module: Casy_Process - edit_CaseInfo_Data
            run_staus, run_log, Up_date, is_err,Case_Status = Casy_Process.edit_CaseInfo_Data(T_CCI,T_CPI, T_PIS, session['UserID'],session['StoreID'],data)            
            redirect_URL = caselist_URL
            return jsonify(dict(redirect = redirect_URL, run_staus = run_staus , run_log=run_log, Up_date=Up_date,is_err=is_err,Case_Status=Case_Status))
            
    ''' 實作AJAX-GET請求處理 '''
    if request.method == 'GET':
        if P_name == "CASY": # 判斷目前程式頁面名稱
            get_web_arg_one = request.args.get('InStoreCaseNo')
            # 調用 Module: Casy_Process - get_CaseInfo_Data
            # 產生 Form column value dictory - CASY_CaseInformation
            form_data = Casy_Process.get_CaseInfo_Data(T_CCI, T_CPI, T_PIS, db_T_SP.PID, get_web_arg_one)
            # 產生新增產品頁面連結 - CASY_ProductInformation
            addcasesub_url = url_for("addcasesub",UserID = session['UserID'], UserName = session['UserNameEn'],InStoreCaseNo=get_web_arg_one,P_name=P_name,sub_name="CASY_ProductInformation")

    return render_template(html_file, UserID = session['UserID'], UserName = session['UserNameEn'],
        DPID = session['DPID'], DpName = session['DpName'], UserNameCh = session['UserNameCh'], store_name = session['StoreNO'],
        role_rank = session['RoleRank'], StoreNameC = session['StoreNameC'], StoreID = session['StoreID'], 
        page_name = page_name, html_file = html_file, P_name=P_name, caselist_URL = caselist_URL,
        list_URL=list_URL,
        addcasesub_url=addcasesub_url,
        list_programs_authority = list_programs_authority,
        is_Unable = is_Unable,
        list_BaseOnStoreDepartment = list_BaseOnStoreDepartment,
        list_BaseOn = list_BaseOn,
        list_Defect = list_Defect,
        main_arg = get_web_arg_one,
        form_data=form_data,
    )
'''-------------------------------------------------------------------'''

'''
----------------------------------------------------------------------
CASE工單_新增Sub頁面-editcase實作區塊 
----------------------------------------------------------------------
'''
@app.route("/addcasesub/<string:P_name>/<string:sub_name>", methods=['GET', 'POST'])
@login_required
def addcasesub(P_name,sub_name):  # CASE工單新增Sub頁面

    # 驗證登入狀態是否異常
    verify_login_status()

    # 頁面名稱
    page_name = "/addcasesub"
  
    # 驗證該網站頁面是否開放
    is_Unable = check_unable_page("addcasesub")

    # 初始化產生網頁URL位址參數實體
    get_web_arg_one = ""
    get_web_arg_two = ""
    get_web_arg_three = ""
    get_web_arg_four = ""

    # 驗證使用者程式使用權限
    list_programs_authority = check_programs_authority()

    # 初始化URL List
    list_URL = initialize_URL()

    # Start Time 參數
    sys_start_time = datetime_format.get_current_datetime(time_format_config["casetime_format"])

    ''' 產生Defect選項資料 '''
    list_Defect = get_all_PRInfo(PID=(get_programs_list(ProgramsName=P_name).PID),TageName="Defect")

    ''' 產生StoreSuggest選項資料 '''
    list_StoreSuggest = get_all_PRInfo(PID=(get_programs_list(ProgramsName=P_name).PID),TageName="StoreSuggest")

    ''' 產生DecidedSuggest選項資料 '''
    list_DecidedSuggest = get_all_PRInfo(PID=(get_programs_list(ProgramsName=P_name).PID),TageName="DecidedSuggest")

    ''' 產生list_LocationType選項資料 '''
    list_LocationType = get_all_PRInfo(PID=(get_programs_list(ProgramsName=P_name).PID),TageName="LocationType")

    ''' 產生list_Action選項資料 '''
    list_Action = get_all_PRInfo(PID=(get_programs_list(ProgramsName=P_name).PID),TageName="Action")

    ''' 取得目前該程式所屬html file 配置 '''
    html_file = str(get_programs_list(ProgramsName=sub_name).add_html)
    
    # 產生 caselist URL連結
    caselist_URL = url_for("caselist",UserID = session['UserID'], UserName = session['UserNameEn'],P_name=P_name)
    # 初始化產生editcase URL連結實體
    editcase_URL = ""
    # 初始化 editcasesub URL連結
    editcasesub_URL =""
    # 初始化 editcasesub2 URL連結
    editcasesub2_URL =""

    # ''' 實作AJAX-GET請求處理 '''
    if request.method == 'GET':
        if P_name == "CASY":
            if sub_name == "CASY_ProductInformation": # 判斷目前程式底下子程式頁面名稱
                get_web_arg_one = request.args.get('InStoreCaseNo')
                # 產生editcasesub URL連結 - CASY
                editcase_URL = url_for("editcase",UserID = session['UserID'], UserName = session['UserNameEn'], InStoreCaseNo=get_web_arg_one, P_name=P_name)
            if sub_name == "CASY_LocationInformation": # 判斷目前程式底下子程式頁面名稱
                get_web_arg_one = request.args.get('InStoreCaseNo')
                get_web_arg_two = request.args.get('ProductsInformationNO')            
                # 產生editcase URL連結 - CASY
                editcase_URL = url_for("editcase",UserID = session['UserID'], UserName = session['UserNameEn'], InStoreCaseNo=get_web_arg_one, P_name=P_name)
                # 產生editcasesub URL連結 - CASY_ProductInformation           
                editcasesub_URL = url_for("editcasesub",UserID = session['UserID'], UserName = session['UserNameEn'], InStoreCaseNo=get_web_arg_one,ProductsInformationNO=get_web_arg_two, P_name=P_name,sub_name="CASY_ProductInformation")
            if sub_name == "CASY_ActionInformation": # 判斷目前程式底下子程式頁面名稱
                get_web_arg_one = request.args.get('InStoreCaseNo')
                get_web_arg_two = request.args.get('ProductsInformationNO')
                get_web_arg_three = request.args.get('ProductsLocationNo')
                # get_web_arg_four = request.args.get('InstoreActionNo')
                # 產生editcase URL連結 - CASY
                editcase_URL = url_for("editcase",UserID = session['UserID'], UserName = session['UserNameEn'], InStoreCaseNo=get_web_arg_one, P_name=P_name)
                # 產生editcasesub URL連結 - CASY_ProductInformation           
                editcasesub_URL = url_for("editcasesub",UserID = session['UserID'], UserName = session['UserNameEn'],InStoreCaseNo=get_web_arg_one,ProductsInformationNO=get_web_arg_two, P_name=P_name,sub_name="CASY_ProductInformation")
                # 產生editcasesub URL連結 - CASY_LocationInformation  
                editcasesub2_URL = url_for("editcasesub",UserID = session['UserID'], UserName = session['UserNameEn'], InStoreCaseNo=get_web_arg_one,ProductsInformationNO=get_web_arg_two,ProductsLocationNo=get_web_arg_three, P_name=P_name,sub_name="CASY_LocationInformation")

    ''' 實作AJAX-POST請求處理 '''
    if request.method == 'POST':
        # 獲取json數據
        data = request.get_json(force=True)
        # 判斷程式系統名稱
        if P_name == "CASY":            
            if sub_name == "CASY_ProductInformation": # 判斷目前程式底下子程式頁面名稱
                get_web_arg_one = request.args.get('InStoreCaseNo')
                # 調用 Module: Casy_Process - Insert_Product_Data
                run_staus, run_log = Casy_Process.Insert_Product_Data(T_CCI,T_CPI,T_PIS,get_web_arg_one,data)
                # 產生editcasesub URL連結
                editcasesub_URL = url_for("editcase",UserID = session['UserID'], UserName = session['UserNameEn'], InStoreCaseNo=get_web_arg_one, P_name=P_name)
                redirect_URL = editcasesub_URL
                return jsonify(dict(redirect = redirect_URL, run_staus = run_staus , run_log=run_log))
            if sub_name == "CASY_LocationInformation": # 判斷目前程式底下子程式頁面名稱
                get_web_arg_one = request.args.get('InStoreCaseNo')
                get_web_arg_two = request.args.get('ProductsInformationNO')
                # print("[addcasesub] InStoreCaseNo:{} ".format(get_web_arg_one))
                # 調用 Module: Casy_Process - Insert_Location_Data
                run_staus, run_log = Casy_Process.Insert_Location_Data(T_CLI, T_CPI, T_PIS,get_web_arg_two,data)
                # 產生editcasesub URL連結 - CASY_ProductInformation
                editcasesub_URL = url_for("editcasesub",UserID = session['UserID'], UserName = session['UserNameEn'],InStoreCaseNo=get_web_arg_one,ProductsInformationNO=get_web_arg_two, P_name=P_name,sub_name="CASY_ProductInformation")
                redirect_URL = editcasesub_URL
                # print("[addcasesub] redirect_URL:{} ".format(redirect_URL))
                return jsonify(dict(redirect = redirect_URL, run_staus = run_staus , run_log=run_log))
            if sub_name == "CASY_ActionInformation": # 判斷目前程式底下子程式頁面名稱
                get_web_arg_one = request.args.get('InStoreCaseNo')
                get_web_arg_two = request.args.get('ProductsInformationNO')
                get_web_arg_three = request.args.get('ProductsLocationNo')
                # 調用 Module: Casy_Process - Insert_Action_Data
                run_staus, run_log = Casy_Process.Insert_Action_Data(T_CAI, T_CLI, T_PIS, get_web_arg_two, get_web_arg_three,data)
                # 產生editcasesub URL連結 - CASY_LocationInformation  
                editcasesub2_URL = url_for("editcasesub",UserID = session['UserID'], UserName = session['UserNameEn'], InStoreCaseNo=get_web_arg_one,ProductsInformationNO=get_web_arg_two,ProductsLocationNo=get_web_arg_three, P_name=P_name,sub_name="CASY_LocationInformation")
                redirect_URL = editcasesub2_URL
                return jsonify(dict(redirect = redirect_URL, run_staus = run_staus , run_log=run_log))

    return render_template(html_file, UserID = session['UserID'], UserName = session['UserNameEn'],
        DPID = session['DPID'], DpName = session['DpName'], UserNameCh = session['UserNameCh'], store_name = session['StoreNO'],
        role_rank = session['RoleRank'], StoreNameC = session['StoreNameC'], StoreID = session['StoreID'], 
        page_name = page_name, html_file = html_file, P_name=P_name, sub_name=sub_name,
        list_URL=list_URL,
        editcase_URL=editcase_URL,
        editcasesub_URL=editcasesub_URL,
        editcasesub2_URL=editcasesub2_URL,
        caselist_URL=caselist_URL,
        list_programs_authority = list_programs_authority,
        is_Unable = is_Unable,
        list_Defect = list_Defect,
        list_StoreSuggest=list_StoreSuggest,
        list_DecidedSuggest=list_DecidedSuggest,
        list_LocationType=list_LocationType,
        list_Action=list_Action,
        main_arg = get_web_arg_one,
        sub_arg=get_web_arg_two,
        sub2_arg=get_web_arg_three,
        sys_start_time=sys_start_time,
    )

'''-------------------------------------------------------------------'''

'''
----------------------------------------------------------------------
CASE工單_修改Sub頁面-editcasesub實作區塊 
----------------------------------------------------------------------
'''
@app.route("/editcasesub/<string:P_name>/<string:sub_name>", methods=['GET', 'POST'])
@login_required
def editcasesub(P_name,sub_name):  # CASE工單_修改Sub頁面
    
    # 驗證登入狀態是否異常
    verify_login_status()

    # 頁面名稱
    page_name = "/editcasesub"
  
    # 驗證該網站頁面是否開放
    is_Unable = check_unable_page("editcasesub")

    # 初始化產生網頁URL位址參數實體
    get_web_arg_one = ""
    get_web_arg_two = ""
    get_web_arg_three = ""
    get_web_arg_four = ""

    # 驗證使用者程式使用權限
    list_programs_authority = check_programs_authority()

    # 初始化URL List
    list_URL = initialize_URL()

    ''' 產生Defect選項資料 '''
    list_Defect = get_all_PRInfo(PID=(get_programs_list(ProgramsName=P_name).PID),TageName="Defect")

    ''' 產生StoreSuggest選項資料 '''
    list_StoreSuggest = get_all_PRInfo(PID=(get_programs_list(ProgramsName=P_name).PID),TageName="StoreSuggest")

    ''' 產生DecidedSuggest選項資料 '''
    list_DecidedSuggest = get_all_PRInfo(PID=(get_programs_list(ProgramsName=P_name).PID),TageName="DecidedSuggest")

    ''' 產生list_LocationType選項資料 '''
    list_LocationType = get_all_PRInfo(PID=(get_programs_list(ProgramsName=P_name).PID),TageName="LocationType")

    ''' 產生list_Action選項資料 '''
    list_Action = get_all_PRInfo(PID=(get_programs_list(ProgramsName=P_name).PID),TageName="Action")

    ''' 取得目前該程式所屬html file 配置 '''
    html_file = str(get_programs_list(ProgramsName=sub_name).edit_html)

    #  取得資料庫程式實體
    db_T_SP = get_programs_list(ProgramsName=P_name)
    
    # 產生 caselist URL連結
    caselist_URL = url_for("caselist",UserID = session['UserID'], UserName = session['UserNameEn'],P_name=P_name)

    # 初始化產生editcase URL連結實體
    editcase_URL = ""
    # 初始化產生addcasesub URL連結實體
    addcasesub_URL=""
    # 初始化產生editcasesub URL連結實體
    editcasesub_URL=""
    # 初始化產生editcasesub2 URL連結實體
    editcasesub2_URL=""
    # 初始化產生form_data實體
    form_data = dict()

    ''' 實作AJAX-GET請求處理 '''
    if request.method == 'GET':
        if P_name == "CASY":  # 判斷目前程式頁面名稱        
            if sub_name == "CASY_ProductInformation": # 判斷目前程式底下子程式頁面名稱
                get_web_arg_one = request.args.get('InStoreCaseNo')
                get_web_arg_two = request.args.get('ProductsInformationNO')
                # 產生editcase URL連結
                editcase_URL = url_for("editcase",UserID = session['UserID'], UserName = session['UserNameEn'], InStoreCaseNo=get_web_arg_one, P_name=P_name)
                # 調用 Module: Casy_Process - get_ProductInfo_Data
                # 產生 Form column value dictory
                form_data = Casy_Process.get_ProductInfo_Data(T_CPI, T_CLI, T_PIS, db_T_SP.PID, get_web_arg_one,get_web_arg_two)
                # 產生addcasesub URL連結實體 - CASY_ActionInformation
                addcasesub_URL = url_for("addcasesub",UserID = session['UserID'], UserName = session['UserNameEn'],InStoreCaseNo=get_web_arg_one,ProductsInformationNO=get_web_arg_two,P_name=P_name,sub_name="CASY_LocationInformation")
            if sub_name == "CASY_LocationInformation": # 判斷目前程式底下子程式頁面名稱
                get_web_arg_one = request.args.get('InStoreCaseNo')
                get_web_arg_two = request.args.get('ProductsInformationNO')
                get_web_arg_three = request.args.get('ProductsLocationNo')
                # 產生editcase URL連結 - CASY
                editcase_URL = url_for("editcase",UserID = session['UserID'], UserName = session['UserNameEn'], InStoreCaseNo=get_web_arg_one, P_name=P_name)
                # 產生addcasesub URL連結實體 - CASY_ActionInformation
                addcasesub_URL = url_for("addcasesub",UserID = session['UserID'], UserName = session['UserNameEn'],InStoreCaseNo=get_web_arg_one,ProductsInformationNO=get_web_arg_two,ProductsLocationNo=get_web_arg_three,P_name=P_name,sub_name="CASY_ActionInformation")
                # 產生addcasesub URL連結實體 - CASY_ProductInformation
                editcasesub_URL = url_for("editcasesub",UserID = session['UserID'], UserName = session['UserNameEn'],InStoreCaseNo=get_web_arg_one,ProductsInformationNO=get_web_arg_two, P_name=P_name,sub_name="CASY_ProductInformation")
                # 調用 Module: Casy_Process - get_Location_Data
                # 產生 Form column value dictory
                form_data = Casy_Process.get_Location_Data(T_CLI, T_CAI, T_PIS, db_T_SP.PID,get_web_arg_three,get_web_arg_two)
            if sub_name == "CASY_ActionInformation": # 判斷目前程式底下子程式頁面名稱
                get_web_arg_one = request.args.get('InStoreCaseNo')
                get_web_arg_two = request.args.get('ProductsInformationNO')
                get_web_arg_three = request.args.get('ProductsLocationNo')
                get_web_arg_four = request.args.get('InstoreActionNo')
                # 產生editcase URL連結 - CASY
                editcase_URL = url_for("editcase",UserID = session['UserID'], UserName = session['UserNameEn'], InStoreCaseNo=get_web_arg_one, P_name=P_name)
                # 產生editcasesub URL連結 - CASY_ProductInformation           
                editcasesub_URL = url_for("editcasesub",UserID = session['UserID'], UserName = session['UserNameEn'],InStoreCaseNo=get_web_arg_one,ProductsInformationNO=get_web_arg_two, P_name=P_name,sub_name="CASY_ProductInformation")
                # 產生editcasesub2 URL連結 - CASY_LocationInformation  
                editcasesub2_URL = url_for("editcasesub",UserID = session['UserID'], UserName = session['UserNameEn'], InStoreCaseNo=get_web_arg_one,ProductsInformationNO=get_web_arg_two,ProductsLocationNo=get_web_arg_three, P_name=P_name,sub_name="CASY_LocationInformation")
                # 調用 Module: Casy_Process - get_Action_Data
                # 產生 Form column value dictory
                form_data = Casy_Process.get_Action_Data(T_CAI, T_PIS, db_T_SP.PID,get_web_arg_three,get_web_arg_four)

    ''' 實作AJAX-POST請求處理 '''
    if request.method == 'POST':
        # 獲取json數據
        data = request.get_json(force=True)
        if P_name == "CASY": # 判斷目前程式頁面名稱         
            if sub_name == "CASY_ProductInformation": # 判斷目前程式底下子程式頁面名稱
                get_web_arg_one = request.args.get('InStoreCaseNo')
                get_web_arg_two = request.args.get('ProductsInformationNO')
                # 調用 Module: Casy_Process - edit_ProductInfo_Data
                run_staus, run_log, Up_date,is_err,Case_Status = Casy_Process.edit_ProductInfo_Data(T_CPI,T_CLI, T_PIS, db_T_SP.PID,get_web_arg_one,get_web_arg_two,data)
                # 產生editcase URL連結
                editcase_URL = url_for("editcase",UserID = session['UserID'], UserName = session['UserNameEn'], InStoreCaseNo=get_web_arg_one, P_name=P_name)
                redirect_URL = editcase_URL
                return jsonify(dict(redirect = redirect_URL, run_staus = run_staus , run_log=run_log, Up_date=Up_date, is_err=is_err,Case_Status=Case_Status))
            if sub_name == "CASY_LocationInformation": # 判斷目前程式底下子程式頁面名稱
                get_web_arg_one = request.args.get('InStoreCaseNo')
                get_web_arg_two = request.args.get('ProductsInformationNO')
                get_web_arg_three = request.args.get('ProductsLocationNo')
                # 調用 Module: Casy_Process - edit_Location_Data
                run_staus, run_log, Up_date,is_err,Case_Status = Casy_Process.edit_Location_Data(T_CPI, T_CLI, T_CAI, T_PIS, db_T_SP.PID, get_web_arg_one, get_web_arg_two,get_web_arg_three,data)
                # 產生editcase URL連結 - CASY_ProductInformation
                editcasesub_URL = url_for("editcasesub",UserID = session['UserID'], UserName = session['UserNameEn'],InStoreCaseNo=get_web_arg_one,ProductsInformationNO=get_web_arg_two, P_name=P_name,sub_name="CASY_ProductInformation")
                redirect_URL = editcasesub_URL
                return jsonify(dict(redirect = redirect_URL, run_staus = run_staus , run_log=run_log, Up_date=Up_date, is_err=is_err,Case_Status=Case_Status))

            if sub_name == "CASY_ActionInformation": # 判斷目前程式底下子程式頁面名稱
                get_web_arg_one = request.args.get('InStoreCaseNo')
                get_web_arg_two = request.args.get('ProductsInformationNO')
                get_web_arg_three = request.args.get('ProductsLocationNo')
                get_web_arg_four = request.args.get('InstoreActionNo')
                # 調用 Module: Casy_Process - edit_Action_Data
                run_staus, run_log = Casy_Process.edit_Action_Data(T_CAI, T_CLI, T_PIS, db_T_SP.PID, get_web_arg_two, get_web_arg_three, get_web_arg_four,data)
                # 產生editcase URL連結 - CASY_ActionInformation
                editcasesub_URL = url_for("editcasesub",UserID = session['UserID'], UserName = session['UserNameEn'], InStoreCaseNo=get_web_arg_one,ProductsInformationNO=get_web_arg_two,ProductsLocationNo=get_web_arg_three, P_name=P_name,sub_name="CASY_LocationInformation")
                redirect_URL = editcasesub_URL
                return jsonify(dict(redirect = redirect_URL, run_staus = run_staus , run_log=run_log))

    return render_template(html_file, UserID = session['UserID'], UserName = session['UserNameEn'],
        DPID = session['DPID'], DpName = session['DpName'], UserNameCh = session['UserNameCh'], store_name = session['StoreNO'],
        role_rank = session['RoleRank'], StoreNameC = session['StoreNameC'], StoreID = session['StoreID'], 
        page_name = page_name, html_file = html_file, P_name=P_name, sub_name=sub_name,
        list_URL=list_URL,
        caselist_URL=caselist_URL,
        editcase_URL=editcase_URL,
        editcasesub_URL=editcasesub_URL,
        editcasesub2_URL=editcasesub2_URL,
        addcasesub_URL=addcasesub_URL,
        list_programs_authority = list_programs_authority,
        is_Unable = is_Unable,
        list_Defect = list_Defect,
        list_StoreSuggest=list_StoreSuggest,
        list_DecidedSuggest=list_DecidedSuggest,
        list_LocationType=list_LocationType,
        list_Action=list_Action,
        form_data=form_data,
        main_arg = get_web_arg_one,
        sub_arg = get_web_arg_two,
        sub2_arg = get_web_arg_three,
        sub3_arg=get_web_arg_four
    )
'''-------------------------------------------------------------------'''

'''
----------------------------------------------------------------------
Report 實作區塊 
----------------------------------------------------------------------
'''
@app.route("/report/<string:P_name>", methods=['GET', 'POST'])
@login_required
def report(P_name):

    # 驗證登入狀態是否異常
    verify_login_status()

    # 頁面名稱
    page_name = "/report"
  
    # 驗證該網站頁面是否開放
    is_Unable = get_Programs_OpenStatus(P_name)
    # print("P_name: {} , is_Unable: {}".format(P_name,is_Unable))

    # 驗證使用者程式使用權限
    list_programs_authority = check_programs_authority()

    # 初始化URL List
    list_URL = initialize_URL()

    ''' 取得目前該程式所屬html file 配置 '''
    html_file = str(get_programs_list(ProgramsName=P_name).report_html)

    # 產生 caselist URL連結
    caselist_URL = url_for("caselist",UserID = session['UserID'], UserName = session['UserNameEn'],P_name=P_name)

    # # 產生篩選條件按鈕清單
    # get_list_filter_option = Report.gen_filter_option(P_name=P_name)

    ''' 實作AJAX請求處理 '''
    if request.method == 'GET':
        # 取得ReportType選單內容
        list_report_type = Report.get_report_type_options(T_RS,P_name)

    ''' 實作AJAX請求處理 '''
    if request.method == 'POST':
        # 獲取json數據
        data = request.get_json(force=True) 
        # print("{}".format(data))      
        get_js_action = data['action']

        if get_js_action == 'Filter': # 判斷處理動作是否為條件查詢
            # 取得條件查詢結果
            run_staus, run_log, lsit_data, list_columns = Report.get_filter_data(
                schema=T_RS, schema2=T_ST, schema3=T_RSRR, data=data, UserID=session["UserID"], StoreID=session["StoreID"], 
                DPID = session["DPID"], DpName = session["DpName"], UserNameEn=session["UserNameEn"],
                UserNameCh = session["UserNameCh"] , STORE = session["StoreNameC"]
            )
            return jsonify(dict(run_staus = run_staus, run_log=run_log, lsit_data=lsit_data, list_columns=list_columns))

        # if get_js_action == 'Export': # 判斷處理動作是否為匯出報表
        #     pass

    return render_template(html_file, UserID = session['UserID'], UserName = session['UserNameEn'],
        DPID = session['DPID'], DpName = session['DpName'], UserNameCh = session['UserNameCh'], store_name = session['StoreNO'],
        role_rank = session['RoleRank'], StoreNameC = session['StoreNameC'], StoreID = session['StoreID'], 
        page_name = page_name, html_file = html_file, P_name=P_name,
        list_URL=list_URL,
        caselist_URL=caselist_URL,
        list_programs_authority = list_programs_authority,
        is_Unable = is_Unable,
        list_report_type=list_report_type
    )
'''-------------------------------------------------------------------'''

'''
----------------------------------------------------------------------
Add Report_SQl 實作區塊 
----------------------------------------------------------------------
'''
@app.route("/add_report_sql", methods=['GET', 'POST'])
@login_required
def add_report_sql():

    # 驗證登入狀態是否異常
    verify_login_status()

    # 頁面名稱
    page_name = "/add_report_sql"

    # 驗證該網站頁面是否開放
    is_Unable = check_unable_page("add_report_sql")

    # 驗證使用者程式使用權限
    list_programs_authority = check_programs_authority()

    # 初始化URL List
    list_URL = initialize_URL()

    ''' 取得目前該程式所屬html file 配置 '''
    html_file = str("Report/report_sql_addcase.html")

    # 初始化放置下拉選單-program
    list_program = list()
    # 初始化放置下拉選單-SQLtype
    list_SQLtype = list()

    ''' 實作AJAX請求處理 '''
    if request.method == 'POST':
        # 獲取json數據
        data = request.get_json(force=True)

        print("[add_report_sql] 新增一筆Report SQL紀錄")

        get_ps = get_programs_list(ProgramsName=data["Program"])    

        run_staus, run_log = Report_SQL.add_report_sql(
                                schema=T_RS, 
                                data=data,
                                StoreID=session["StoreID"],
                                STORE=session['StoreNameC'],
                                PID=get_ps.PID,
                                Program=get_ps.ProgramsName
                            )

        return jsonify(dict(run_staus = run_staus, run_log=run_log, redirect=list_URL["report_sql"]))
        
    ''' 實作AJAX請求處理 '''
    if request.method == 'GET':

        # 取得SQLTYPE選單內容
        list_SQLtype = Report_SQL.get_sqltype_options(T_ST)
        # 取得Program選單內容
        list_program = Report_SQL.get_program_options(T_RSP)  
 
    return render_template(html_file, UserID = session['UserID'], UserName = session['UserNameEn'],
        DPID = session['DPID'], DpName = session['DpName'], UserNameCh = session['UserNameCh'], store_name = session['StoreNO'],
        role_rank = session['RoleRank'], StoreNameC = session['StoreNameC'], StoreID = session['StoreID'], 
        page_name = page_name, html_file = html_file, list_programs_authority = list_programs_authority, is_Unable = is_Unable,
        list_URL = list_URL,list_program=list_program,list_SQLtype=list_SQLtype,
    )
'''-------------------------------------------------------------------'''

'''
----------------------------------------------------------------------
Edit Report_SQl 實作區塊 
----------------------------------------------------------------------
'''
@app.route("/edit_report_sql", methods=['GET', 'POST'])
@login_required
def edit_report_sql():  
    # 驗證登入狀態是否異常
    verify_login_status()

    # 頁面名稱
    page_name = "/edit_report_sql"

    # 驗證該網站頁面是否開放
    is_Unable = check_unable_page("edit_report_sql")

    # 驗證使用者程式使用權限
    list_programs_authority = check_programs_authority()

    # 初始化URL List
    list_URL = initialize_URL()

    # 初始化產生form_data實體
    form_data = dict()

    ''' 取得目前該程式所屬html file 配置 '''
    html_file = str("Report/report_sql_editcase.html")

    # 初始化放置下拉選單-program
    list_program = list()
    # 初始化放置下拉選單-SQLtype
    list_SQLtype = list()

    RID = 0

    ''' 實作AJAX請求處理 '''
    if request.method == 'POST':
        # 獲取網址參數
        get_web_arg_RID = request.args.get("RID")

        # 獲取json數據
        data = request.get_json(force=True)
        # print("{}".format(data))

        # 執行編輯作業
        run_staus, run_log, Up_date = Report_SQL.edit_report_sql(
            schema=T_RS, 
            data=data,
            StoreID=session["StoreID"],
            RID=int(get_web_arg_RID)
        )

        return jsonify(dict(run_staus = run_staus, run_log=run_log, Up_date=Up_date,  redirect=list_URL["report_sql"]))
          
    ''' 實作AJAX請求處理 '''
    if request.method == 'GET':
        # 獲取網址參數
        get_web_arg_RID = request.args.get("RID")
        RID = get_web_arg_RID
        # print("[edit_report_sql] get_web_arg_RID：{}".format(get_web_arg_RID))

        # 取得form data
        form_data = Report_SQL.get_report_sql_info(T_RS,int(get_web_arg_RID))       

        # 取得SQLTYPE選單內容
        list_SQLtype = Report_SQL.get_sqltype_options(T_ST)
        # 取得Program選單內容
        list_program = Report_SQL.get_program_options(T_RSP)  

    return render_template(html_file, UserID = session['UserID'], UserName = session['UserNameEn'],
        DPID = session['DPID'], DpName = session['DpName'], UserNameCh = session['UserNameCh'], store_name = session['StoreNO'],
        role_rank = session['RoleRank'], StoreNameC = session['StoreNameC'], StoreID = session['StoreID'], RID=RID,
        page_name = page_name, html_file = html_file, list_programs_authority = list_programs_authority, is_Unable = is_Unable,
        list_URL = list_URL,list_program=list_program,list_SQLtype=list_SQLtype,form_data=form_data,
    )

'''-------------------------------------------------------------------'''

'''
----------------------------------------------------------------------
Report_SQl 實作區塊 
----------------------------------------------------------------------
'''
@app.route("/report_sql", methods=['GET', 'POST', 'DELETE'])
@login_required
def report_sql():
    
    # 驗證登入狀態是否異常
    verify_login_status()

    # 頁面名稱
    page_name = "/report_sql"
  
    # 驗證該網站頁面是否開放
    is_Unable = check_unable_page("report_sql")

    # 驗證使用者程式使用權限
    list_programs_authority = check_programs_authority()

    # 初始化URL List
    list_URL = initialize_URL()

    ''' 取得目前該程式所屬html file 配置 '''
    html_file = str("Report/report_sql.html")

    # 初始化放置下拉選單-program
    list_program = list()
    # 初始化放置下拉選單-SQLtype
    list_SQLtype = list()

    ''' 實作AJAX請求處理 '''
    if request.method == 'POST':
        # 獲取json數據
        data = request.get_json(force=True)           

    ''' 實作AJAX請求處理 '''
    if request.method == 'GET':

        # 取得SQLTYPE選單內容
        list_SQLtype = Report_SQL.get_sqltype_options(T_ST)
        # 取得Program選單內容
        list_program = Report_SQL.get_program_options(T_RSP) 

    ''' 實作AJAX請求處理 '''
    if request.method == 'DELETE':
        # 獲取json數據
        data = request.get_json(force=True)
        # print("{}".format(data["RID"]))
        
        run_status, run_log = Report_SQL.del_record(data["RID"],session["StoreID"])
        return jsonify(dict(run_status=run_status, run_log=run_log))     

    return render_template(html_file, UserID = session['UserID'], UserName = session['UserNameEn'],
        DPID = session['DPID'], DpName = session['DpName'], UserNameCh = session['UserNameCh'], store_name = session['StoreNO'],
        role_rank = session['RoleRank'], StoreNameC = session['StoreNameC'], StoreID = session['StoreID'], 
        page_name = page_name, html_file = html_file, list_programs_authority = list_programs_authority, is_Unable = is_Unable,
        list_URL = list_URL,list_SQLtype=list_SQLtype,list_program=list_program
    )
'''-------------------------------------------------------------------'''

'''
----------------------------------------------------------------------
SQL_Test 實作區塊 
----------------------------------------------------------------------
'''
@app.route("/sql_test", methods=['GET', 'POST'])
@login_required
def sql_test():

    # 驗證登入狀態是否異常
    verify_login_status()

    # 頁面名稱
    page_name = "/sql_test"
  
    # 驗證該網站頁面是否開放
    is_Unable = check_unable_page("sql_test")

    # 驗證使用者程式使用權限
    list_programs_authority = check_programs_authority()

    # 初始化URL List
    list_URL = initialize_URL()

    ''' 取得目前該程式所屬html file 配置 '''
    html_file = 'SQL_Test/sql_test.html'

    # 產生篩選條件按鈕清單
    get_list_filter_option = SQL_Test.gen_filter_option()

    # 控制內容是否開放
    content_enable = False

    # 驗證授權，UserID必須為指定編號才能進行內容讀取
    if session['UserID'] == '0966027':
        content_enable = True

    ''' 實作AJAX請求處理 '''
    if request.method == 'POST':
        if content_enable:
            # 獲取json數據
            data = request.get_json(force=True)
            get_js_SQLSyntax = data['SQL_Syntax']
            print(f"[sql_test] UserID：{session['UserID']}, UserName：{session['UserNameEn']},  get_js_SQLSyntax：{get_js_SQLSyntax}")
            # 取得條件查詢結果
            run_staus, run_log, lsit_data, list_columns = SQL_Test.get_filter_data(SQL_syntax=get_js_SQLSyntax)
            return jsonify(dict(run_staus = run_staus, run_log=run_log, lsit_data=lsit_data, list_columns=list_columns))

    return render_template(html_file, UserID = session['UserID'], UserName = session['UserNameEn'],
        DPID = session['DPID'], DpName = session['DpName'], UserNameCh = session['UserNameCh'], store_name = session['StoreNO'],
        role_rank = session['RoleRank'], StoreNameC = session['StoreNameC'], StoreID = session['StoreID'], 
        page_name = page_name, html_file = html_file,
        list_URL=list_URL,
        list_programs_authority = list_programs_authority,
        is_Unable = is_Unable,
        content_enable = content_enable,
        get_list_filter_option = get_list_filter_option,
    )
'''-------------------------------------------------------------------'''

'''
----------------------------------------------------------------------
帳戶登入頁面-login實作區塊 
----------------------------------------------------------------------
'''
@app.route("/login", methods=['GET', 'POST'])
def login(): # 帳戶登入頁面

    # 頁面名稱
    page_name = "/login"
  
    # 驗證該網站頁面是否開放
    is_Unable = check_unable_page("login")

    # 載入Config設定登入頁面標題
    Http_Title = login_page_title
    status = None

    # 初始化所有session
    initialize_session()

    if request.method == 'POST':

        # Get AJAX JSON Data
        data = request.get_json(force=True)
        status = data['status']  # status

        if status == 'login':
            
            log_content = ""
            get_curtime = get_current_datetime()

            # 查詢 帳戶權限UserAuthority)Table，帳號與密碼是否有存在
            check_result = T_USER.query.filter_by(UserID=data['account'], Password=data['psw']).count()
        
            # 判斷當前登入的帳號密碼是否有存在，以存在筆數作為參考
            if check_result != 0:  # 如果有存在筆數不為0

                # 查詢取得帳戶資訊
                result = T_USER.query.filter_by(UserID=data['account'], Password=data['psw']).first()  

                # 查詢帳戶部門資訊
                select_DP = T_DP.query.filter_by(DPID=result.DPID).first()              

                # 判斷當前登入的帳號啟用狀態是否為啟用中(True)
                if  result.ActivationStatus: 

                    login_user(result)  # 會自動註冊新的session['user_id],內容為id                    

                    session['UserID'] = result.UserID  # 帳戶編號(UserID)
                    session['DPID'] = result.DPID # 部門編號
                    session['DpName'] = select_DP.DpName # 部門名稱
                    session['UserNameEn'] = result.UserNameEn  # 帳戶英文姓名(UserNameEn)
                    session['UserNameCh'] = result.UserNameCh  # 帳戶中文姓名(UserNameCh)
                    session['RoleRank'] = result.RoleRank # 角色
                    session['StoreID'] = result.StoreID # 分店索引
                    session['StoreNO'] = T_ST.query.filter_by(StoreID=session['StoreID']).first().StoreNO # 分店編號
                    session['StoreNameC'] = T_ST.query.filter_by(StoreID=session['StoreID']).first().StoreNameC # 分店中文名稱
                    logindate = get_curtime # 登入時間

                    log_content = "UserID: {} , UserNameEn: {}({}) ,  DpName: {}({}) . 登入系統".format(
                        session['UserID'], 
                        session['UserNameEn'],
                        session['UserNameCh'],
                        session['DpName'],
                        session['DPID'],
                    )

                    print("[login]: {}".format(log_content))

                    Insert_SysLog(
                        UserID = result.UserID,
                        UserNameEn = result.UserNameEn,
                        UserNameCh = result.UserNameCh,
                        StoreID = result.StoreID,
                        StoreNO = T_ST.query.filter_by(StoreID=session['StoreID']).first().StoreNO,
                        DPID = result.StoreID,
                        DpName = select_DP.DpName,
                        PageName = page_name,
                        log_class = log_class_list[page_name],
                        log_content = log_content,
                        InertDate = get_curtime
                    )               

                    if session['RoleRank'] != "DBAdmin":
                        # 回傳轉址URL與驗證狀態,以JSON格式
                        return jsonify(dict(redirect=url_for('index', UserID=session['UserID'], UserName=session['UserNameEn']), allow_redirect=True))
                    else:

                        print("[login] RoleRank [{}] is DBAdmin, redirect to DB Admin Page.".format(session['RoleRank']))
                        # 回傳轉址URL與驗證狀態,以JSON格式
                        return jsonify(dict(redirect=url_for('admin.index'), allow_redirect=True))

                else:

                    log_content = "該帳戶目前未授權登入系統，請與所屬管理者連絡處理。\n[UserID]: {} \n[UserNameEn]: {}({}) \n[DpName:] {}({})".format(
                        result.UserID,
                        result.UserNameEn,
                        result.UserNameCh,
                        select_DP.DpName,
                        result.DPID,
                    )
                     
                    # 新增紀錄
                    Insert_SysLog(
                        UserID = result.UserID,
                        UserNameEn = result.UserNameEn,
                        UserNameCh = result.UserNameCh,
                        StoreID = result.StoreID,
                        StoreNO = T_ST.query.filter_by(StoreID=result.StoreID).first().StoreNO,
                        DPID = result.DPID,
                        DpName = select_DP.DpName,
                        PageName = page_name,
                        log_class = log_class_list[page_name],
                        log_content = log_content,
                        InertDate = get_curtime
                    )   

                    err_log = log_content

                    print("[login]: {}".format(log_content))

                    return jsonify(dict(allow_redirects=False,err_log=err_log))

            else:           

                err_log = "帳號或密碼輸入錯誤!"

                print("[login]: 登入失敗. {}".format(get_current_datetime()))

                return jsonify(dict(allow_redirects=False,err_log=err_log))

    else:

        return render_template('login.html', Http_Title = Http_Title, page_name = page_name)

'''
----------------------------------------------------------------------
帳戶登出頁面-logout實作區塊 
----------------------------------------------------------------------
'''
@app.route('/logout', methods=['GET'])
@login_required
def logout(): # 帳戶登出頁面

    page_name = "/logout"

    log_content = "UserID: {} , UserNameEn: {}({}) ,  DpName: {}({}) 登出系統 {}".format(
        session['UserID'], 
        session['UserNameEn'],
        session['UserNameCh'],
        session['DpName'],
        session['DPID'],
        request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    )

    print("[logout]: {}".format(log_content))

    # 新增紀錄
    Insert_SysLog(
        UserID = session['UserID'],
        UserNameEn = session['UserNameEn'],
        UserNameCh = session['UserNameCh'],
        StoreID = session['StoreID'],
        StoreNO = session['StoreNO'],
        DPID = session['DPID'],
        DpName = session['DpName'],
        PageName = page_name,
        log_class = log_class_list[page_name],
        log_content = log_content,
        InertDate = get_current_datetime()
    )  

    logout_user()  # 登出

    initialize_session()  # 初始化Session 

    return redirect(url_for('login'))
'''-------------------------------------------------------------------'''





