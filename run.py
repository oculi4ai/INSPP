from PyQt5 import QtCore, QtGui, QtWidgets, uic
from models import functions, database_controller, languages
import sys, os
from types import MethodType
import threading
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import *
import threading
import time
from models.styles import *
import sqlite3 as sq
import configparser, notify2
from models import windows,dictionary,translation
import requests, json
from PyQt5.QtGui import *



config = configparser.ConfigParser()
config.read('settings.ini')

app = QtWidgets.QApplication(sys.argv)


def open_main_window(database,loading_ui):
	
	def progressbar_val(val,about):
		loading_ui.msg.setText(about)
		loading_ui.progressBar.setValue(val)




	threading.Thread(target=progressbar_val , args=(5,'Creating Window...') ).start()
	MainWindow = QtWidgets.QMainWindow()
	
	ui2 =uic.loadUi('windows/main_window.ui', MainWindow)
	
	windows.watting_window(ui2,'detail')
	

	ui2.session = requests.Session()
	
	main_style = styles['ui_style']

	ui2.logged_in=False
	ui2.notifications_mode=0
	ui2.important_notifications_count=0
	ui2.notifications_sound=0
	ui2.notifications_popup=0
	ui2.auto_backup = config['settings']['auto_backup']
	ui2.backup_term = 1
	
	ui2.main_data_base=database
	ui2.current_style=styles[config['settings']['style']]+main_style
	






	ui2.counts_labels={
		'RawMaterials':ui2.rm_label,
		'PackingMaterial':ui2.pm_label,
		'UnpackedProduct':ui2.upp_label,
		'PackedProduct':ui2.pp_label,
		'"Order"':ui2.orders_label,
		'inbox_mail':ui2.inbox_count,
		'outbox_mail':ui2.outbox_count,
	}

	ui2.backup_tables={
					'products' 				:'name,code,material_type',
					'raw_materials'			:'name,type,code,quantity,unit,density',
					'packing_materials'		:'name,code,quantity,unit',
					'product_raw_materials'	:'product_id,material_id,t_quantity,t_unit,m_quantity,m_unit, percentage',
					'orders'				:'name,product_id,quantity,unit_id,done,date_from,date_to',
					
					'units'					:'name,product_id,value,unit_id,is_standard ',
					'material_types'		:'type,units_ids',
					'backups'				:'date,location'}
	ui2.open=True
	
	threading.Thread(target=progressbar_val , args=(10,'Checking Database...') ).start()
	database_controller.check_database(database)
	functions.init(ui2 ,MainWindow,loading_ui)
	threading.Thread(target=progressbar_val , args=(80,'Creating Window...') ).start()
	MainWindow.showMaximized()


	names = json.loads(config['settings']['mail_users'])
	completer = QCompleter(names)
	ui2.mail_to.setCompleter(completer)	

	subjects = json.loads(config['settings']['mail_subjects'])
	completer1 = QCompleter(subjects)
	ui2.mail_subject.setCompleter(completer1)	

	ui2.setStyleSheet(styles[config['settings']['style']]+main_style)
	font_family = config['settings']['font_family']
	font = QFont()
	font.setFamily(font_family)
	ui2.setFont(font)

	ui2.centralwidget.setStyleSheet(f'font-family:{font_family};')
	ui2.menuBar.setStyleSheet(f'font-family:{font_family};')
	ui2.dockWidget.setStyleSheet(f'font-family:{font_family};')
	ui2.dockWidget_2.setStyleSheet(f'font-family:{font_family};')
	ui2.statusBar.setStyleSheet(f'font: 8pt {font_family};')

	ui2.setStyleSheet(styles[config['settings']['style']]+main_style)

	translation.translate_main_window(ui2, dictionary.languages[config['settings']['current_language']]  )


	MainWindow.show()
	
	

	def exit_app():
		ui2.open=False

	def closeEvent(self, event):
	            close = QtWidgets.QMessageBox.question(self,
	                                         "QUIT",
	                                         dictionary.languages[config['settings']['current_language']]['Are you sure want to EXIT?'],
	                                         QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No )
	            if close == QtWidgets.QMessageBox.Yes:
	                event.accept()
	                for window in app.allWindows():

	                    window.close()
	            else:
	                event.ignore()

	MainWindow.closeEvent = MethodType(closeEvent,MainWindow)
	ui2.setWindowTitle(f'{database} | INS Production Plan')
	MainWindow.setWindowTitle(f'{database} | INS Production Plan')

	app.aboutToQuit.connect(exit_app)
	threading.Thread(target=progressbar_val , args=(100,'INS Production Plan Ready') ).start()
	def closing_loading_window():
		time.sleep(1)
		loading_win.close()
		loading_win.destroy()
		
		config = configparser.ConfigParser()
		config.read('settings.ini')
		
		ui2.notifications_sound=int(config['settings']['notification_sound'])
		ui2.notifications_popup=int(config['settings']['notification_popup'])
		if ui2.important_notifications_count:
			notifications_count_warning=f'\nYou have {ui2.important_notifications_count} notification please check your notifications section'
		else:
			notifications_count_warning=''
		windows.notification(ui2,'Wellcome', f'Wellcome to INS production plan {notifications_count_warning}')
		

		
	threading.Thread(target=closing_loading_window ).start()


