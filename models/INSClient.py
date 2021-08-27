
import sqlite3 as sql
import requests, configparser
from models import database_controller
import json
import threading
from PyQt5 import QtWidgets, QtGui


URL = {
    'login'                                    : 'login/',

    'createUnpackedProduct'                       :'AddUnpackedProduct/' ,
    'createRawMaterials'                          :'AddRawMaterial/'     ,
    'createRawMaterialsInput'                      :'AddRawMaterialInput/' ,
    'createRawMaterialsOutput'                     :'AddRawMaterialOutput/' ,
    'createUnpackedProductRawMaterial'            :'AddUnpackedProductRawMaterial/'  ,
    'createPackedProduct'                         :'AddPackedProduct/'               ,
    'createPackingMaterial'                       :'AddPackingMaterial/'             ,
    'createPackingMaterialInput'                  :'AddPackingMaterialInput/'         ,
    'createPackingMaterialOutput'                 :'AddPackingMaterialOutput/'        ,
    'createPackedProductPackingMaterial'          :'AddPackedProductPackingMaterial/' ,
    'createOrder'                                 :'AddOrder/'                        ,

    'editRawMaterials'                          :'RawMaterial/{}/'             ,
    'editPackingMaterial'                      :'PackingMaterial/{}/'         ,
    'editUnpackedProduct'                      :'UnpackedProduct/{}/'         ,
    'editUnpackedProductRawMaterial'           :'UnpackedProductRawMaterial/{}',
    'editPackedProduct'                        :'PackedProduct/{}/'            ,
    'editPackedProductPackingMaterial'         :'PackedProductPackingMaterial/{}/' ,
    'editOrder'                                :'Order/{}/'                     
}






def login(mw_ui,url,username,password):
    config = configparser.ConfigParser()
    config.read('settings.ini')
    
    mw_ui.url = url
    url= url+config['URLs']['login']
    try:
        login_page=mw_ui.session.get(url)
    except:
        return  (0,'(Wrong url)')

    csrf_token_code=(login_page.cookies.get('csrftoken'))
    database_code = database_controller.get_data(mw_ui.main_data_base, 'database_code')[0][0]
    ret=mw_ui.session.post(url, {'csrfmiddlewaretoken':csrf_token_code,'username':username,'password':password,'database_code':database_code,'app':'INSPP'})
    

    # send readed messages
    readed_mails = database_controller.get_data(mw_ui.main_data_base , 'readed_mails')
    status=0
    for m in readed_mails:
        try:
            mw_ui.session.get(config['login-settings']['url']+config['URLs']['readmail'].format(m[0]))
            status = 1
        except:
            status = 0
    
    if status:
        con=sql.connect(mw_ui.main_data_base)
        con.execute('delete from readed_mails ')
        con.commit()
        con.close()

    if ret.url == url:
        mw_ui.logged_in=False
        mw_ui.INS_LOGO_SB.hide()
        mw_ui.username_label.setText('')
        mw_ui.actionINS.setText('Login')
        return  (0,ret.cookies.get('message'))
        
    else:

        mw_ui.logged_in=True
        mw_ui.INS_LOGO_SB.show()
        mw_ui.username_label.setText(config['login-settings']['username'])
        mw_ui.actionINS.setText('Logout')
        
        open_drive_folder(mw_ui)
        return (1,)
    
    
    
    
def open_drive_folder(mw_ui, folder_pk= 'main folder'):
    config = configparser.ConfigParser()
    config.read('settings.ini')
    print(mw_ui.url+'download/30/')
    mw_ui.session.get(mw_ui.url+'download/30/')

    if folder_pk == 'main folder':
        url = mw_ui.url+config['URLs']['main_personal_storage_API']

    else:
        url = mw_ui.url+config['URLs']['personal_storage_API'].format(folder_pk)

    mw_ui.drive_list.clear()
    folder_data = mw_ui.session.get(url).json()
    folder_icon = QtGui.QIcon(config['icons themes folders'][config['settings']['style']]+'/folder.png')
    file_icon = QtGui.QIcon(config['icons themes folders'][config['settings']['style']]+'/file.png')
    for folder in folder_data['folders']:

        item = QtWidgets.QListWidgetItem()
       	item.setData(2,folder['name'])
       	item.setData(4,folder['pk'])
        item.setIcon(folder_icon)
        item.setData(5,'folder')
       	mw_ui.drive_list.addItem(item)

    for files in folder_data['files']:

        item = QtWidgets.QListWidgetItem()
       	item.setData(2,files['name'])
       	item.setData(4,files['file'])
        item.setIcon(file_icon)
        item.setData(5,'folder')
       	mw_ui.drive_list.addItem(item)


    

def ins_logout(mw_ui):
    mw_ui.logged_in=False   
    mw_ui.INS_LOGO_SB.hide()
    mw_ui.username_label.setText('')
    mw_ui.actionINS.setText('Login')





def fill_out_form(session,url,data,op_type = 'create'):
    try:
        get_form = session.get(url)
        data['csrfmiddlewaretoken']=(get_form.cookies.get('csrftoken'))
        data['app']='INSPP'
        data[op_type]=[op_type,]
        returned_page=session.post(url,data)
        return    returned_page 

    except:
        return 0



