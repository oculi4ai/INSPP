from models.INSClient import ins_logout
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtChart import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from pyqtgraph import PlotWidget, plot
import sqlite3 as sq
import os
import datetime
import sys
from calendar import monthrange
import openpyxl
from models.windows import *
from models.languages import languages
import json
import pyqtgraph as pg
import random
import threading
import time
from models.styles import *
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtGui import QIcon
from models.styles import styles ,main_style
from models.messages import *
import configparser
from models import views, windows, translation, dictionary
import configparser
import io

def backup_timer(mw_ui):
	config = configparser.ConfigParser()
	config.read('settings.ini')
	backups = database_controller.get_data(mw_ui.main_data_base , 'backups', columns='date'  )
	backup_every_seconds = int(config['settings']['backup_year'])*31536000 + int(config['settings']['backup_month'])*2592000  + int(config['settings']['backup_day'])*86400 + int(config['settings']['backup_hour'])*3600 
	if len(backups)>0:
		last_backup_date = backups[-1][0]
		sleep_time = backup_every_seconds - (datetime.datetime.now() - datetime.datetime.fromisoformat(last_backup_date)).total_seconds()
	else:
		sleep_time = backup_every_seconds
	while mw_ui.isVisible() and mw_ui.auto_backup and sleep_time>0:
		time.sleep(mw_ui.backup_term)
		sleep_time-=mw_ui.backup_term
	if sleep_time<=0 and mw_ui.isVisible() :

		#watting_window = windows.watting_window(mw_ui,'<html><head/><body><p align="center">creating Backup...<br/><span style=" font-size:16pt;">please wait </span></p></body></html>')
		mw_ui.watting_ui.detail.setText('<html><head/><body><p align="center">creating Backup...<br/><span style=" font-size:16pt;">please wait </span></p></body></html>')
		mw_ui.watting_ui.show()
		
		time.sleep(5)#to make sure all operations stoped
		conn = sq.connect(mw_ui.main_data_base)

		with io.open(os.path.join(config['settings']['backup_location'],f'{datetime.datetime.now().isoformat()}.INSPP'), 'w') as f:
   			for linha in conn.iterdump():
   				f.write('%s\n' % linha)
		conn.close()
		database_controller.add(mw_ui, 'backups', [datetime.datetime.now().isoformat(),os.path.join(config['settings']['backup_location'],f'{datetime.datetime.now().isoformat()}.INSPP' )])
		mw_ui.watting_ui.hide()
		backup_timer(mw_ui)









