from models import database_controller , windows
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtGui, QtCore
import datetime, json
from calendar import monthrange
import configparser
from playsound import playsound
from models import styles

def add_item_to_listWidget(title,listWidget,**data):
	item = QtWidgets.QListWidgetItem()
	item.setData(2,title)

	for bit in data.keys():#  data ={ data_4:2 , data_5:'rm' } 	data_4 for id / data_5 for material type
		item.setData(int(bit[-1]),data[bit])

	listWidget.addItem(item)

def fill_out_list(count_label, db, GUI_list , db_table , title_index , title_form , id_index,tooltip_form=None, condition='' ):
	
    data = database_controller.get_data(db , db_table, condition=condition )
    if count_label!=None:
    	count_label[db_table].setToolTip(str(len(data)))


    GUI_list.clear()
    for bit in data:
       	title=title_form

       	for i in range(len(title_index)):
       		title=title.replace('{'+str(i)+'}', str(bit[title_index[i]]) )

       	tooltip=tooltip_form
       	item = QtWidgets.QListWidgetItem()
       	
       	item.setData(2,title)
       	item.setData(4,bit[id_index])
       	if tooltip!=None:
       		for i in range(len(title_index)):
       			tooltip=tooltip.replace('{'+str(i)+'}', str(bit[title_index[i]]) )

       		tooltip=tooltip.replace('\\n','<br>')
       		item.setToolTip(tooltip)


       	GUI_list.addItem(item)



def fill_out_mail_list(mw_ui , count_label, db, GUI_list , db_table ):
    config = configparser.ConfigParser()
    config.read('settings.ini')
    tooltip_form='{}'
    title_index = (1,2) 
    title_form = '{0} ({1})'	
    data = database_controller.get_data(db , db_table)[::-1]
    if db_table=='inbox_mail':
    	mw_ui.new_messages_count = 0

    if count_label!=None:
    	count_label[db_table].setText(str(len(data)))


    GUI_list.clear()
    for bit in data:

       	title=title_form

       	for i in range(len(title_index)):
			
       			title=title.replace('{'+str(i)+'}', str(bit[title_index[i]]) )

       	tooltip=tooltip_form
       	item = QtWidgets.QListWidgetItem()
       	if not bit[-1] and db_table=='inbox_mail':
       		path = config['icons themes folders'][config['settings']['style']]+'/mail.png'
       		mw_ui.new_messages_count+=1
       		item.setIcon(QtGui.QIcon(path))
       		
       	item.setData(2,title)
       	item.setData(4,bit[0])


       	GUI_list.addItem(item)
    GUI_list.update()


def fill_out_orders_list(mw_ui):

    db 			= mw_ui.main_data_base
    GUI_list	= mw_ui.orders_list
    db_table	= '"Order"'
	
    data = database_controller.get_data(db , db_table )
    mw_ui.orders_label.setToolTip(str(len(data)))


    GUI_list.clear()
    for bit in data:#'name','code','packed_product','quantity','starting_date','planned_finishing_date','actual_finishing_date','done'
       	order_sd = datetime.date.fromisoformat(bit[5])
       	if bit[8]:
       		status='Done'

		
       	elif  datetime.date.fromisoformat(bit[5]) > datetime.date.today() :# not started yet
       		status='Wating'

       	elif  datetime.date.fromisoformat(bit[5]) <= datetime.date.today() <= datetime.date.fromisoformat(bit[6]):# in progress
       		status='In progress'

       	else:# late
       		status='Late'



       	title=f'{bit[1]}	({bit[2]})	({status})'

		
       	item = QtWidgets.QListWidgetItem()
       	item.setData(2,title)
       	item.setData(4,bit[0])


       	GUI_list.addItem(item)


