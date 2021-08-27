import random, datetime, string, configparser
import sqlite3 as sql
from models import INSClient, views
import json
from PyQt5 import QtWidgets

all_chars = string.ascii_letters + string.digits 

new_database_code=''.join(random.choices(all_chars, k=20))





tables={# table_name : ( columns , defult_data  )
    'RawMaterials'                  :( ('id integer primary key autoincrement' ,'name', 'm_type', 'code', 'quantity', 'unit', 'density','loq_warning','loq_quantity', 'loq_unit')                                                    ,[]),
    'RawMaterialsOutput'            :( ('id integer primary key autoincrement' ,'material', 'quantity', 'unit', 'date', 'note')                                                    ,[]),
    'RawMaterialsInput'             :( ('id integer primary key autoincrement' ,'material', 'quantity', 'unit', 'date', 'note')                                                    ,[]),

    'PackingMaterial'               :( ('id integer primary key autoincrement' ,'name','code','quantity','unit','loq_warning','loq_quantity')                                                                            ,[]),
    'PackingMaterialOutput'         :( ('id integer primary key autoincrement' ,'material', 'quantity', 'date', 'note')                                                    ,[]),
    'PackingMaterialInput'          :( ('id integer primary key autoincrement' ,'material', 'quantity', 'date', 'note')                                                    ,[]),

    'UnpackedProduct'               :( ('id integer primary key autoincrement' ,'name','code','material_type','quantity','unit')                                                            ,[]),
    'UnpackedProductRawMaterial'    :( ('id integer primary key autoincrement' ,'product','material','percent')                                                                             ,[]),# rename percent
    'PackedProduct'                 :( ('id integer primary key autoincrement' ,'name','code','unpacked_product','unpacked_product_quantity_in_one','unit')                                        ,[]),# add code,unit column
    'PackedProductPackingMaterial'  :( ('id integer primary key autoincrement' ,'packed_product','packing_material','count')                                                                        ,[]),# rename count
    '"Order"'                       :( ('id integer primary key autoincrement' ,'name','code','packed_product','quantity','starting_date','planned_finishing_date','actual_finishing_date','done')  ,[]),
    'inbox_mail'                    :( ('id integer primary key autoincrement' ,'username_from','subject','body','sending_datetime','received','readed')  ,[]),
    'outbox_mail'                   :( ('id integer primary key autoincrement' ,'username_to','subject','body','sending_datetime','received','readed')  ,[]),
    
    'readed_mails'                       :( ('mail_id',),[]),
    'backups'                       :( ('id integer primary key autoincrement' ,'date','location')                                                                                          ,[]),
    'history'                       :( ('id integer primary key autoincrement' , 'operation' , '"table"' , '"values"' , 'date_and_time', 'item_id','"pushed"'),[]),
    'database_code'                 :( ('code',)                                                                                                    ,[[ '"'+new_database_code+'"'  ],]),
    'local_creation_items'          :( ('ids',)                                                                                                     ,[[ '"[]"'  ],])

}



tables_cascade={#table name  : ( (subtable name , id column name), )
    'RawMaterials'                  :(('UnpackedProductRawMaterial','material'),),
    'UnpackedProduct'               :(('PackedProduct','unpacked_product'),('UnpackedProductRawMaterial','product')),
    'UnpackedProductRawMaterial'    :(False,),
    'PackedProduct'                 :(('"Order"','packed_product'),('PackedProductPackingMaterial','packed_product')),
    'PackingMaterial'               :(('PackedProductPackingMaterial','packing_material'),),
    'PackedProductPackingMaterial'  :(False,),
    '"Order"'                       :(False,),
    'backups'                       :(False,),
    'history'                       :(False,),
    'database_code'                 :(False,),
}

synchable_tables=[
    'RawMaterials',
    'RawMaterialsOutput',
    'RawMaterialsInput',
    'PackingMaterial',
    'PackingMaterialOutput',
    'PackingMaterialInput',
    'UnpackedProduct',
    'UnpackedProductRawMaterial',
    'PackedProduct',
    'PackedProductPackingMaterial',
    'Order',

]

tables_visible_names={
    'RawMaterials'                  :'Raw Materials',
    'UnpackedProduct'               :'Unpacked Products',
    'UnpackedProductRawMaterial'    :'UnpackedProductRawMaterial',
    'PackedProduct'                 :'Packed Products', 
    'PackingMaterial'               :'Packing Materials',
    'PackedProductPackingMaterial'  :'PackedProductPackingMaterial',
    '"Order"'                       :'Orders',
    'backups'                       :'backups',
    'history'                       :'history',
    'database_code'                 :'database_code',
}

tables_urls = {

    'add-c'                           :'AddRawMaterial/',
    'add-UnpackedProduct'             :'AddUnpackedProduct/',
    'add-UnpackedProductRawMaterial'  :'AddUnpackedProductRawMaterial/',
    'add-PackedProduct'               :'AddPackedProduct/',
    'add-PackingMaterial'             :'AddPackingMaterial/',
    'add-PackedProductPackingMaterial':'AddPackedProductPackingMaterial/',
    'add-"Order"'                     :'AddOrder/',
}