def init(mw_ui,mw,loading_ui):
	config = configparser.ConfigParser()
	config.read('settings.ini')
	def progressbar_val(val,about,loading_ui=loading_ui):
		loading_ui.progressBar.setValue(val)
		loading_ui.msg.setText(about)

	mw_ui.orders_table_year.setDate( datetime.date.today() )

	# status bar 
	mw_ui.statusBar.setContentsMargins(0, 0, 0, 0)

	widget221 = QFrame()
	horizontalLayout_2 = QHBoxLayout(widget221)
	horizontalLayout_2.setObjectName(u"horizontalLayout_2")
	horizontalLayout_2.setSpacing(17)
	horizontalLayout_2.setContentsMargins(0, 0, 0, 0)

	widget221.setObjectName('statusbar_layout')
	widget221.setStyleSheet('''#statusbar_layout {background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 0, 0, 0), stop:1 rgba(255, 255, 255, 0));font: 8pt "Ubuntu";} ''')
	

	mw_ui.statusBar.setMinimumSize(QSize(0, 25))
	mw_ui.statusBar.setMaximumSize(QSize(16777215, 25))
	
	mw_ui.movie = QMovie("GIFs/loading.gif")
	mw_ui.loading_gif = QLabel()
	mw_ui.loading_gif.setMinimumSize(QSize(17, 17))
	mw_ui.loading_gif.setMaximumSize(QSize(17, 17))
	mw_ui.loading_gif.setScaledContents(True)
	mw_ui.loading_gif.setMovie(mw_ui.watting_ui.movie)
	mw_ui.loading_gif.show()
	mw_ui.movie.start()
	horizontalLayout_2.addWidget(mw_ui.loading_gif)


	mw_ui.INS_LOGO_SB = QLabel()
	mw_ui.INS_LOGO_SB.setToolTip('INS Server\nconnected')
	mw_ui.INS_LOGO_SB.setObjectName(u"label")
	mw_ui.INS_LOGO_SB.setGeometry(QRect(230, 150, 21, 21))
	mw_ui.INS_LOGO_SB.setPixmap(QPixmap("icons/INSS_logo.png"))
	mw_ui.INS_LOGO_SB.setScaledContents(True)
	mw_ui.INS_LOGO_SB.setMinimumSize(QSize(23, 23))
	mw_ui.INS_LOGO_SB.setMaximumSize(QSize(23, 23))
	mw_ui.INS_LOGO_SB.hide()
	horizontalLayout_2.addWidget(mw_ui.INS_LOGO_SB)

	
	mw_ui.username_label = QLabel('')
	horizontalLayout_2.addWidget(mw_ui.username_label)



	




	horizontalLayout_2.addWidget(QLabel(''))
	
	mw_ui.add_theme = QPushButton()
	mw_ui.add_theme.setMinimumSize(QSize(20, 20))
	mw_ui.add_theme.setMaximumSize(QSize(20, 20))

	horizontalLayout_2.addWidget(mw_ui.add_theme )
	mw_ui.themes_combobox = QComboBox()
	horizontalLayout_2.addWidget(mw_ui.themes_combobox )


	mw_ui.add_language = QPushButton()
	mw_ui.add_language.setMinimumSize(QSize(20, 20))
	mw_ui.add_language.setMaximumSize(QSize(20, 20))

	horizontalLayout_2.addWidget(mw_ui.add_language )
	mw_ui.languages_combobox = QComboBox()
	horizontalLayout_2.addWidget(mw_ui.languages_combobox )#

	mw_ui.font_combobox = QFontComboBox()
	mw_ui.font_combobox.setEditable(False)
	font = QFont()
	font.setFamily(config['settings']['font_family'])
	
	mw_ui.font_combobox.setCurrentFont(font)
	mw_ui.font_combobox.setStyleSheet('font-family:none;')
	horizontalLayout_2.addWidget(mw_ui.font_combobox )

	mw_ui.statusBar.addWidget(widget221, 1)
	mw_ui.statusBar.setContentsMargins(0, 0, 0, 0)
	widget221.setContentsMargins(0, 0, 0, 0)
	horizontalLayout_2.setStretch(0, 1)
	horizontalLayout_2.setStretch(1, 1)
	horizontalLayout_2.setStretch(2, 1)
	horizontalLayout_2.setStretch(3, 20)
	horizontalLayout_2.setStretch(4, 1)
	horizontalLayout_2.setStretch(5, 2)
	horizontalLayout_2.setStretch(6, 1)
	horizontalLayout_2.setStretch(7, 2)
	horizontalLayout_2.setStretch(8, 2)





	
	threading.Thread(target=progressbar_val , args=(20,'View Data...') ).start()
	views.init(mw_ui)
	threading.Thread(target=progressbar_val , args=(40,'Create Window Connection...') ).start()
	btns_connections(mw_ui)
	threading.Thread(target=progressbar_val , args=(50,'Get backup setting...') ).start()
	config = configparser.ConfigParser()
	config.read('settings.ini')
	if int(config['settings']['auto_backup']):

		threading.Thread(target=backup_timer, args=(mw_ui,)).start()

	languages_files = os.listdir('languages')
	
	config = configparser.ConfigParser()
	config.read('settings.ini')
	a=0
	for lang in languages_files:

		if lang[len(lang)-2:]=='py':
			
			lang_model_name = lang.split('.')[0]
			language_file = __import__(f'languages.{lang_model_name}', fromlist=['object'])
			mw_ui.languages_combobox.addItem(language_file.Language_view_name,language_file.language_shortcut)
			if config['settings']['current_language'] == language_file.language_shortcut:
				mw_ui.languages_combobox.setCurrentIndex(a)
			a=a+1

	
	#styles
	#mw_ui.themes_combobox.clear()
	index_ = 0
	config = configparser.ConfigParser()
	config.read('settings.ini')
	current_style_name = config['settings']['style']
	print(dir(mw_ui.themes_combobox))
	for style in styles.keys():
		if style != 'ui_style':
			mw_ui.themes_combobox.addItem(style.replace('_',' ').title())
			index_+=1
			if current_style_name == style:
				
				mw_ui.themes_combobox.setCurrentIndex(index_-1)
			




def send_mail(mw_ui):
	if mw_ui.logged_in:
		config = configparser.ConfigParser()
		config.read('settings.ini')
		url = config['login-settings']['url']+config['URLs']['sendmail']
		data={
			'user_to' 	: mw_ui.mail_to.text(),
			'subject' 	: mw_ui.mail_subject.text(),
			'body' 		: mw_ui.mail_body.toPlainText(),
		}

		users= json.loads(config['settings']['mail_users'])
		if mw_ui.mail_to.text() not in users:
			config['settings']['mail_users'] = json.dumps(users+[mw_ui.mail_to.text(),])

		subjects= json.loads(config['settings']['mail_subjects'])
		if mw_ui.mail_to.text() not in subjects:
			config['settings']['mail_subjects'] = json.dumps(users+[mw_ui.mail_subject.text(),])

		config.write(open('settings.ini','w'))

		INSClient.fill_out_form(mw_ui.session,url,data,op_type = 'create')
		mw_ui.mail_to.setText('')
		mw_ui.mail_subject.setText('')
		mw_ui.mail_body.clear()

		names = json.loads(config['settings']['mail_users'])
		completer = QCompleter(names)
		mw_ui.mail_to.setCompleter(completer)	

		subjects = json.loads(config['settings']['mail_subjects'])
		completer1 = QCompleter(subjects)
		mw_ui.mail_subject.setCompleter(completer1)	
		

	else:
		windows.notification(mw_ui , 'INS Server' , 'Please login to INS server before you send an email')
	


