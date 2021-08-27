
import requests
import configparser
import json, time, threading
from models import database_controller, views
import sqlite3 as sql
from  models import INSClient, windows




def check_data(mw_ui,session):
    config = configparser.ConfigParser()
    config.read('settings.ini')
    while mw_ui.isVisible() and mw_ui.logged_in:
        if mw_ui.isActiveWindow():
            try:
                time.sleep(1)
                changed_tables = session.get(config['login-settings']['url']+config['URLs']['GetUpdatedTable']).json()
                if len(changed_tables)>0:

                    mw_ui.loading_gif.show()
                    install_missing_data(mw_ui,session)
                    views.view_all_data(mw_ui)
                    mw_ui.loading_gif.hide()
            except:
                mw_ui.logged_in = False
                mw_ui.username_label.username_label('')
                mw_ui.INS_LOGO_SB.hide()
                
            


def init(session,mw_ui):
    
    config = configparser.ConfigParser()
    config.read('settings.ini')
    mw_ui.synchronization=True

    #clean database
    con=sql.connect(mw_ui.main_data_base)
    unpushed_commits = con.execute('select * from history where pushed = 0').fetchall()
    models_from_name = {
        'RAWMATERIALS':                  'RawMaterials',
        'RAWMATERIALSOUTPUT':           'RawMaterialsOutput',
        'RAWMATERIALSINPUT':            'RawMaterialsInput',
        'PACKINGMATERIAL':              'PackingMaterial',
        'PACKINGMATERIALOUTPUT':        'PackingMaterialOutput',
        'PACKINGMATERIALINPUT':         'PackingMaterialInput',
        'UNPACKEDPRODUCT':              'UnpackedProduct',
        'UNPACKEDPRODUCTRAWMATERIAL':   'UnpackedProductRawMaterial',
        'PACKEDPRODUCT':                'PackedProduct',
        'PACKEDPRODUCTPACKINGMATERIAL': 'PackedProductPackingMaterial',
        'ORDER':                        '"Order"',
        'messages':                     'inbox_mail'
    }
    
    changed_tables = session.get(config['login-settings']['url']+config['URLs']['GetUpdatedTable']).json()
    for table in changed_tables:
        if table !='mail':
            con.execute(f' delete from {models_from_name[table]}')

    new_ids={
            'RawMaterials':{},
            'PackingMaterial':{},
            'UnpackedProduct':{},
            'PackedProduct':{},
        }
    #push history


    for commit in unpushed_commits:

        if commit[2] not in ('inbox_mail','outbox_mail'):
            print(unpushed_commits)
            try :
                commit=json.loads(commit)
            except:
                pass
            
            table = commit[2]
            data = json.loads(commit[3])
            
            url = config['login-settings']['url']+ INSClient.URL[ (commit[1]+commit[2]).replace('"','').replace('delete','edit') ]
            if commit[1]=='edit' or commit[1]=='delete':
                url = url.format(commit[-2])
            dict_data={}
            
            columns=database_controller.tables[commit[2]][0]
            try:
                data = json.loads(data)
            except:
                pass 
            
            for bit in range(len(data)):
                
                dict_data[columns[bit+1]] = data[bit]


            if table == 'RawMaterialsOutput' or table =='RawMaterialsInput':
                if int(dict_data['material']) in new_ids['RawMaterials'].keys():
                    dict_data['material'] = new_ids['RawMaterials'][dict_data['material']]

            elif table == 'PackingMaterialOutput' or table =='PackingMaterialInput':
                if int(dict_data['material']) in new_ids['PackingMaterial'].keys():
                    dict_data['material'] = new_ids['PackingMaterial'][dict_data['material']]

            elif table == 'UnpackedProductRawMaterial':
                if int(dict_data['material']) in new_ids['RawMaterials'].keys():
                    dict_data['material'] = new_ids['RawMaterials'][dict_data['material']]

                if int(dict_data['product']) in new_ids['UnpackedProduct'].keys():
                    dict_data['product'] = new_ids['UnpackedProduct'][dict_data['product']]

            elif table == 'PackedProduct':
                if int(dict_data['unpacked_product']) in new_ids['UnpackedProduct'].keys():
                    dict_data['unpacked_product'] = new_ids['UnpackedProduct'][dict_data['unpacked_product']]

            elif table == 'PackedProductPackingMaterial':
                if int(dict_data['packed_product']) in new_ids['PackedProduct'].keys():
                    dict_data['packed_product'] = new_ids['PackedProduct'][dict_data['packed_product']]

                if int(dict_data['packing_material']) in new_ids['PackingMaterial'].keys():
                    dict_data['packing_material'] = new_ids['PackingMaterial'][dict_data['packing_material']]

            elif table == '"Order"':#packed_product
                if int(dict_data['packed_product']) in new_ids['PackedProduct'].keys():
                    dict_data['packed_product'] = new_ids['PackedProduct'][dict_data['packed_product']]


            
            form = INSClient.fill_out_form(session,url,dict_data,commit[1])
            
            
            if table == 'RawMaterials':
                try:
                    new_ids['RawMaterials'][commit[5]]=int(form.cookies.get('id'))
                except:
                    pass

            elif table == 'PackingMaterial':
                try:
                    new_ids['PackingMaterial'][commit[5]]=int(form.cookies.get('id'))
                except:
                    pass


            elif table == 'UnpackedProduct':
                try:
                    new_ids['UnpackedProduct'][commit[5]]=int(form.cookies.get('id'))
                except:
                    pass

            elif table == 'PackedProduct':
                try:
                    new_ids['PackedProduct'][commit[5]]=int(form.cookies.get('id'))
                except:
                    pass


    con.execute('delete from history ')
    con.execute('update local_creation_items set ids ="[]"')

    con.commit()
    con.close()

    #install data
    
    
    install_missing_data(mw_ui,mw_ui.session)
    threading.Thread(target=check_data, args=(mw_ui,session)).start()
            
    mw_ui.synchronization=False  
    
    views.view_all_data(mw_ui)
    mw_ui.loading_gif.hide()
    