# loading window
dictionary.fill_out_dicionary()
loading_win = QtWidgets.QWidget()
l_ui =uic.loadUi('windows/loading_program.ui', loading_win)

lang = config['settings']['current_language']
l_ui.open.setText(dictionary.languages[lang]['open file'])
l_ui.create.setText(dictionary.languages[lang]['create new file'])

loading_win.setWindowModality(QtCore.Qt.ApplicationModal)
loading_win.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

qtRectangle = loading_win.frameGeometry()
centerPoint = QDesktopWidget().availableGeometry().center()
qtRectangle.moveCenter(centerPoint)
loading_win.move(qtRectangle.topLeft())
loading_win.setAttribute(Qt.WA_TranslucentBackground)
style=config['settings']['style']
current_style=styles[style]+main_style
font_family = config['settings']['font_family']
font_family_style = '''#MainWindow , QWidget {
    font-family : "'''+font_family +'''";
}'''
loading_win.setStyleSheet(font_family_style+current_style+'''#frame{

background-image: url("covers/loading-cover-''' + style + '''.jpg");
        background-repeat: no-repeat;
        background-position: center;

}''')

loading_win.setAttribute(QtCore.Qt.WA_DeleteOnClose)
notify2.init('INP Production Plan')
loading_win.show()
def open_INSPP_file():

	file_name=QFileDialog.getOpenFileName(l_ui,"create INSPP file",config['settings']['last_opened_location'],"INS PP Files (*.INSPP)")
	
	if len(file_name[1])>0:
		l_ui.open.setVisible(False)
		l_ui.create.setVisible(False)
		l_ui.exit.setVisible(False)
		config['settings']['last_opened_location']=file_name[0]
		config.write(open('settings.ini','w'))
		open_main_window(file_name[0],l_ui)

def create_INSPP_file():# open create exit

	file_name=QFileDialog.getSaveFileName(l_ui,"create INSPP file",config['settings']['last_opened_location'],"INS PP Files (*.INSPP)")
	
	if len(file_name[1])>0:
		l_ui.open.setVisible(False)
		l_ui.create.setVisible(False)
		l_ui.exit.setVisible(False)
		config['settings']['last_opened_location']=file_name[0]
		config.write(open('settings.ini','w'))
		open_main_window(file_name[0]+'.INSPP',l_ui)


l_ui.exit.clicked.connect(lambda:loading_win.close())
l_ui.open.clicked.connect(open_INSPP_file)
l_ui.create.clicked.connect(create_INSPP_file)




sys.exit(app.exec_())