material_types={
    'solid' :['MG','CG','DG','G','DAG','HG','KG','T'],
    'liquid':['ML','CL','DL','L','DAL','HL','KL'],
    'gas'   :['ML','CL','DL','L','DAL','HL','KL'],
    }


material_units_convert={
    'MG'    :0.001
    ,'CG'   :0.01
    ,'DG'   :0.1
    ,'G'    :1
    ,'DAG'  :10
    ,'HG'   :100
    ,'KG'   :1000
    ,'T'    :1000000
    
    ,'ML'   :0.001
    ,'CL'   :0.01
    ,'DL'   :0.1
    ,'L'    :1
    ,'DAL'  :10
    ,'HL'   :100
    ,'KL'   :1000

}

def convert_to_best_unit(value,unit,m_type):
    units=material_types[m_type.lower()]
    while True :
        if float(value)>=10 and units.index(unit)<len(units)-1 and unit.upper()!='KG':
            value=value/10
            unit=units[units.index(unit)+1]
        elif float(value)>=1000 and units.index(unit)<len(units)-1 and unit.upper()=='KG':
            value=value/1000
            unit=units[units.index(unit)+1]
        else:
            break
    return (value,unit)




packing_materials_units=[
    'Metre',
    'Piace'
]


def get_data(db , table, columns='*'  , condition=''):
    con=sql.connect(db)
    data=con.execute(f' select {columns} from {table} {condition} ').fetchall()
    con.close()
    return data


def check_database(path):
    con=sql.connect(path)
    database_tables=con.execute("SELECT name FROM sqlite_master WHERE type ='table' ").fetchall()

    for table in tables.keys():
        if (table.replace('"',''),) not in database_tables:
            columns=','.join(tables[table][0])
            con.execute('create table {} ({})'.format(table, columns))

            if tables[table][0][0]=='id integer primary key autoincrement':                
                columns=','.join(tables[table][0][1:])


            for bit in tables[table][1]:
                data=','.join(bit)
                
                con.execute('insert into {} ({}) values ({})'.format(table , columns , data))

                
    con.commit()
    con.close()

def add_command_to_histoy(con , table , operation , data, _id ):
    config = configparser.ConfigParser()
    config.read('settings.ini')
    try:
        data = json.dumps(data)
    except:
        pass
    local_creation_items = json.loads(con.execute('select * from local_creation_items').fetchall()[0][0])
    
    if operation == 'edit' and _id in local_creation_items:
        con.execute(f'''update history set "values" = '{data}' where item_id = {_id} and "table" = '{table}' ''')
        
    elif operation == 'delete' and _id in local_creation_items:
        con.execute(f'delete from history where item_id = {_id}')

    

    else:
        if operation == 'create':
            con.execute('update local_creation_items set ids ="{}"'.format(json.dumps(local_creation_items+[_id,])))

        con.execute("""insert into history ( 'table' , operation , 'values' , date_and_time, item_id ,'pushed') values ('{}','{}','{}','{}',{},0)""".format(table, operation, json.dumps(data), str(datetime.datetime.today()), _id ))
        
    con.commit()



def add(mw,table,data,with_id = False):
    con=sql.connect(mw.main_data_base)


    filtered_data=[]
    for bit in range(len(data)):
        if type(bit) == str:
            filtered_data.append(data[bit].replace('"','\"').replace("'",'\''))
        else:
            filtered_data.append(data[bit])
    filtered_data=tuple(filtered_data)
    if len(filtered_data)==1:
        filtered_data=str(filtered_data).replace(',','')


    if tables[table][0][0]=='id integer primary key autoincrement':                
        if with_id:
            columns=json.dumps(('id',)+tables[table][0][1:])
        else:
            columns=json.dumps(tables[table][0][1:])
        
    else:
        columns=json.dumps(tables[table][0])
    columns=columns.replace('[','(').replace(']',')')
    

    com='''insert into {} {} values {}'''.format(table,columns,filtered_data)

    

    adding_return=con.execute(com)
    if not with_id and table not in ('readed_mails',):
        
        if mw.logged_in:
            try:
                config = configparser.ConfigParser()
                config.read('settings.ini')
                form_data={}
                columns = tables[table][0][1:]
                for i in range(len(columns)):
                    form_data[columns[i]]=filtered_data[i]

                returned_form = INSClient.fill_out_form(mw.session , config['login-settings']['url']+ INSClient.URL['create'+table],form_data)
                last_local_id = con.execute(f'select id from {table}').fetchall()[-1][0]
                new_id = returned_form.cookies.get('id')
                con.execute(f'update {table} set id = {new_id} where id = {last_local_id}')
                
            except:
                mw.logged_in=False
                mw.INS_LOGO_SB.hide()
                add_command_to_histoy(con , table , 'create' , filtered_data,adding_return.lastrowid )
        else:
            add_command_to_histoy(con , table , 'create' , filtered_data,adding_return.lastrowid )
    con.commit()#lastrowid
    con.close()

    
    return adding_return