def change_style(mw_ui):
	try:
		style = mw_ui.themes_combobox.currentText().lower().replace(' ','_')
		config = configparser.ConfigParser()
		config.read('settings.ini')
		config['settings']['style']=style
		config.write(open('settings.ini','w'))
		mw_ui.setStyleSheet(styles[style]+main_style)
		mw_ui.current_style=styles[style]+main_style
		views.view_mw_icons(mw_ui)
	except:
		pass
	


def clear_notifications(mw_ui):
	config = configparser.ConfigParser()
	config.read('settings.ini')
	icon	= QtGui.QIcon()
	icon_folder=config['icons themes folders'][config['settings']['style']]
	icon.addPixmap(QtGui.QPixmap(f"{icon_folder}/notifications.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
	mw_ui.tabWidget_2.setTabIcon(0,icon)
	mw_ui.tabWidget_2.setTabText(0,'')
	mw_ui.notifications_mode=0
	mw_ui.important_notifications_count=0

def change_language(mw_ui, lang):
	try:
		config = configparser.ConfigParser()
		config.read('settings.ini')
		config['settings']['current_language']=lang.currentData()
		config.write(open('settings.ini','w'))
		translation.translate_main_window(mw_ui, dictionary.languages[lang.currentData()]  )
	except:
		pass

def AddLanguage(mw_ui):
	file_name=QFileDialog.getOpenFileName(mw_ui,"Add language")
	open(os.path.join('languages',os.path.split(file_name[0])[1] ), 'w').write(open(file_name[0], 'r').read())


def open_inspp_file(mw_ui):
    mw_ui.loading_gif.show()
    file_name = QFileDialog.getOpenFileName(mw_ui,"open INSPP file","","INSPP files (*.INSPP)")
    if file_name[0] != '':
        mw_ui.logged_in = False
        mw_ui.INS_LOGO_SB.hide()
        mw_ui.username_label.setText('')
        mw_ui.main_data_base = file_name[0]
        mw_ui.setWindowTitle(f'{mw_ui.main_data_base} | INS Production Plan')
        database_controller.check_database(mw_ui.main_data_base)
        clear_notifications(mw_ui)
        views.view_all_data(mw_ui)
        views.view_late_orders(mw_ui)
        views.view_rm_low_quantity(mw_ui)
		
    mw_ui.loading_gif.hide()


def change_font_family(mw_ui):
	config = configparser.ConfigParser()
	config.read('settings.ini')
	config['settings']['font_family'] = mw_ui.font_combobox.currentFont().family()

	font_family = mw_ui.font_combobox.currentFont().family()
	mw_ui.centralwidget.setStyleSheet(f'font-family:{font_family};')
	mw_ui.menuBar.setStyleSheet(f'font-family:{font_family};')
	mw_ui.dockWidget.setStyleSheet(f'font-family:{font_family};')
	mw_ui.dockWidget_2.setStyleSheet(f'font-family:{font_family};')
	mw_ui.statusBar.setStyleSheet(f'font: 8pt {font_family};')

	
	config.write(open('settings.ini','w'))

def create_inspp_file(mw_ui):
	mw_ui.loading_gif.show()
	file_name = QFileDialog.getSaveFileName(mw_ui,"open INSPP file","","INSPP files (*.INSPP)")
	if file_name[0] != '':
		mw_ui.logged_in = False
		mw_ui.INS_LOGO_SB.hide()
		mw_ui.username_label.setText('')
		mw_ui.main_data_base = file_name[0]+'.INSPP'
		mw_ui.setWindowTitle(f'{mw_ui.main_data_base} | INS Production Plan')
		database_controller.check_database(mw_ui.main_data_base)
		clear_notifications(mw_ui)
		views.view_all_data(mw_ui)
		views.view_late_orders(mw_ui)
		views.view_rm_low_quantity(mw_ui)
		
	mw_ui.loading_gif.hide()

def ins_login_action(mw_ui):
	if mw_ui.logged_in:
		ins_logout(mw_ui)
	else:
		ins_login(mw_ui)


def btns_connections(mw_ui):

	#actions #
	mw_ui.export_excell_button.triggered.connect(			lambda: open_export_excell(mw_ui))
	mw_ui.actionSettings.triggered.connect(					lambda:OpenSettingsWindow(mw_ui))
	mw_ui.actionChange_Language.triggered.connect(			lambda:OpenChangeLanguageWindow(mw_ui))#actionAdd_language
	mw_ui.actionAdd_language.triggered.connect(				lambda:AddLanguage(mw_ui))
	mw_ui.actionEnglish.triggered.connect(					lambda:change_language(mw_ui,'en'))
	mw_ui.actionArabic.triggered.connect(					lambda:change_language(mw_ui,'ar'))
	mw_ui.actionINS.triggered.connect(						lambda:ins_login_action(mw_ui))
	mw_ui.themes_combobox.currentIndexChanged.connect(		lambda:change_style(mw_ui))
	mw_ui.actionOpen.triggered.connect(						lambda:open_inspp_file(mw_ui))
	mw_ui.actionNew.triggered.connect(						lambda:create_inspp_file(mw_ui))
	mw_ui.font_combobox.currentFontChanged.connect(		lambda:change_font_family(mw_ui))

	



	#add buttons
	mw_ui.add_rm.clicked.connect(				lambda: open_add_rm_window(mw_ui))
	mw_ui.add_pm.clicked.connect(				lambda: open_add_pm_window(mw_ui))
	mw_ui.add_unpacked_product.clicked.connect(	lambda: open_add_unpacked_product_window(mw_ui))
	mw_ui.add_packed_product.clicked.connect(	lambda: open_add_packed_product_window(mw_ui))
	mw_ui.add_order.clicked.connect(			lambda: open_add_order_window(mw_ui))
	mw_ui.add_rm_output.clicked.connect(		lambda: open_add_output_rm_window(mw_ui))
	mw_ui.add_rm_input.clicked.connect(			lambda: open_add_input_rm_window(mw_ui))
	mw_ui.add_pm_output.clicked.connect(		lambda: open_add_output_pm_window(mw_ui))
	mw_ui.add_pm_input.clicked.connect(			lambda: open_add_input_pm_window(mw_ui))
	mw_ui.add_language.clicked.connect(			lambda: AddLanguage(mw_ui))
	mw_ui.send_mail.clicked.connect(			lambda: send_mail(mw_ui))
	
#
	#edit buttons
	mw_ui.edit_rm.clicked.connect(					lambda: open_edit_rm_window(mw_ui))
	mw_ui.edit_pm.clicked.connect(					lambda: open_edit_pm_window(mw_ui))
	mw_ui.edit_unpacked_product.clicked.connect(	lambda: open_edit_up_window(mw_ui))
	mw_ui.edit_packed_product.clicked.connect(		lambda: open_edit_packed_product_window(mw_ui))
	mw_ui.edit_order.clicked.connect(				lambda: open_edit_order_window(mw_ui))
	mw_ui.inbox_mail.clicked.connect(				lambda: open_mail_window(mw_ui , 'inbox'))
	mw_ui.outbox_mail.clicked.connect(				lambda: open_mail_window(mw_ui, 'outbox'))


	#delete buttons
	mw_ui.delete_rm.clicked.connect(				lambda: delete_item(mw_ui,	'RawMaterials' 		,mw_ui.rm_list.currentItem() 				) )
	mw_ui.delete_pm.clicked.connect(				lambda: delete_item(mw_ui,	'PackingMaterial'	,mw_ui.pm_list.currentItem() 				) )
	mw_ui.delete_unpacked_product.clicked.connect(	lambda: delete_item(mw_ui, 	'UnpackedProduct'	,mw_ui.unpacked_product_list.currentItem()	) )
	mw_ui.delete_packed_product.clicked.connect(	lambda: delete_item(mw_ui, 	'PackedProduct'		,mw_ui.packed_product_list.currentItem()  	) )
	mw_ui.delete_order.clicked.connect(				lambda: delete_order(mw_ui,	mw_ui.orders_list.currentItem() 			) )
	mw_ui.clear_notifications.clicked.connect(		lambda: clear_notifications(mw_ui))


	#select 
	def open_file_or_folder(mw_ui):
		if mw_ui.drive_list.currentItem().data(5) == 'folder':
			INSClient.open_drive_folder(mw_ui, folder_pk= mw_ui.drive_list.currentItem().data(4))

	mw_ui.drive_list.clicked.connect(lambda: open_file_or_folder(mw_ui))




	mw_ui.languages_combobox.currentIndexChanged.connect(lambda: functions.change_language(mw_ui,mw_ui.languages_combobox))