def get_mail(mw_ui,session):
    config = configparser.ConfigParser()
    config.read('settings.ini')
    messages = session.get(config['login-settings']['url']+config['URLs']['viewmail']).json()
    inbox   =   messages['inbox']
    outbox  =   messages['outbox']
    edited  =   messages['edited']


    


    for mail in outbox:
        database_controller.add(mw_ui, 'outbox_mail', list(mail.values()) ,True)

    for mail in inbox:
        database_controller.add(mw_ui, 'inbox_mail', list(mail.values()),True)

    for mail in edited:
        database_controller.edit(mw_ui , 'outbox_mail' , list(mail.values())[1:] , list(mail.values())[0])
        database_controller.edit(mw_ui , 'inbox_mail' , list(mail.values())[1:] , list(mail.values())[0])

    views.fill_out_mail_list(mw_ui ,mw_ui.counts_labels, mw_ui.main_data_base, mw_ui.outbox_mail 			, 'inbox_mail' 	)
    views.fill_out_mail_list(mw_ui ,mw_ui.counts_labels, mw_ui.main_data_base, mw_ui.outbox_mail 			, 'outbox_mail' 	)

    if 0 < len(inbox) == 1 :
        windows.notification(mw_ui, 'Mail Inbox', 'you have 1 new message')
    elif len(inbox)>1:
        windows.notification(mw_ui, 'Mail Inbox', f'you have {len(inbox) == 1} new messages')

    

    