def get_linked_data(db, main_table, item_id,data):  
    for table in tables_cascade[main_table]:
        if table:
            try:
                bit = get_data(db , table[0], columns='id,name'  , condition=f'where {table[1]} = {item_id} ')
            except:
                bit = get_data(db , table[0], columns='id'  , condition=f'where {table[1]} = {item_id} ')
            if len(bit)>0:
                data[table[0]]=[]

            for i in bit:
                data[table[0]]+=(i,)

            if len(bit)>0:
                get_linked_data(db, table[0] , bit[0][0], data)

    return data



def delete(mw,db, table, _id):
    con=sql.connect(db)

    def delete_confirmed():
        con.execute(f'delete from {table} where id = {_id}')
        if mw.logged_in:
            try:
                config = configparser.ConfigParser()
                config.read('settings.ini')


                INSClient.fill_out_form(mw.session , config['login-settings']['url']+ INSClient.URL['edit'+table.replace('"','')].format(_id),{},'delete')
            except:
                mw.logged_in=False
                mw.INS_LOGO_SB.hide()
                add_command_to_histoy(con , table , 'delete' , '',_id )
        else:
            add_command_to_histoy(con , table , 'delete' , '',_id )

        
        for t in data.keys():
            for item in data[t]:
                con.execute(f'delete from {t} where id = {item[0]}')
                add_command_to_histoy(con , t , 'delete' , '',_id )

        con.commit()
        views.view_all_data(mw)

    data = get_linked_data(db, table, _id,{})
    msg=''
    for i in data.keys():
        if len(data[i][0])==2:
            msg+='\n'+tables_visible_names[i]+' ('+str(len(data[i]))+'):\n'
            for n in data[i]:
                msg+=f'     . {n[1]}\n'
    if len(msg)>0:
        a=QtWidgets.QMessageBox.question(mw , 'Cascade delete confirm' ,'There are some cascaded data will deleted if you delete this item\n'+msg+'\n\n Do you still want to delete?')
        if a==QtWidgets.QMessageBox.Yes:
            delete_confirmed()
    else:
        delete_confirmed()
   

def edit_specific_field(mw,table,data,_id):
    con=sql.connect(mw.main_data_base)
    con.execute(f'update {table} set {data} where id = {_id}')
    con.commit()
    if table=='RawMaterials':
        views.view_rm_low_quantity(mw, f' and id = {_id}')

    if table=='PackingMaterial':
        views.view_pm_low_quantity(mw, f' and id = {_id}')


def edit(mw,table,data,_id):
    
    con=sql.connect(mw.main_data_base)

    if tables[table][0][0]=='id integer primary key autoincrement':                
        columns=(tables[table][0][1:])
    else:
        columns=(tables[table][0])
    
    

    filtered_data=[]

    for bit in range(len(data)):
        if type(bit) == str:
            filtered_data.append(('"'+data[bit].replace('"','\"').replace("'",'\'')+'"'))
        else:
            filtered_data.append(data[bit])

    filtered_data.append(_id)
    filtered_data=tuple(filtered_data)
    
    keys_and_values=''
    
    for i in range(len(columns)):
        if type(filtered_data[i]) == str:
            keys_and_values+=f' "{columns[i]}" = "{filtered_data[i]}" ,'
        else:
            keys_and_values+=f' "{columns[i]}" = {filtered_data[i]} ,'

    keys_and_values=keys_and_values[:len(keys_and_values)-1]
    
    com='''update {} set {} where id={}'''.format(table,keys_and_values,_id)
    
    adding_return=con.execute(com)

    if mw.logged_in:
        try:
                config = configparser.ConfigParser()
                config.read('settings.ini')
                form_data={}
                columns = tables[table][0][1:]
                for i in range(len(columns)):
                    form_data[columns[i]]=filtered_data[i]

                INSClient.fill_out_form(mw.session , config['login-settings']['url']+ INSClient.URL['edit'+table.replace('"','')].format(_id),form_data,'edit')
                
        except:
                mw.logged_in=False
                mw.INS_LOGO_SB.hide()
                add_command_to_histoy(con , table , 'edit' , filtered_data[:-1], filtered_data[-1] )
    else:
            print(filtered_data)
            add_command_to_histoy(con , table , 'edit' , filtered_data[:-1], filtered_data[-1] )
    
    con.commit()
    if table=='RawMaterials':
        views.view_rm_low_quantity(mw, f' and id = {_id}')

    elif table=='PackingMaterial':
        views.view_pm_low_quantity(mw, f' and id = {_id}')


    
    return adding_return