def view_mw_icons(mw_ui):
	config = configparser.ConfigParser()
	config.read('settings.ini')

	icon_folder=config['icons themes folders'][config['settings']['style']]

	icon	= QtGui.QIcon()
	icon.addPixmap(QtGui.QPixmap(f"{icon_folder}/Raw materials Rotate.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
	mw_ui.materials_and_products_widget.setTabIcon(0,icon)

	icon	= QtGui.QIcon()
	icon.addPixmap(QtGui.QPixmap(f"{icon_folder}/Packing materials Rotate.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
	mw_ui.materials_and_products_widget.setTabIcon(1,icon)

	icon	= QtGui.QIcon()
	icon.addPixmap(QtGui.QPixmap(f"{icon_folder}/unpacked products rotate.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
	mw_ui.materials_and_products_widget.setTabIcon(2,icon)

	icon	= QtGui.QIcon()
	icon.addPixmap(QtGui.QPixmap(f"{icon_folder}/packed products rotate.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
	mw_ui.materials_and_products_widget.setTabIcon(3,icon)

	icon	= QtGui.QIcon()
	icon.addPixmap(QtGui.QPixmap(f"{icon_folder}/history.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
	mw_ui.materials_and_products_widget.setTabIcon(4,icon)


	icon	= QtGui.QIcon()
	icon.addPixmap(QtGui.QPixmap(f"{icon_folder}/output.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
	mw_ui.add_rm_output.setIcon(icon)
	mw_ui.add_pm_output.setIcon(icon)
	mw_ui.menuExport.setIcon(icon)
	

	icon	= QtGui.QIcon()
	icon.addPixmap(QtGui.QPixmap(f"{icon_folder}/input.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
	mw_ui.add_rm_input.setIcon(icon)
	mw_ui.add_pm_input.setIcon(icon)


	icon	= QtGui.QIcon()
	icon.addPixmap(QtGui.QPixmap(f"{icon_folder}/export excel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
	mw_ui.export_excell_button.setIcon(icon)


	

	#delete icon
	mw_ui.delete_icon	= QtGui.QIcon()
	mw_ui.delete_icon.addPixmap(QtGui.QPixmap(f"{icon_folder}/delete.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
	mw_ui.delete_packed_product.setIcon(mw_ui.delete_icon)
	mw_ui.delete_unpacked_product.setIcon(mw_ui.delete_icon)
	mw_ui.delete_pm.setIcon(mw_ui.delete_icon)
	mw_ui.delete_rm.setIcon(mw_ui.delete_icon)
	mw_ui.delete_order.setIcon(mw_ui.delete_icon)
	mw_ui.clear_notifications.setIcon(mw_ui.delete_icon)


	#edit icon
	mw_ui.edit_icon	= QtGui.QIcon()
	mw_ui.edit_icon.addPixmap(QtGui.QPixmap(f"{icon_folder}/edit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
	mw_ui.edit_packed_product.setIcon(mw_ui.edit_icon)
	mw_ui.edit_unpacked_product.setIcon(mw_ui.edit_icon)
	mw_ui.edit_pm.setIcon(mw_ui.edit_icon)
	mw_ui.edit_rm.setIcon(mw_ui.edit_icon)
	mw_ui.edit_order.setIcon(mw_ui.edit_icon)


	#add icon
	mw_ui.add_icon	= QtGui.QIcon()
	mw_ui.add_icon.addPixmap(QtGui.QPixmap(f"{icon_folder}/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
	mw_ui.add_packed_product.setIcon(mw_ui.add_icon)
	mw_ui.add_unpacked_product.setIcon(mw_ui.add_icon)
	mw_ui.add_pm.setIcon(mw_ui.add_icon)
	mw_ui.add_rm.setIcon(mw_ui.add_icon)
	mw_ui.add_order.setIcon(mw_ui.add_icon)
	mw_ui.add_theme.setIcon(mw_ui.add_icon)
	mw_ui.add_language.setIcon(mw_ui.add_icon)
	mw_ui.actionNew.setIcon(mw_ui.add_icon)


	mw_ui.open_icon	= QtGui.QIcon()
	mw_ui.open_icon.addPixmap(QtGui.QPixmap(f"{icon_folder}/open.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
	mw_ui.actionOpen.setIcon(mw_ui.open_icon)

	#notification
	icon	= QtGui.QIcon()
	if mw_ui.notifications_mode:
		icon.addPixmap(QtGui.QPixmap(f"{icon_folder}/notifications +.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
	else:
		icon.addPixmap(QtGui.QPixmap(f"{icon_folder}/notifications.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
	mw_ui.tabWidget_2.setTabIcon(0,icon)

	del icon









       	

def view_late_orders(mw_ui):
	orders = database_controller.get_data(mw_ui.main_data_base , '"Order"', columns='planned_finishing_date,name', condition='where done = 0')
	for order in orders:
		if datetime.date.today()>datetime.date.fromisoformat(order[0]):
			mw_ui.notifications_mode = 1
			windows.notification(mw_ui,'ORDERS', f'You are late on "{order[1]}" order',1)


def view_rm_low_quantity(mw_ui,condition=''):
	rms = database_controller.get_data(mw_ui.main_data_base , 'RawMaterials', columns='name, quantity, unit, loq_quantity, loq_unit', condition=f'where loq_warning = 1 {condition}')

	for rm in rms:
		if  rm[1]*database_controller.material_units_convert[rm[2]]<rm[3]*database_controller.material_units_convert[rm[4]]:
			mw_ui.notifications_mode = 1
			windows.notification(mw_ui,'RAW MATERIALS', f'You have low quantity of "{rm[0]}" raw material',1)	

def view_pm_low_quantity(mw_ui,condition=''):
	pms = database_controller.get_data(mw_ui.main_data_base , 'PackingMaterial', columns='name, quantity, loq_quantity', condition=f'where loq_warning = 1 {condition}')
	for pm in pms:
		if  pm[1]<pm[2]:
			mw_ui.notifications_mode = 1
			windows.notification(mw_ui,'PACKING MATERIALS', f'You have low quantity of "{pm[0]}" packing material',1)	


def init(mw_ui):
	view_all_data(mw_ui)
	view_late_orders(mw_ui)
	view_rm_low_quantity(mw_ui)
	view_mw_icons(mw_ui)


def view_all_data(mw_ui):
	fill_out_list(mw_ui.counts_labels, mw_ui.main_data_base, mw_ui.rm_list 				, 'RawMaterials' 	, (1,3,4,5)  	,'{0}	({1})	({2} {3})'	, 0 )
	fill_out_list(mw_ui.counts_labels, mw_ui.main_data_base, mw_ui.pm_list 				, 'PackingMaterial' , (1,2,3,4)  	,'{0}	({1})	({2} {3})'	, 0 )
	fill_out_list(mw_ui.counts_labels, mw_ui.main_data_base, mw_ui.unpacked_product_list , 'UnpackedProduct' , (1,2,4,5)  	,'{0}	({1})	({2} {3})'	, 0 )
	fill_out_list(mw_ui.counts_labels, mw_ui.main_data_base, mw_ui.packed_product_list 	, 'PackedProduct' 	, (1,2)  		,'{0}	({1})'				, 0 )
	fill_out_mail_list(mw_ui ,mw_ui.counts_labels, mw_ui.main_data_base, mw_ui.inbox_mail 			, 'inbox_mail' 	)
	fill_out_mail_list(mw_ui ,mw_ui.counts_labels, mw_ui.main_data_base, mw_ui.outbox_mail 			, 'outbox_mail' 	)
	fill_out_orders_list(mw_ui)
	view_pm_low_quantity(mw_ui)
	view_all_orders(mw_ui)


	







def add_header_to_tableWidget(title,tableWidget,**data):
	tableWidget.setRowCount(tableWidget.rowCount()+1)
	item = QtWidgets.QTableWidgetItem()
	item.setText(title)
	for bit in data.keys():
		item.setData(int(bit[-1]),data[bit])

	tableWidget.setVerticalHeaderItem(tableWidget.rowCount()-1, item)

def add_order_to_orders_tables(mw_ui,date_from,date_to ,title , tooltip,current_year ,y):

	mw_ui.all_orders.setSpan(y,(date_from-datetime.date(current_year,1,1)).days  , 1 ,(date_to - date_from).days+1)
	current_col=(date_to - date_from).days

	item = QtWidgets.QTableWidgetItem()
	item.setText(title)


	now=datetime.date.today()

	if date_from <= now <= date_to:

		icon = QtGui.QIcon()
		icon.addPixmap(QtGui.QPixmap(f"icons/active.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		item.setIcon(icon)
	item.setTextAlignment(QtCore.Qt.AlignCenter)

	item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsDropEnabled|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
	item.setToolTip(tooltip)
	mw_ui.all_orders.setItem(mw_ui.all_orders.rowCount()-1 , (date_from-datetime.date(current_year,1,1)).days , item)



def view_all_orders(mw_ui):


	mw_ui.all_orders.setRowCount(0)
	mw_ui.all_orders.setColumnCount(0)

	add_header_to_tableWidget(title='Month',tableWidget=mw_ui.all_orders)


	current_year=mw_ui.orders_table_year.date().year()
	monthes_names=['Jan' ,'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']

	year_days_count=(datetime.date(current_year,12,monthrange(current_year , 12)[1])-datetime.date(current_year,1,1)).days+1
	mw_ui.all_orders.setColumnCount(year_days_count)

	for i in range(year_days_count):
		item = QtWidgets.QTableWidgetItem()
		item.setTextAlignment(QtCore.Qt.AlignCenter)
		mw_ui.all_orders.setItem(0, i, item)

	current_col=0



	for month in range(1,13):
		current_month_days=monthrange(current_year , month)[1]

		mw_ui.all_orders.setSpan(0,current_col,1,current_month_days)
		mw_ui.all_orders.item(0 , current_col).setText(f'{monthes_names[month-1]} ({current_month_days} DAY)')
		current_col+=current_month_days



	
	products = database_controller.get_data(mw_ui.main_data_base , 'PackedProduct', columns='name, id' )




	y=1
	for product in products:
		add_header_to_tableWidget(title=product[0],tableWidget=mw_ui.all_orders,data_4=product[1])

		orders=database_controller.get_data(mw_ui.main_data_base , '"Order"', condition=f'where packed_product={product[1]}' )

		current_col=0
		for order in orders:
			add_order_to_orders_tables(mw_ui,datetime.date.fromisoformat(order[5]),datetime.date.fromisoformat(order[6]) ,order[1] , f'{order[1]} \n from {order[5]} \n to {order[6]} \n ',current_year ,y)

		y+=1#(id integer primary key autoincrement, name, product_id, quantity, unit_id, done, date_from, date_to)
	