def install_missing_data(mw_ui,session):

    models_from_name = {
        'RAWMATERIALS':                  'RawMaterials',
        'RAWMATERIALSOUTPUT':           'RawMaterialsOutput',
        'RAWMATERIALSINPUT':            'RawMaterialsInput',
        'PACKINGMATERIAL':              'PackingMaterial',
        'PACKINGMATERIALOUTPUT':        'PackingMaterialOutput',
        'PACKINGMATERIALINPUT':         'PackingMaterialInput',
        'UNPACKEDPRODUCT':              'UnpackedProduct',
        'UNPACKEDPRODUCTRAWMATERIAL':   'UnpackedProductRawMaterial',
        'PACKEDPRODUCT':                'PackedProduct',
        'PACKEDPRODUCTPACKINGMATERIAL': 'PackedProductPackingMaterial',
        'ORDER':                        '"Order"',
        'messages':                     'inbox_mail'
    }

    models_ui_object = {
        'RAWMATERIALS':                 mw_ui.tab_3,
        'PACKINGMATERIAL':              mw_ui.tab_4,
        'UNPACKEDPRODUCT':              mw_ui.tab_10,
        'PACKEDPRODUCT':                mw_ui.tab_6,
        'ORDER':                        mw_ui.tabWidget,
        'messages':                     mw_ui.tab_5
    }




    config = configparser.ConfigParser()
    config.read('settings.ini')
    changed_tables = session.get(config['login-settings']['url']+config['URLs']['GetUpdatedTable']).json()

    

    if 'mail' in changed_tables:
        changed_tables.remove('mail')
        get_mail(mw_ui,session)

    con=sql.connect(mw_ui.main_data_base)
    for table in changed_tables:
        con.execute(f' delete from {models_from_name[table]}')
        if table.upper() in models_ui_object.keys():
            models_ui_object[table.upper()].setEnabled(0)
    con.commit()
    con.close()

    

    for table in changed_tables:
        page = session.get(config['login-settings']['url']+config['URLs']['GetData'])
        csrf_token_code=(page.cookies.get('csrftoken'))
        
        data = session.post(config['login-settings']['url']+config['URLs']['GetData'], {'csrfmiddlewaretoken':csrf_token_code,'name':table}).json()
        
        if table == 'Order':
            table='"Order"'
        for bit in data:
            if table == 'RAWMATERIALS':
                bit = [int(bit[0]), bit[1],bit[2],bit[3],float(bit[4]),bit[5],float(bit[6]),bit[7],float(bit[8]),bit[9]]

            elif table == 'RAWMATERIALSOUTPUT' or table =='RAWMATERIALSINPUT':
                bit = [int(bit[0]), int(bit[1]),float(bit[2]),bit[3],bit[4],bit[5]]

            elif table == 'PACKINGMATERIAL':
                bit = [int(bit[0]), bit[1],bit[2],float(bit[3]),bit[4],bit[5],float(bit[6])]

            elif table == 'PACKINGMATERIALOUTPUT' or table =='PACKINGMATERIALINPUT':
                bit = [int(bit[0]), int(bit[1]),float(bit[2]),bit[3],bit[4]]

            elif table == 'UNPACKEDPRODUCT':
                bit = [int(bit[0]), bit[1],bit[2],bit[3],float(bit[4]),bit[5]]

            elif table == 'UNPACKEDPRODUCTRAWMATERIAL':
                bit = [int(bit[0]), int(bit[1]),int(bit[2]),float(bit[3])]

            elif table == 'PACKEDPRODUCT':
                bit = [int(bit[0]), bit[1],bit[2],int(bit[3]),float(bit[4]),bit[5]]

            elif table == 'PACKEDPRODUCTPACKINGMATERIAL':
                bit = [int(bit[0]), int(bit[1]),int(bit[2]),float(bit[3])]

            elif table == 'ORDER':
                bit = [int(bit[0]), bit[1],bit[2],int(bit[3]),float(bit[4]),bit[5],bit[6],bit[7],bool(bit[8])]

    
    

            
            for i in range(len(bit)):
                if bit[i] == None:
                    bit[i]=''
            database_controller.add(mw_ui, models_from_name[table],bit,with_id=True)

        if table.upper() in models_ui_object.keys():
            models_ui_object[table.upper()].setEnabled(1)