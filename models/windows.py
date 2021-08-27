from types import MethodType
from tkinter import *
import sqlite3 as sq
import datetime
from models import functions
from PyQt5 import QtCore, QtGui, QtWidgets , uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie
from models import functions , synch_center
from models.languages import languages
from models.translation import *
import sys
import sh
import socket
import threading
import time, datetime
from PyQt5.QtWidgets import QFileDialog,QDesktopWidget
from openpyxl import Workbook
from models import INSClient
import requests,configparser
from models import database_controller, views, functions, translation,dictionary
from playsound import playsound
import ctypes
import notify2 , os



def confirmCloseEvent(self, event):
	config = configparser.ConfigParser()
	config.read('settings.ini')
	if self.saved:
		event.accept()
	else:
	            close = QtWidgets.QMessageBox.question(self,
	                                         "QUIT",
											 dictionary.languages[config['settings']['current_language']]["Are you sure want to close this window?"],
	                                         QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No )
	            if close == QtWidgets.QMessageBox.Yes:
	                event.accept()
	            else:
	                event.ignore()


#####################################################
############ ADD DATA windows #######################
#####################################################
#>

def open_add_rm_window(mw_ui):

	mw_ui.add_rm_window = QtWidgets.QDialog()
	mw_ui.add_rm_window.setWindowModality(QtCore.Qt.ApplicationModal)
	mw_ui.open_add_rm_ui = uic.loadUi('windows/AddRawMaterial.ui', mw_ui.add_rm_window )
	mw_ui.open_add_rm_ui.setStyleSheet(mw_ui.current_style)
	mw_ui.open_add_rm_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)

	mw_ui.open_add_rm_ui.add_rm.setIcon(mw_ui.add_icon)


	config = configparser.ConfigParser()
	config.read('settings.ini')

	translation.retranslate_add_rm_window(mw_ui.open_add_rm_ui , dictionary.languages[config['settings']['current_language']])
	if config['settings']['current_language']=='ar':
		mw_ui.open_add_rm_ui.setLayoutDirection(QtCore.Qt.RightToLeft)
	else:
		mw_ui.open_add_rm_ui.setLayoutDirection(QtCore.Qt.LeftToRight)

	# view material types
	con=sq.connect(mw_ui.main_data_base)
	for m_type in database_controller.material_types.keys():
		mw_ui.open_add_rm_ui.material_type.addItem(m_type)


	def view_rm_units():
		mw_ui.open_add_rm_ui.rm_units_combo.clear()
		mw_ui.open_add_rm_ui.loq_units.clear()
		for unit in database_controller.material_types[mw_ui.open_add_rm_ui.material_type.currentText().lower()]:
			mw_ui.open_add_rm_ui.rm_units_combo.addItem(unit)
			mw_ui.open_add_rm_ui.loq_units.addItem(unit)

	view_rm_units()
	mw_ui.open_add_rm_ui.material_type.currentIndexChanged.connect(view_rm_units)

	def call_add_rm_function():
		mw_ui.add_rm_window.close()

		database_controller.add(mw_ui , 'RawMaterials' , 
										(
													mw_ui.open_add_rm_ui.material_name.text(),
													mw_ui.open_add_rm_ui.material_type.currentText(),
													mw_ui.open_add_rm_ui.material_code.text(),
													mw_ui.open_add_rm_ui.rm_quantity.value(),
													mw_ui.open_add_rm_ui.rm_units_combo.currentText(),
													mw_ui.open_add_rm_ui.rm_density.value(),
													mw_ui.open_add_rm_ui.loq_warning.isChecked(),
													mw_ui.open_add_rm_ui.loq_quantity.value(),
													mw_ui.open_add_rm_ui.loq_units.currentText(),
										))
		views.fill_out_list(mw_ui.counts_labels,mw_ui.main_data_base, mw_ui.rm_list 				, 'RawMaterials' 	, (1,3,4,5)  	,'{0}	({1})	({2} {3})'	, 0 )
	

	

	mw_ui.open_add_rm_ui.add_rm.clicked.connect(call_add_rm_function)
	mw_ui.add_rm_window.show()

def open_add_output_rm_window(mw_ui):

	try:
		units = database_controller.material_types[database_controller.get_data(mw_ui.main_data_base,'RawMaterials', columns='m_type', condition=f'where id = {mw_ui.rm_list.currentItem().data(4)}')[0][0].lower()]
		mw_ui.add_rm_output_window = QtWidgets.QDialog()
		mw_ui.add_rm_output_window.setWindowModality(QtCore.Qt.ApplicationModal)
		mw_ui.open_add_rm_output_ui = uic.loadUi('windows/add_rm_output.ui', mw_ui.add_rm_output_window )
		mw_ui.open_add_rm_output_ui.setStyleSheet(mw_ui.current_style)
		mw_ui.open_add_rm_output_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		config = configparser.ConfigParser()
		config.read('settings.ini')
		icon_folder=config['icons themes folders'][config['settings']['style']]
		mw_ui.add_icon	= QtGui.QIcon()
		mw_ui.add_icon.addPixmap(QtGui.QPixmap(f"{icon_folder}/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		mw_ui.open_add_rm_output_ui.add.setIcon(mw_ui.add_icon)

		for unit in units :
				mw_ui.open_add_rm_output_ui.unit.addItem(unit)
		
		def add_output():
			mw_ui.open_add_rm_output_ui.close()
			material = database_controller.get_data(mw_ui.main_data_base,'RawMaterials', columns='quantity,unit,m_type', condition=f'where id = {mw_ui.rm_list.currentItem().data(4)}')[0]
			if material[0]* database_controller.material_units_convert[material[1]] >= mw_ui.open_add_rm_output_ui.quantity.value()* database_controller.material_units_convert[mw_ui.open_add_rm_output_ui.unit.currentText()]:
				new_quantity = material[0]* database_controller.material_units_convert[material[1]] - mw_ui.open_add_rm_output_ui.quantity.value()* database_controller.material_units_convert[mw_ui.open_add_rm_output_ui.unit.currentText()]
				if material[2].upper()=='SOLID':
					unit='G'
				else:
					unit='L'
				new_quantity=database_controller.convert_to_best_unit(new_quantity, unit, material[2])
				database_controller.add(mw_ui , 'RawMaterialsOutput' , 
											(
														mw_ui.rm_list.currentItem().data(4), 
														mw_ui.open_add_rm_output_ui.quantity.value(), 
														mw_ui.open_add_rm_output_ui.unit.currentText(),
														mw_ui.open_add_rm_output_ui.date.date().toPyDate().isoformat(),
														mw_ui.open_add_rm_output_ui.note.toPlainText(),
														
											))
				database_controller.edit_specific_field(mw_ui,'RawMaterials',f'quantity = {new_quantity[0]} , unit = "{new_quantity[1]}"',mw_ui.rm_list.currentItem().data(4))
				views.fill_out_list(mw_ui.counts_labels, mw_ui.main_data_base, mw_ui.rm_list 				, 'RawMaterials' 	, (1,3,4,5)  	,'{0}	({1})	({2} {3})'	, 0 )

			else:
				notification(mw_ui,'NO ENOUGH QUANTITY', f'There is no enough qunatity to make this output')

		mw_ui.open_add_rm_output_ui.add.clicked.connect(add_output)
		mw_ui.open_add_rm_output_ui.show()
	except:
		notification(mw_ui,'NO ITEM SELECTED', f'Plaese select item to output')

def open_add_input_rm_window(mw_ui):

	try:
		units = database_controller.material_types[database_controller.get_data(mw_ui.main_data_base,'RawMaterials', columns='m_type', condition=f'where id = {mw_ui.rm_list.currentItem().data(4)}')[0][0].lower()]
		mw_ui.add_rm_input_window = QtWidgets.QDialog()
		mw_ui.add_rm_input_window.setWindowModality(QtCore.Qt.ApplicationModal)
		mw_ui.open_add_rm_input_ui = uic.loadUi('windows/add_rm_input.ui', mw_ui.add_rm_input_window )
		mw_ui.open_add_rm_input_ui.setStyleSheet(mw_ui.current_style)
		mw_ui.open_add_rm_input_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		config = configparser.ConfigParser()
		config.read('settings.ini')
		icon_folder=config['icons themes folders'][config['settings']['style']]
		mw_ui.add_icon	= QtGui.QIcon()
		mw_ui.add_icon.addPixmap(QtGui.QPixmap(f"{icon_folder}/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		mw_ui.open_add_rm_input_ui.add.setIcon(mw_ui.add_icon)

		for unit in units :
				mw_ui.open_add_rm_input_ui.unit.addItem(unit)
		
		def add_output():
			mw_ui.open_add_rm_input_ui.close()
			material = database_controller.get_data(mw_ui.main_data_base,'RawMaterials', columns='quantity,unit,m_type', condition=f'where id = {mw_ui.rm_list.currentItem().data(4)}')[0]
			
			new_quantity = material[0]* database_controller.material_units_convert[material[1]] + mw_ui.open_add_rm_input_ui.quantity.value()* database_controller.material_units_convert[mw_ui.open_add_rm_input_ui.unit.currentText()]
			if material[2].upper()=='SOLID':
					unit='G'
			else:
					unit='L'
			new_quantity=database_controller.convert_to_best_unit(new_quantity, unit, material[2])
			database_controller.add(mw_ui , 'RawMaterialsInput' , 
											(
														mw_ui.rm_list.currentItem().data(4), 
														mw_ui.open_add_rm_input_ui.quantity.value(), 
														mw_ui.open_add_rm_input_ui.unit.currentText(),
														mw_ui.open_add_rm_input_ui.date.date().toPyDate().isoformat(),
														mw_ui.open_add_rm_input_ui.note.toPlainText(),
														
											))
			database_controller.edit_specific_field(mw_ui,'RawMaterials',f'quantity = {new_quantity[0]} , unit = "{new_quantity[1]}"',mw_ui.rm_list.currentItem().data(4))
			views.fill_out_list(mw_ui.counts_labels, mw_ui.main_data_base, mw_ui.rm_list 				, 'RawMaterials' 	, (1,3,4,5)  	,'{0}	({1})	({2} {3})'	, 0 )

		mw_ui.open_add_rm_input_ui.add.clicked.connect(add_output)
		mw_ui.open_add_rm_input_ui.show()
	except:
		notification(mw_ui,'NO ITEM SELECTED', f'Plaese select item to input')




def open_add_pm_window(mw_ui):

	mw_ui.add_pm_window =QtWidgets.QDialog()
	mw_ui.add_pm_window.setWindowModality(QtCore.Qt.ApplicationModal)
	mw_ui.add_pm_ui = uic.loadUi('windows/AddPackingMaterial.ui', mw_ui.add_pm_window)
	mw_ui.add_pm_ui.setStyleSheet(mw_ui.current_style)
	mw_ui.add_pm_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
	mw_ui.add_pm_ui.add_pm.setIcon(mw_ui.add_icon)
	
	config = configparser.ConfigParser()
	config.read('settings.ini')

	translation.retranslate_add_pm_window(mw_ui.add_pm_ui , dictionary.languages[config['settings']['current_language']])
	if config['settings']['current_language']=='ar':
		mw_ui.add_pm_ui.setLayoutDirection(QtCore.Qt.RightToLeft)
	else:
		mw_ui.add_pm_ui.setLayoutDirection(QtCore.Qt.LeftToRight)

	def call_add_pm():
		mw_ui.add_pm_window.close()
		
		database_controller.add(mw_ui , 'PackingMaterial' , 
										(
													mw_ui.add_pm_ui.material_name.text(), 
		                                            mw_ui.add_pm_ui.material_code.text(), 
		                                            mw_ui.add_pm_ui.rm_quantity.value(),
		                                            mw_ui.add_pm_ui.rm_units_combo.currentText(),
													mw_ui.add_pm_ui.loq_warning.isChecked(),
													mw_ui.add_pm_ui.loq_quantity.value(),
										))
		views.fill_out_list(mw_ui.counts_labels,mw_ui.main_data_base, mw_ui.pm_list 				, 'PackingMaterial' , (1,2,3,4)  	,'{0}	({1})	({2} {3})'	, 0 )
		




	mw_ui.add_pm_ui.add_pm.clicked.connect(call_add_pm)

	con=sq.connect(mw_ui.main_data_base)
	mw_ui.add_pm_ui.rm_units_combo.clear()

	for unit in database_controller.packing_materials_units:
		mw_ui.add_pm_ui.rm_units_combo.addItem(unit)


	mw_ui.add_pm_window.show()


def open_add_output_pm_window(mw_ui):

	try:
		mw_ui.pm_list.currentItem().data(4)
		mw_ui.add_pm_output_window = QtWidgets.QDialog()
		mw_ui.add_pm_output_window.setWindowModality(QtCore.Qt.ApplicationModal)
		mw_ui.open_add_pm_output_ui = uic.loadUi('windows/add_pm_output.ui', mw_ui.add_pm_output_window )
		mw_ui.open_add_pm_output_ui.setStyleSheet(mw_ui.current_style)
		mw_ui.open_add_pm_output_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		config = configparser.ConfigParser()
		config.read('settings.ini')
		icon_folder=config['icons themes folders'][config['settings']['style']]
		mw_ui.add_icon	= QtGui.QIcon()
		mw_ui.add_icon.addPixmap(QtGui.QPixmap(f"{icon_folder}/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		mw_ui.open_add_pm_output_ui.add.setIcon(mw_ui.add_icon)


		
		def add_output():
			mw_ui.open_add_pm_output_ui.close()
			material = database_controller.get_data(mw_ui.main_data_base,'PackingMaterial', columns='quantity', condition=f'where id = {mw_ui.pm_list.currentItem().data(4)}')[0]
			if material[0] >= mw_ui.open_add_pm_output_ui.quantity.value():
				new_quantity = material[0] - mw_ui.open_add_pm_output_ui.quantity.value()

				
				database_controller.add(mw_ui , 'PackingMaterialOutput' , 
											(
														mw_ui.pm_list.currentItem().data(4), 
														mw_ui.open_add_pm_output_ui.quantity.value(), 
														mw_ui.open_add_pm_output_ui.date.date().toPyDate().isoformat(),
														mw_ui.open_add_pm_output_ui.note.toPlainText(),
														
											))
				database_controller.edit_specific_field(mw_ui,'PackingMaterial',f'quantity = {new_quantity} ',mw_ui.pm_list.currentItem().data(4))
				views.fill_out_list(mw_ui.counts_labels, mw_ui.main_data_base, mw_ui.pm_list 				, 'PackingMaterial' , (1,2,3,4)  	,'{0}	({1})	({2} {3})'	, 0 )
			else:
				notification(mw_ui,'NO ENOUGH QUANTITY', f'There is no enough qunatity to make this output')

		mw_ui.open_add_pm_output_ui.add.clicked.connect(add_output)
		mw_ui.open_add_pm_output_ui.show()
	except:
		notification(mw_ui,'NO ITEM SELECTED', f'Plaese select item to output')

def open_add_input_pm_window(mw_ui):

	try:
		mw_ui.pm_list.currentItem().data(4)
		mw_ui.add_pm_input_window = QtWidgets.QDialog()
		mw_ui.add_pm_input_window.setWindowModality(QtCore.Qt.ApplicationModal)
		mw_ui.open_add_pm_input_ui = uic.loadUi('windows/add_pm_input.ui', mw_ui.add_pm_input_window )
		mw_ui.open_add_pm_input_ui.setStyleSheet(mw_ui.current_style)
		mw_ui.open_add_pm_input_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		config = configparser.ConfigParser()
		config.read('settings.ini')
		icon_folder=config['icons themes folders'][config['settings']['style']]
		mw_ui.add_icon	= QtGui.QIcon()
		mw_ui.add_icon.addPixmap(QtGui.QPixmap(f"{icon_folder}/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		mw_ui.open_add_pm_input_ui.add.setIcon(mw_ui.add_icon)

		
		def add_output():
			mw_ui.open_add_pm_input_ui.close()
			material = database_controller.get_data(mw_ui.main_data_base,'PackingMaterial', columns='quantity', condition=f'where id = {mw_ui.pm_list.currentItem().data(4)}')[0]
			
			new_quantity = material[0]+ mw_ui.open_add_pm_input_ui.quantity.value()
			
			
			database_controller.add(mw_ui , 'PackingMaterialInput' , 
											(
														mw_ui.pm_list.currentItem().data(4), 
														mw_ui.open_add_pm_input_ui.quantity.value(), 
														mw_ui.open_add_pm_input_ui.date.date().toPyDate().isoformat(),
														mw_ui.open_add_pm_input_ui.note.toPlainText(),
														
											))
			database_controller.edit_specific_field(mw_ui,'PackingMaterial',f'quantity = {new_quantity} ',mw_ui.pm_list.currentItem().data(4))
			views.fill_out_list(mw_ui.counts_labels, mw_ui.main_data_base, mw_ui.pm_list 				, 'PackingMaterial' , (1,2,3,4)  	,'{0}	({1})	({2} {3})'	, 0 )

		mw_ui.open_add_pm_input_ui.add.clicked.connect(add_output)
		mw_ui.open_add_pm_input_ui.show()
	except:
		notification(mw_ui,'NO ITEM SELECTED', f'Plaese select item to input')
















def open_add_unpacked_product_window(mw_ui):

	mw_ui.add_up_window =QtWidgets.QDialog()
	mw_ui.add_up_window.setWindowModality(QtCore.Qt.ApplicationModal)
	mw_ui.add_up_ui = uic.loadUi('windows/AddUnpackedProduct.ui', mw_ui.add_up_window)
	mw_ui.add_up_ui.setStyleSheet(mw_ui.current_style)
	mw_ui.add_up_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
	mw_ui.add_up_ui.add.setIcon(mw_ui.add_icon)
	mw_ui.add_up_ui.add_raw_material.setIcon(mw_ui.add_icon)
	mw_ui.add_up_ui.remove_row.setIcon(mw_ui.delete_icon)
	mw_ui.add_up_ui.composed_percent=0
	mw_ui.add_up_ui.saved=False

	for m_type in database_controller.material_types.keys():
		mw_ui.add_up_ui.material_type.addItem(m_type)

	config = configparser.ConfigParser()
	config.read('settings.ini')

	translation.retranslate_add_unpacked_product_window(mw_ui.add_up_ui , dictionary.languages[config['settings']['current_language']])
	if config['settings']['current_language']=='ar':
		mw_ui.add_up_ui.setLayoutDirection(QtCore.Qt.RightToLeft)
	else:
		mw_ui.add_up_ui.setLayoutDirection(QtCore.Qt.LeftToRight)


	def view_rm_units():
		mw_ui.add_up_ui.unit.clear()
		for unit in database_controller.material_types[mw_ui.add_up_ui.material_type.currentText().lower()]:
			mw_ui.add_up_ui.unit.addItem(unit)

	view_rm_units()
	mw_ui.add_up_ui.material_type.currentIndexChanged.connect(view_rm_units)

	def change_progress_bar_value(pb,value, direction):
	
		pb.setValue(pb.value()+(value*direction))
			
		if pb.value()>50:
			pb.setStyleSheet('color:rgb(0,0,0);border:0px;')
		if pb.value()<50:
			pb.setStyleSheet('color:rgb(200,200,200);border:0px;')
			pb.update()
		pb.setFormat(str(mw_ui.add_up_ui.composed_percent)+'% Composed')
		

	def add_rm():
			mw_ui.add_up_ui.add_uprm_ui.close()

			material_name 	= mw_ui.add_up_ui.add_uprm_ui.material.currentText()
			material_id		= mw_ui.add_up_ui.add_uprm_ui.material.currentData()
			percent			= mw_ui.add_up_ui.add_uprm_ui.percent.value()
			mw_ui.add_up_ui.composed_percent+=percent

			mw_ui.add_up_ui.tableWidget.setRowCount(mw_ui.add_up_ui.tableWidget.rowCount()+1)
			
			item = QtWidgets.QTableWidgetItem()
			item.setText(material_name)
			item.setData(4,material_id)
			mw_ui.add_up_ui.tableWidget.setItem(mw_ui.add_up_ui.tableWidget.rowCount()-1,0,item)

			item = QtWidgets.QTableWidgetItem()
			item.setText(str(percent)+'%')
			item.setData(4,percent)
			mw_ui.add_up_ui.tableWidget.setItem(mw_ui.add_up_ui.tableWidget.rowCount()-1,1,item)


			change_progress_bar_value(mw_ui.add_up_ui.progressBar,percent,1)
			
			
	def open_add_raw_material_window():
		if mw_ui.add_up_ui.composed_percent<100:
			mw_ui.add_up_ui.add_uprm_window =QtWidgets.QDialog()
			mw_ui.add_up_ui.add_uprm_window.setWindowModality(QtCore.Qt.ApplicationModal)
			mw_ui.add_up_ui.add_uprm_ui = uic.loadUi('windows/AddUnpackedProductRawMaterial.ui', mw_ui.add_up_ui.add_uprm_window)
			mw_ui.add_up_ui.add_uprm_ui.setStyleSheet(mw_ui.current_style)
			mw_ui.add_up_ui.add_uprm_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
			mw_ui.add_up_ui.add_uprm_ui.percent.setMaximum(100-mw_ui.add_up_ui.composed_percent)
			mw_ui.add_up_ui.add_uprm_ui.add.setIcon(mw_ui.add_icon)

			config = configparser.ConfigParser()
			config.read('settings.ini')

			translation.retranslate_add_unpp_raw_material_window(mw_ui.add_up_ui.add_uprm_ui , dictionary.languages[config['settings']['current_language']])
			if config['settings']['current_language']=='ar':
				mw_ui.add_up_ui.add_uprm_ui.setLayoutDirection(QtCore.Qt.RightToLeft)
			else:
				mw_ui.add_up_ui.add_uprm_ui.setLayoutDirection(QtCore.Qt.LeftToRight)

			materials = database_controller.get_data(mw_ui.main_data_base , 'RawMaterials', columns='name,id')
			
			for material in materials:
				mw_ui.add_up_ui.add_uprm_ui.material.addItem(material[0],material[1])
				



			mw_ui.add_up_ui.add_uprm_ui.show()
			
			mw_ui.add_up_ui.add_uprm_ui.add.clicked.connect(lambda: add_rm() )
			
		else:
			QtWidgets.QMessageBox.warning(mw_ui.add_up_ui,'composing not completed',"you have composed 100% of this product you can't add more materials ",QtWidgets.QMessageBox.Ok)

	def delete_row():
		try:
			percent=(mw_ui.add_up_ui.tableWidget.item(mw_ui.add_up_ui.tableWidget.currentRow(),1).text())
			percent=float(percent[:len(percent)-1])
			mw_ui.add_up_ui.composed_percent-=percent
			change_progress_bar_value(mw_ui.add_up_ui.progressBar,percent,-1)
			

			mw_ui.add_up_ui.tableWidget.removeRow(mw_ui.add_up_ui.tableWidget.currentRow())
		except:
			pass
	

	def add_unpacked_product():
			mw_ui.add_up_window.close()
			product_id = database_controller.add(mw_ui , 'UnpackedProduct' , 
											(
														mw_ui.add_up_ui.product_name.text(), 
														mw_ui.add_up_ui.product_code.text(), 
														mw_ui.add_up_ui.material_type.currentText(), 
														mw_ui.add_up_ui.quantity.value(), 
														mw_ui.add_up_ui.unit.currentText(), 
											)).lastrowid
			views.fill_out_list(mw_ui.counts_labels,mw_ui.main_data_base, mw_ui.unpacked_product_list , 'UnpackedProduct' , (1,2,4,5)  	,'{0}	({1})	({2} {3})'	, 0 )

			for i in range(mw_ui.add_up_ui.tableWidget.rowCount()):
				percent	= mw_ui.add_up_ui.tableWidget.item(i,1).data(4)
				rm_id	= mw_ui.add_up_ui.tableWidget.item(i,0).data(4)
				database_controller.add(mw_ui , 'UnpackedProductRawMaterial' , 
											(
														product_id,
														rm_id,
														percent
											))
			mw_ui.add_up_ui.saved=True
			

	mw_ui.add_up_ui.add.clicked.connect(add_unpacked_product)
	mw_ui.add_up_ui.add_raw_material.clicked.connect(open_add_raw_material_window)
	mw_ui.add_up_ui.remove_row.clicked.connect(delete_row)



	mw_ui.add_up_ui.closeEvent = MethodType(confirmCloseEvent,mw_ui.add_up_ui)

	mw_ui.add_up_window.show()

def open_add_packed_product_window(mw_ui):

	mw_ui.add_pp_window =QtWidgets.QDialog()
	mw_ui.add_pp_window.setWindowModality(QtCore.Qt.ApplicationModal)
	mw_ui.add_pp_ui = uic.loadUi('windows/AddPackedProduct.ui', mw_ui.add_pp_window)
	mw_ui.add_pp_ui.setStyleSheet(mw_ui.current_style)
	mw_ui.add_pp_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
	mw_ui.add_pp_ui.add_packing_material.setIcon(mw_ui.add_icon)
	mw_ui.add_pp_ui.remove_row.setIcon(mw_ui.delete_icon)
	mw_ui.add_pp_ui.add.setIcon(mw_ui.add_icon)

	config = configparser.ConfigParser()
	config.read('settings.ini')

	translation.retranslate_add_packed_product_window(mw_ui.add_pp_ui , dictionary.languages[config['settings']['current_language']])
	if config['settings']['current_language']=='ar':
		mw_ui.add_pp_ui.setLayoutDirection(QtCore.Qt.RightToLeft)
	else:
		mw_ui.add_pp_ui.setLayoutDirection(QtCore.Qt.LeftToRight)

	products = database_controller.get_data(mw_ui.main_data_base , 'UnpackedProduct', columns='name,id')
	for product in products:
		mw_ui.add_pp_ui.product.addItem(product[0],product[1])

	def view_p_units():
		mw_ui.add_pp_ui.unit.clear()
		try:
			material_type = database_controller.get_data(mw_ui.main_data_base , 'UnpackedProduct', columns='material_type', condition=f'where id = {mw_ui.add_pp_ui.product.currentData()}')[0][0]
			for unit in database_controller.material_types[material_type.lower()]:
				mw_ui.add_pp_ui.unit.addItem(unit)
		except:
			pass



	def add_pm():
			material_name 	= mw_ui.add_pp_ui.add_uppm_ui.material.currentText()
			material_id		= mw_ui.add_pp_ui.add_uppm_ui.material.currentData()
			count			= mw_ui.add_pp_ui.add_uppm_ui.count.value()

			mw_ui.add_pp_ui.tableWidget.setRowCount(mw_ui.add_pp_ui.tableWidget.rowCount()+1)
			
			item = QtWidgets.QTableWidgetItem()
			item.setText(material_name)
			item.setData(4,material_id)
			mw_ui.add_pp_ui.tableWidget.setItem(mw_ui.add_pp_ui.tableWidget.rowCount()-1,0,item)

			item = QtWidgets.QTableWidgetItem()
			item.setText(str(count))
			item.setData(4,count)
			mw_ui.add_pp_ui.tableWidget.setItem(mw_ui.add_pp_ui.tableWidget.rowCount()-1,1,item)

			mw_ui.add_pp_ui.add_uppm_ui.close()

	def open_add_packing_material_window():
			mw_ui.add_pp_ui.add_uppm_window =QtWidgets.QDialog()
			mw_ui.add_pp_ui.add_uppm_window.setWindowModality(QtCore.Qt.ApplicationModal)
			mw_ui.add_pp_ui.add_uppm_ui = uic.loadUi('windows/AddPackedProductPackingMaterial.ui', mw_ui.add_pp_ui.add_uppm_window)
			mw_ui.add_pp_ui.add_uppm_ui.setStyleSheet(mw_ui.current_style)
			mw_ui.add_pp_ui.add_uppm_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
			mw_ui.add_pp_ui.add_uppm_ui.add.setIcon(mw_ui.add_icon)

			config = configparser.ConfigParser()
			config.read('settings.ini')

			translation.retranslate_add_pp_packing_material_window(mw_ui.add_pp_ui.add_uppm_ui , dictionary.languages[config['settings']['current_language']])
			if config['settings']['current_language']=='ar':
				mw_ui.add_pp_ui.add_uppm_ui.setLayoutDirection(QtCore.Qt.RightToLeft)
			else:
				mw_ui.add_pp_ui.add_uppm_ui.setLayoutDirection(QtCore.Qt.LeftToRight)

			materials = database_controller.get_data(mw_ui.main_data_base , 'PackingMaterial', columns='name,id')
			
			for material in materials:
				mw_ui.add_pp_ui.add_uppm_ui.material.addItem(material[0],material[1])

			mw_ui.add_pp_ui.add_uppm_ui.show()
			
			mw_ui.add_pp_ui.add_uppm_ui.add.clicked.connect(add_pm)

	def delete_pm_row():
		try:
			mw_ui.add_pp_ui.tableWidget.removeRow(mw_ui.add_pp_ui.tableWidget.currentRow())
		except:
			pass
	

	def add_packed_product():
			mw_ui.add_pp_ui.close()
			material_id = database_controller.add(mw_ui , 'PackedProduct' , 
											(
														mw_ui.add_pp_ui.packing_name.text(), 
														mw_ui.add_pp_ui.packing_code.text(), 
														mw_ui.add_pp_ui.product.currentData(), 
														mw_ui.add_pp_ui.quantity.value(), 
														mw_ui.add_pp_ui.unit.currentText(), 
											)).lastrowid
			views.fill_out_list(mw_ui.counts_labels,mw_ui.main_data_base, mw_ui.packed_product_list 	, 'PackedProduct' 	, (1,2)  		,'{0}	({1})'				, 0 )
					
	


			for i in range(mw_ui.add_pp_ui.tableWidget.rowCount()):
				count	= float(mw_ui.add_pp_ui.tableWidget.item(i,1).text())
				pm_id	= mw_ui.add_pp_ui.tableWidget.item(i,0).data(4)
				database_controller.add(mw_ui , 'PackedProductPackingMaterial' , 
											(
														material_id,
														pm_id,
														count
											))

			


	view_p_units()
	mw_ui.add_pp_ui.product.currentIndexChanged.connect(view_p_units) 
	mw_ui.add_pp_ui.add_packing_material.clicked.connect(open_add_packing_material_window)
	mw_ui.add_pp_ui.remove_row.clicked.connect(delete_pm_row)
	mw_ui.add_pp_ui.add.clicked.connect(add_packed_product)


	mw_ui.add_pp_window.show()


def open_add_order_window(mw_ui):

	mw_ui.add_o_window =QtWidgets.QDialog()
	mw_ui.add_o_window.setWindowModality(QtCore.Qt.ApplicationModal)
	mw_ui.add_o_ui = uic.loadUi('windows/AddOrder.ui', mw_ui.add_o_window)
	mw_ui.add_o_ui.setStyleSheet(mw_ui.current_style)
	mw_ui.add_o_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
	mw_ui.add_o_ui.add.setIcon(mw_ui.add_icon)#

	config = configparser.ConfigParser()
	config.read('settings.ini')

	translation.retranslate_add_order_window(mw_ui.add_o_ui , dictionary.languages[config['settings']['current_language']])
	if config['settings']['current_language']=='ar':
		mw_ui.add_o_ui.setLayoutDirection(QtCore.Qt.RightToLeft)
	else:
		mw_ui.add_o_ui.setLayoutDirection(QtCore.Qt.LeftToRight)

	products = database_controller.get_data(mw_ui.main_data_base , 'PackedProduct', columns='name,id')
	for product in products:
		mw_ui.add_o_ui.packed_product.addItem(product[0],product[1])

	def check_quantities():
		quantity			= mw_ui.add_o_ui.quantity.value()
		packed_product_id 	= mw_ui.add_o_ui.packed_product.currentData()
		enought_quantities	= True
		used_materials		= []#(id, name, quantity, type, unit, quantity, having enought quantity?)
		#check packing materials
		packing_materials_connection		= database_controller.get_data(mw_ui.main_data_base , 'PackedProductPackingMaterial', columns='packing_material,count', condition=f'where packed_product = {packed_product_id}')
		for c_material in packing_materials_connection:
			material = database_controller.get_data(mw_ui.main_data_base , 'PackingMaterial', columns='name, code, quantity, unit', condition=f'where id = {c_material[0]}')[0]
			used_materials.append((c_material[0], material[0], material[2], None, material[3] , quantity*c_material[1] , quantity*c_material[1]<=material[2] ))
			if not  quantity*c_material[1]<=material[2]:
				enought_quantities	= False

		#check raw materials
		unpacked_product			= database_controller.get_data(mw_ui.main_data_base , 'PackedProduct', columns='unpacked_product, unpacked_product_quantity_in_one, unit', condition=f'where id = {packed_product_id}')[0]
		
		unpacked_product_connection = database_controller.get_data(mw_ui.main_data_base , 'UnpackedProductRawMaterial', columns=' material, percent', condition=f'where product= {unpacked_product[0]}')
		
		for c_material in unpacked_product_connection:
			material = database_controller.get_data(mw_ui.main_data_base , 'RawMaterials', columns='name, m_type, code, quantity, unit', condition=f'where id = {c_material[0]}')[0]
			m_quantity = quantity * unpacked_product[1] *  database_controller.material_units_convert[unpacked_product[2]] * (c_material[1]/100)
			a_quantity = material[3] * database_controller.material_units_convert[material[4]]

			if material[1].upper()=='SOLID':
				unit='G'

			else:
				unit='L'

			used_materials.append((c_material[0], material[0], material[3]*database_controller.material_units_convert[material[4]]  , material[1], unit ,m_quantity ,  m_quantity <= a_quantity ))
			if not  m_quantity <= a_quantity:
				enought_quantities	= False


		msg=''
		for i in used_materials:
			if i[3] !=None:

				m_quantity=database_controller.convert_to_best_unit(i[2], i[4] ,i[3])
				a_quantity=database_controller.convert_to_best_unit(i[5], i[4] ,i[3])
			else:
				m_quantity=(i[2], i[4])
				a_quantity=(i[5], i[4])

			if not i[6]:
				alert='<span style=" color:#ef2929;"><b>Not Available</b></span>'
			else:
				alert='<span style=" color:#8ae234;"><b>Available</b></span>'

			msg+=f''' <br> <br><b>({i[1]})</b> <br>{a_quantity[0]} {a_quantity[1]} from {m_quantity[0]} {m_quantity[1]}		{alert}  '''

		
		if enought_quantities:
			a=QtWidgets.QMessageBox.question(mw_ui , 'Add confirm' ,'This order will use the following quantities '+msg+'<br><br> <b>Do you still want to add this Order?</b>')
			return (used_materials,a==QtWidgets.QMessageBox.Yes)
		else:
			a=QtWidgets.QMessageBox.warning(mw_ui , 'Add confirm' ,"This order can't be created because you don't have the required quantities"+msg)
			return (used_materials,False)

	def add_order():
		used_materials = check_quantities()
		if used_materials[1]:
			mw_ui.add_o_ui.close()
			database_controller.add(mw_ui , '"Order"' , 
											(
														mw_ui.add_o_ui.name.text() ,
														mw_ui.add_o_ui.code.text() ,
														mw_ui.add_o_ui.packed_product.currentData() ,
														mw_ui.add_o_ui.quantity.value() ,
														mw_ui.add_o_ui.starting_date.date().toPyDate().isoformat() ,
														mw_ui.add_o_ui.planned_finishing_date.date().toPyDate().isoformat() ,
														mw_ui.add_o_ui.actual_finishing_date.date().toPyDate().isoformat() ,
														mw_ui.add_o_ui.done.isChecked()
											))
			
			views.fill_out_orders_list(mw_ui)
			views.view_all_orders(mw_ui)
			#(id, name, quantity, type, unit, quantity, having enought quantity?)
			for material in used_materials[0]:
				if material[3] == None: # then it is packing material
					data='quantity = '+str(material[2]-material[5])
					database_controller.edit_specific_field(mw_ui,'PackingMaterial',data,material[0])
					
				else:
					updated_data		= database_controller.convert_to_best_unit(material[2]-material[5] ,material[4], material[3])
					data=f'quantity = {updated_data[0]} , unit = "{updated_data[1]}"'
					database_controller.edit_specific_field(mw_ui,'RawMaterials',data,material[0])
					
			views.fill_out_list(mw_ui.counts_labels,mw_ui.main_data_base, mw_ui.pm_list, 'PackingMaterial' , (1,2,3,4)  	,'{0}	({1})	({2} {3})'	, 0 )
			views.fill_out_list(mw_ui.counts_labels,mw_ui.main_data_base, mw_ui.rm_list, 'RawMaterials' 	, (1,3,4,5)  	,'{0}	({1})	({2} {3})'	, 0 )


	mw_ui.add_o_ui.add.clicked.connect(add_order)
	mw_ui.add_o_ui.show()

#####################################################
############ DELETE DATA windows ####################
#####################################################
#>	


def delete_item(mw_ui, table, current_item):
	#try:
		_id = current_item.data(4)
		config = configparser.ConfigParser()
		config.read('settings.ini')
		a=QtWidgets.QMessageBox.question(mw_ui , 'Delete confirm' ,dictionary.languages[config['settings']['current_language']]['Do you really want to delete this item?'])
		if a==QtWidgets.QMessageBox.Yes:
			database_controller.delete(mw_ui, mw_ui.main_data_base, table, _id)
					

	
	#except:
		notification(mw_ui,'NO ITEM SELECTED', f'Plaese select item to delete it')
	


def delete_order(mw_ui,_id):
	config = configparser.ConfigParser()
	config.read('settings.ini')

	a=QtWidgets.QMessageBox.question(mw_ui , 'Delete confirm' ,dictionary.languages[config['settings']['current_language']]['Do you really want to delete this item?'])
	if a==QtWidgets.QMessageBox.Yes:
		_id=_id.data(4)
		a=QtWidgets.QMessageBox.question(mw_ui , 'Delete detail' ,dictionary.languages[config['settings']['current_language']]['Do you want to restore the materials quantity that been used in this order?'])
		if a==QtWidgets.QMessageBox.Yes:

			
			data			 	= database_controller.get_data(mw_ui.main_data_base , '"Order"', columns='packed_product, quantity', condition=f'where id = {mw_ui.orders_list.currentItem().data(4)}')[0]
			packed_product_id	= data[0]
			order_quantity		= data[1]

			
			packing_materials		= database_controller.get_data(mw_ui.main_data_base , 'PackedProductPackingMaterial', columns='packing_material,count', condition=f'where packed_product = {packed_product_id}')
			for material in packing_materials:
				material_quantity = database_controller.get_data(mw_ui.main_data_base , 'PackingMaterial', columns='quantity', condition=f'where id = {material[0]}')[0][0]
				updated_data=f'quantity = '+str(material_quantity+(order_quantity*material[1]))

				database_controller.edit_specific_field(mw_ui,'PackingMaterial',updated_data,material[0])
			
			views.fill_out_list(mw_ui.counts_labels,mw_ui.main_data_base, mw_ui.pm_list, 'PackingMaterial' , (1,2,3,4)  	,'{0}	({1})	({2} {3})'	, 0 )
			
			
			#(id, name, quantity, type, unit, quantity, having enought quantity?) PackedProduct
			unpacked_product_id 		= database_controller.get_data(mw_ui.main_data_base , 'PackedProduct', columns='unpacked_product', condition=f'where id = {packed_product_id}')[0][0]
			unpacked_product_quintity_in_pp 	= database_controller.get_data(mw_ui.main_data_base , 'PackedProduct', columns='unpacked_product_quantity_in_one, unit', condition=f'where id = {packed_product_id}')[0]
			unpacked_product_quantity	= unpacked_product_quintity_in_pp[0]*database_controller.material_units_convert[unpacked_product_quintity_in_pp[1]]
			raw_materials				= database_controller.get_data(mw_ui.main_data_base , 'UnpackedProductRawMaterial', columns=' material, percent', condition=f'where product = {unpacked_product_id}')
			for material in raw_materials:
				material_quantity = database_controller.get_data(mw_ui.main_data_base , 'RawMaterials', columns='quantity,unit,m_type', condition=f'where id = {material[0]}')[0]
				old_quantity	= material_quantity[0]*database_controller.material_units_convert[material_quantity[1]]
				added_quantity	= order_quantity * unpacked_product_quantity *(material[1]/100)
				if material_quantity[2].upper()== 'SOLID':
					unit='G'
				else:
					unit='L'


				updated_data		= database_controller.convert_to_best_unit(old_quantity+added_quantity ,unit ,material_quantity[2])
				data=f'quantity = {updated_data[0]} , unit = "{updated_data[1]}"'

				database_controller.edit_specific_field(mw_ui,'RawMaterials',data,material[0])
			views.fill_out_orders_list(mw_ui)
			views.view_all_orders(mw_ui)
		database_controller.delete(mw_ui, mw_ui.main_data_base, '"Order"', _id)
			

		
	


###################################################
############ EDIT DATA windows ####################
###################################################
#>



def open_edit_rm_window(mw_ui):
	try:
		data=database_controller.get_data(mw_ui.main_data_base , 'RawMaterials', columns='name, m_type, code, quantity, unit, density, loq_warning,loq_quantity, loq_unit'  , condition=f'where id = {mw_ui.rm_list.currentItem().data(4)}')[0]

		mw_ui.edit_rm_window =QtWidgets.QDialog()
		mw_ui.edit_rm_window.setWindowModality(QtCore.Qt.ApplicationModal)
		mw_ui.edit_rm_ui = uic.loadUi('windows/EditRawMaterial.ui', mw_ui.edit_rm_window)
		mw_ui.edit_rm_ui.setStyleSheet(mw_ui.current_style)
		mw_ui.edit_rm_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)

		config = configparser.ConfigParser()
		config.read('settings.ini')

		translation.retranslate_edit_rm_window(mw_ui.edit_rm_ui , dictionary.languages[config['settings']['current_language']])
		if config['settings']['current_language']=='ar':
			mw_ui.edit_rm_ui.setLayoutDirection(QtCore.Qt.RightToLeft)
		else:
			mw_ui.edit_rm_ui.setLayoutDirection(QtCore.Qt.LeftToRight)

		#view data
		mw_ui.edit_rm_ui.material_name.setText(data[0])
		mw_ui.edit_rm_ui.material_type.setText(data[1])
		mw_ui.edit_rm_ui.material_code.setText(data[2])
		mw_ui.edit_rm_ui.rm_quantity.setValue(data[3])
		mw_ui.edit_rm_ui.rm_density.setValue(data[5])
		mw_ui.edit_rm_ui.loq_warning.setChecked(data[6])
		mw_ui.edit_rm_ui.loq_quantity.setValue(data[7])




		mw_ui.edit_rm_ui.loq_units.addItem(data[8])
		mw_ui.edit_rm_ui.rm_units_combo.addItem(data[4])
		for unit in database_controller.material_types[mw_ui.edit_rm_ui.material_type.text().lower()]:
			mw_ui.edit_rm_ui.rm_units_combo.addItem(unit)
			mw_ui.edit_rm_ui.loq_units.addItem(unit)

		views.fill_out_list(None, mw_ui.main_data_base, mw_ui.edit_rm_ui.outputs , 'RawMaterialsOutput' 	, (2,3,4,5)  	,'{0} {1}	({2})'	, 0 ,tooltip_form='{3}' ,condition=f'where material={mw_ui.rm_list.currentItem().data(4)}')
		views.fill_out_list(None, mw_ui.main_data_base, mw_ui.edit_rm_ui.inputs	 , 'RawMaterialsInput'	 	, (2,3,4,5)  	,'{0} {1}	({2})'	, 0 ,tooltip_form='{3}' ,condition=f'where material={mw_ui.rm_list.currentItem().data(4)}')


		def edit_rm():
			mw_ui.edit_rm_ui.close()
			database_controller.edit(mw_ui,'RawMaterials',(
						mw_ui.edit_rm_ui.material_name.text(),
						mw_ui.edit_rm_ui.material_type.text(),
						mw_ui.edit_rm_ui.material_code.text(),
						mw_ui.edit_rm_ui.rm_quantity.value(),
						mw_ui.edit_rm_ui.rm_units_combo.currentText(),
						mw_ui.edit_rm_ui.rm_density.value(),
						
						mw_ui.edit_rm_ui.loq_warning.isChecked(),
						mw_ui.edit_rm_ui.loq_quantity.value(),
						mw_ui.edit_rm_ui.loq_units.currentText())
						
						,mw_ui.rm_list.currentItem().data(4))
			
			views.fill_out_list(mw_ui.counts_labels,mw_ui.main_data_base, mw_ui.rm_list 				, 'RawMaterials' 	, (1,3,4,5)  	,'{0}	({1})	({2} {3})'	,0)

		mw_ui.edit_rm_ui.edit_rm.clicked.connect(edit_rm)
		mw_ui.edit_rm_ui.show()
	
	except:
		notification(mw_ui,'NO ITEM SELECTED', f'Plaese select item to edit it')

def open_edit_pm_window(mw_ui):
	try:
		data=database_controller.get_data(mw_ui.main_data_base , 'PackingMaterial', columns='name, code, quantity, unit,loq_warning,loq_quantity'  , condition=f'where id = {mw_ui.pm_list.currentItem().data(4)}')[0]

		mw_ui.edit_pm_window =QtWidgets.QDialog()
		mw_ui.edit_pm_window.setWindowModality(QtCore.Qt.ApplicationModal)
		mw_ui.edit_pm_ui = uic.loadUi('windows/EditPackingMaterial.ui', mw_ui.edit_pm_window)
		mw_ui.edit_pm_ui.setStyleSheet(mw_ui.current_style)
		mw_ui.edit_pm_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)

		config = configparser.ConfigParser()
		config.read('settings.ini')

		translation.retranslate_edit_pm_window(mw_ui.edit_pm_ui , dictionary.languages[config['settings']['current_language']])
		if config['settings']['current_language']=='ar':
			mw_ui.edit_pm_ui.setLayoutDirection(QtCore.Qt.RightToLeft)
		else:
			mw_ui.edit_pm_ui.setLayoutDirection(QtCore.Qt.LeftToRight)
		#view data
		mw_ui.edit_pm_ui.material_name.setText(data[0])
		mw_ui.edit_pm_ui.material_code.setText(data[1])
		mw_ui.edit_pm_ui.rm_quantity.setValue(data[2])
		mw_ui.edit_pm_ui.loq_warning.setChecked(data[4])
		mw_ui.edit_pm_ui.loq_quantity.setValue(data[5])
		
		
		
		mw_ui.edit_pm_ui.rm_units_combo.addItem(data[3])
		for unit in database_controller.packing_materials_units:
			mw_ui.edit_pm_ui.rm_units_combo.addItem(unit)


		views.fill_out_list(None, mw_ui.main_data_base, mw_ui.edit_pm_ui.outputs , 'PackingMaterialOutput' 		, (2,3,4)  	,'{0}	({1})'	, 0 ,tooltip_form='{2}' ,condition=f'where material={mw_ui.pm_list.currentItem().data(4)}')
		views.fill_out_list(None, mw_ui.main_data_base, mw_ui.edit_pm_ui.inputs	 , 'PackingMaterialInput'	 	, (2,3,4)  	,'{0}	({1})'	, 0 ,tooltip_form='{2}' ,condition=f'where material={mw_ui.pm_list.currentItem().data(4)}')

		def edit_pm():
			mw_ui.edit_pm_ui.close()
			database_controller.edit(mw_ui,'PackingMaterial',(
						mw_ui.edit_pm_ui.material_name.text(),
						mw_ui.edit_pm_ui.material_code.text(),
						mw_ui.edit_pm_ui.rm_quantity.value(),
						mw_ui.edit_pm_ui.rm_units_combo.currentText(),
						mw_ui.edit_pm_ui.loq_warning.isChecked(),
						mw_ui.edit_pm_ui.loq_quantity.value(),
						)
						
						,mw_ui.pm_list.currentItem().data(4))
			
			views.fill_out_list(mw_ui.counts_labels,mw_ui.main_data_base, mw_ui.pm_list 				, 'PackingMaterial' , (1,2,3,4)  	,'{0}	({1})	({2} {3})'	, 0 )

		mw_ui.edit_pm_ui.edit_pm.clicked.connect(edit_pm)
		mw_ui.edit_pm_ui.show()

	except:
		notification(mw_ui,'NO ITEM SELECTED', f'Plaese select item to edit it')

def open_edit_up_window(mw_ui):
	try:
		data=database_controller.get_data(mw_ui.main_data_base , 'UnpackedProduct', columns='name, code, material_type, quantity, unit'  , condition=f'where id = {mw_ui.unpacked_product_list.currentItem().data(4)}')[0]

		mw_ui.edit_up_window =QtWidgets.QDialog()
		mw_ui.edit_up_window.setWindowModality(QtCore.Qt.ApplicationModal)
		mw_ui.edit_up_ui = uic.loadUi('windows/EditUnpackedProduct.ui', mw_ui.edit_up_window)
		mw_ui.edit_up_ui.setStyleSheet(mw_ui.current_style)
		mw_ui.edit_up_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)

		mw_ui.edit_up_ui.edit.setIcon(mw_ui.edit_icon)
		mw_ui.edit_up_ui.add_raw_material.setIcon(mw_ui.add_icon)
		mw_ui.edit_up_ui.remove_row.setIcon(mw_ui.delete_icon)

		mw_ui.edit_up_ui.composed_percent=0
		mw_ui.edit_up_ui.saved=False
		mw_ui.edit_up_ui.deleted_rm	= []
		mw_ui.edit_up_ui.added_rm	= []

		config = configparser.ConfigParser()
		config.read('settings.ini')

		translation.retranslate_edit_up_window(mw_ui.edit_up_ui , dictionary.languages[config['settings']['current_language']])
		if config['settings']['current_language']=='ar':
			mw_ui.edit_up_ui.setLayoutDirection(QtCore.Qt.RightToLeft)
		else:
			mw_ui.edit_up_ui.setLayoutDirection(QtCore.Qt.LeftToRight)

		#view data
		mw_ui.edit_up_ui.product_name.setText(data[0])
		mw_ui.edit_up_ui.product_code.setText(data[1])
		mw_ui.edit_up_ui.material_type.setText(data[2])
		mw_ui.edit_up_ui.quantity.setValue(data[3])
		
		
		
		mw_ui.edit_up_ui.unit.addItem(data[4])
		for unit in database_controller.material_types[mw_ui.edit_up_ui.material_type.text().lower()]:
			mw_ui.edit_up_ui.unit.addItem(unit)



		def change_progress_bar_value(pb,value, direction):
		
			pb.setValue(pb.value()+(value*direction))
				
			if pb.value()>50:
				pb.setStyleSheet('color:rgb(0,0,0);border:0px;')
			if pb.value()<50:
				pb.setStyleSheet('color:rgb(200,200,200);border:0px;')
				pb.update()
			pb.setFormat(str(mw_ui.edit_up_ui.composed_percent)+'% Composed')
				

		def add_rm(material_name, material_id, percent):

				mw_ui.edit_up_ui.composed_percent+=percent

				mw_ui.edit_up_ui.tableWidget.setRowCount(mw_ui.edit_up_ui.tableWidget.rowCount()+1)
				
				item = QtWidgets.QTableWidgetItem()
				item.setText(material_name)
				item.setData(4,material_id)
				mw_ui.edit_up_ui.tableWidget.setItem(mw_ui.edit_up_ui.tableWidget.rowCount()-1,0,item)

				item = QtWidgets.QTableWidgetItem()
				item.setText(str(percent)+'%')
				item.setData(4,percent)
				mw_ui.edit_up_ui.tableWidget.setItem(mw_ui.edit_up_ui.tableWidget.rowCount()-1,1,item)


				change_progress_bar_value(mw_ui.edit_up_ui.progressBar,percent,1)
				
				try:
					mw_ui.edit_up_ui.add_uprm_ui.close()
					mw_ui.edit_up_ui.added_rm.append((mw_ui.unpacked_product_list.currentItem().data(4),material_id[0],percent))
				except:
					pass

		def open_add_raw_material_window():
			if mw_ui.edit_up_ui.composed_percent<100:
				mw_ui.edit_up_ui.add_uprm_window =QtWidgets.QDialog()
				mw_ui.edit_up_ui.add_uprm_window.setWindowModality(QtCore.Qt.ApplicationModal)
				mw_ui.edit_up_ui.add_uprm_ui = uic.loadUi('windows/AddUnpackedProductRawMaterial.ui', mw_ui.edit_up_ui.add_uprm_window)
				mw_ui.edit_up_ui.add_uprm_ui.setStyleSheet(mw_ui.current_style)
				mw_ui.edit_up_ui.add_uprm_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
				mw_ui.edit_up_ui.add_uprm_ui.add.setIcon(mw_ui.add_icon)
				mw_ui.edit_up_ui.add_uprm_ui.percent.setMaximum(100-mw_ui.edit_up_ui.composed_percent)

				materials = database_controller.get_data(mw_ui.main_data_base , 'RawMaterials', columns='name,id')
				
				for material in materials:
					mw_ui.edit_up_ui.add_uprm_ui.material.addItem(material[0],material[1])
					



				mw_ui.edit_up_ui.add_uprm_ui.show()
				
				mw_ui.edit_up_ui.add_uprm_ui.add.clicked.connect(lambda: add_rm(mw_ui.edit_up_ui.add_uprm_ui.material.currentText(),(mw_ui.edit_up_ui.add_uprm_ui.material.currentData(),None),mw_ui.edit_up_ui.add_uprm_ui.percent.value()) )
				
			else:
				QtWidgets.QMessageBox.warning(mw_ui.edit_up_ui,'composing not completed',"you have composed 100% of this product you can't add more materials ",QtWidgets.QMessageBox.Ok)



		def edit_up():
			
			database_controller.edit(mw_ui,'UnpackedProduct',(
					mw_ui.edit_up_ui.product_name.text(),
					mw_ui.edit_up_ui.product_code.text(),
					mw_ui.edit_up_ui.material_type.text(),
					mw_ui.edit_up_ui.quantity.value(),
					mw_ui.edit_up_ui.unit.currentText())
						,mw_ui.unpacked_product_list.currentItem().data(4))
			
			views.fill_out_list(mw_ui.counts_labels,mw_ui.main_data_base, mw_ui.unpacked_product_list , 'UnpackedProduct' , (1,2,4,5)  	,'{0}	({1})	({2} {3})'	, 0 )
			for rm in mw_ui.edit_up_ui.deleted_rm:
				database_controller.delete(mw_ui,mw_ui.main_data_base, 'UnpackedProductRawMaterial', rm[1])
			for rm in mw_ui.edit_up_ui.added_rm:
				database_controller.add(mw_ui,'UnpackedProductRawMaterial',rm)
			mw_ui.edit_up_ui.saved=True
			mw_ui.edit_up_ui.close()
			

		def delete_row():
			try:
				percent=(mw_ui.edit_up_ui.tableWidget.item(mw_ui.edit_up_ui.tableWidget.currentRow(),1).text())
				maerial_id=(mw_ui.edit_up_ui.tableWidget.item(mw_ui.edit_up_ui.tableWidget.currentRow(),0).data(4))

				if maerial_id[1]==None:
					mw_ui.edit_up_ui.added_rm.remove((mw_ui.unpacked_product_list.currentItem().data(4), maerial_id[0], float(percent.replace('%',''))))
					
				else:
					mw_ui.edit_up_ui.deleted_rm.append(maerial_id)

				percent=float(percent[:len(percent)-1])
				mw_ui.edit_up_ui.composed_percent-=percent
				change_progress_bar_value(mw_ui.edit_up_ui.progressBar,percent,-1)
				

				mw_ui.edit_up_ui.tableWidget.removeRow(mw_ui.edit_up_ui.tableWidget.currentRow())
			except:
				pass

		rms=database_controller.get_data(mw_ui.main_data_base , 'UnpackedProductRawMaterial', columns='percent,material,id'  , condition=f'where product = {mw_ui.unpacked_product_list.currentItem().data(4)}')
		for i in rms:
			mw_ui.edit_up_ui.composed_percent+i[0]
			material_name=database_controller.get_data(mw_ui.main_data_base , 'RawMaterials', columns='name'  , condition=f'where id = {i[1]}')[0][0]
			add_rm(material_name, (i[1],i[2]), i[0])


		
		mw_ui.edit_up_ui.closeEvent = MethodType(confirmCloseEvent,mw_ui.edit_up_ui)
		mw_ui.edit_up_ui.add_raw_material.clicked.connect(open_add_raw_material_window)

		mw_ui.edit_up_ui.edit.clicked.connect(edit_up)
		mw_ui.edit_up_ui.remove_row.clicked.connect(delete_row)
		mw_ui.edit_up_ui.show()
	except:
		notification(mw_ui,'NO ITEM SELECTED', f'Plaese select item to edit it')

def open_edit_packed_product_window(mw_ui):
	try:
		mw_ui.edit_pp_window = QtWidgets.QDialog()
		mw_ui.edit_pp_window.setWindowModality(QtCore.Qt.ApplicationModal)
		mw_ui.edit_pp_ui = uic.loadUi('windows/EditPackedProduct.ui', mw_ui.edit_pp_window)
		mw_ui.edit_pp_ui.setStyleSheet(mw_ui.current_style)
		mw_ui.edit_pp_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		mw_ui.edit_pp_ui.edit.setIcon(mw_ui.add_icon)
		mw_ui.edit_pp_ui.remove_row.setIcon(mw_ui.delete_icon)
		
		mw_ui.edit_pp_ui.add_packing_material.setIcon(mw_ui.add_icon)

	

		mw_ui.edit_pp_ui.saved = False
		mw_ui.edit_pp_ui.deleted_rm	= []
		mw_ui.edit_pp_ui.added_rm	= []

		config = configparser.ConfigParser()
		config.read('settings.ini')

		translation.retranslate_edit_packed_product_window(mw_ui.edit_pp_ui , dictionary.languages[config['settings']['current_language']])
		if config['settings']['current_language']=='ar':
			mw_ui.edit_pp_ui.setLayoutDirection(QtCore.Qt.RightToLeft)
		else:
			mw_ui.edit_pp_ui.setLayoutDirection(QtCore.Qt.LeftToRight)

		data = database_controller.get_data(mw_ui.main_data_base , 'PackedProduct', columns='name, code, unpacked_product, unpacked_product_quantity_in_one, unit', condition=f'where id = {mw_ui.packed_product_list.currentItem().data(4)}')[0]
		
		products = database_controller.get_data(mw_ui.main_data_base , 'UnpackedProduct', columns='name,id')
		a_index=0
		for product in products:
			mw_ui.edit_pp_ui.product.addItem(product[0],product[1])
			if product[1] == data[2]:
				mw_ui.edit_pp_ui.product.setCurrentIndex(a_index)
			a_index+=1

		mw_ui.edit_pp_ui.packing_name.setText(data[0])
		mw_ui.edit_pp_ui.packing_code.setText(data[1])
		mw_ui.edit_pp_ui.quantity.setValue(data[3])
		


		def view_p_units():
			mw_ui.edit_pp_ui.unit.clear()
			material_type = database_controller.get_data(mw_ui.main_data_base , 'UnpackedProduct', columns='material_type', condition=f'where id = {mw_ui.edit_pp_ui.product.currentData()}')[0][0]
			a_index=0
			for unit in database_controller.material_types[material_type.lower()]:
				mw_ui.edit_pp_ui.unit.addItem(unit)
				if data[4] == unit:
					mw_ui.edit_pp_ui.unit.setCurrentIndex(a_index)
				a_index+=1


		def add_pm(material_name,material_id,count):

				mw_ui.edit_pp_ui.tableWidget.setRowCount(mw_ui.edit_pp_ui.tableWidget.rowCount()+1)
				
				item = QtWidgets.QTableWidgetItem()
				item.setText(material_name)
				item.setData(4,material_id)
				mw_ui.edit_pp_ui.tableWidget.setItem(mw_ui.edit_pp_ui.tableWidget.rowCount()-1,0,item)

				item = QtWidgets.QTableWidgetItem()
				item.setText(str(count))
				item.setData(4,count)
				mw_ui.edit_pp_ui.tableWidget.setItem(mw_ui.edit_pp_ui.tableWidget.rowCount()-1,1,item)

				try:
					mw_ui.edit_pp_ui.add_uppm_ui.close()
					mw_ui.edit_pp_ui.added_rm.append((mw_ui.packed_product_list.currentItem().data(4),material_id[0],count))
				except:
					pass

				
				

		def open_add_packing_material_window():
				mw_ui.edit_pp_ui.add_uppm_window =QtWidgets.QDialog()
				mw_ui.edit_pp_ui.add_uppm_window.setWindowModality(QtCore.Qt.ApplicationModal)
				mw_ui.edit_pp_ui.add_uppm_ui = uic.loadUi('windows/AddPackedProductPackingMaterial.ui', mw_ui.edit_pp_ui.add_uppm_window)
				mw_ui.edit_pp_ui.add_uppm_ui.setStyleSheet(mw_ui.current_style)
				mw_ui.edit_pp_ui.add_uppm_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
				mw_ui.edit_pp_ui.add_uppm_ui.add.setIcon(mw_ui.add_icon)

				materials = database_controller.get_data(mw_ui.main_data_base , 'PackingMaterial', columns='name,id')
				
				for material in materials:
					mw_ui.edit_pp_ui.add_uppm_ui.material.addItem(material[0],material[1])

				mw_ui.edit_pp_ui.add_uppm_ui.show()
				
				mw_ui.edit_pp_ui.add_uppm_ui.add.clicked.connect(lambda:add_pm( mw_ui.edit_pp_ui.add_uppm_ui.material.currentText(),(mw_ui.edit_pp_ui.add_uppm_ui.material.currentData(),None),mw_ui.edit_pp_ui.add_uppm_ui.count.value() ))

		def delete_pm_row():
			try:
				maerial_id=(mw_ui.edit_pp_ui.tableWidget.item(mw_ui.edit_pp_ui.tableWidget.currentRow(),0).data(4))
				

				if maerial_id[1]==None:
					count			= mw_ui.edit_pp_ui.tableWidget.item(mw_ui.edit_pp_ui.tableWidget.currentRow(),1).text()
					mw_ui.edit_pp_ui.added_rm.remove((mw_ui.packed_product_list.currentItem().data(4), maerial_id[0], float(count)))

				else:
					mw_ui.edit_pp_ui.deleted_rm.append(maerial_id)
				mw_ui.edit_pp_ui.tableWidget.removeRow(mw_ui.edit_pp_ui.tableWidget.currentRow())
			except:
				pass
		

		def edit_up():
			
			database_controller.edit(mw_ui,'PackedProduct',(
						mw_ui.edit_pp_ui.packing_name.text(),
						mw_ui.edit_pp_ui.packing_code.text(),
						mw_ui.edit_pp_ui.product.currentData(), 
						mw_ui.edit_pp_ui.quantity.value(), 
						mw_ui.edit_pp_ui.unit.currentText(),
					)
						,mw_ui.packed_product_list.currentItem().data(4))
			
			views.fill_out_list(mw_ui.counts_labels,mw_ui.main_data_base, mw_ui.packed_product_list 	, 'PackedProduct' 	, (1,2)  		,'{0}	({1})'				, 0 )
			for rm in mw_ui.edit_pp_ui.deleted_rm:
				database_controller.delete(mw_ui,mw_ui.main_data_base, 'PackedProductPackingMaterial', rm[1])
			for rm in mw_ui.edit_pp_ui.added_rm:
				database_controller.add(mw_ui,'PackedProductPackingMaterial',rm)
			mw_ui.edit_pp_ui.saved=True
			mw_ui.edit_pp_ui.close()


		packing_materials = database_controller.get_data(mw_ui.main_data_base , 'PackedProductPackingMaterial', columns='count, packing_material,id', condition=f'where packed_product = {mw_ui.packed_product_list.currentItem().data(4)}')

		for i in packing_materials:
			material_name = database_controller.get_data(mw_ui.main_data_base , 'PackingMaterial', columns=' name', condition=f'where id = {i[1]}')[0][0]
			add_pm(material_name,(i[1],i[2]),i[0])

		view_p_units()
		mw_ui.edit_pp_ui.product.currentIndexChanged.connect(view_p_units) 
		mw_ui.edit_pp_ui.add_packing_material.clicked.connect(open_add_packing_material_window)
		mw_ui.edit_pp_ui.remove_row.clicked.connect(delete_pm_row)
		mw_ui.edit_pp_ui.edit.clicked.connect(edit_up)


		mw_ui.edit_pp_window.show()
	
	except:
		notification(mw_ui,'NO ITEM SELECTED', f'Plaese select item to edit it')

def open_edit_order_window(mw_ui):
	try:
		mw_ui.edit_o_window =QtWidgets.QDialog()
		mw_ui.edit_o_window.setWindowModality(QtCore.Qt.ApplicationModal)
		mw_ui.edit_o_ui = uic.loadUi('windows/EditOrder.ui', mw_ui.edit_o_window)
		mw_ui.edit_o_ui.setStyleSheet(mw_ui.current_style)
		mw_ui.edit_o_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)#

		config = configparser.ConfigParser()
		config.read('settings.ini')

		translation.retranslate_edit_order_window(mw_ui.edit_o_ui , dictionary.languages[config['settings']['current_language']])
		if config['settings']['current_language']=='ar':
			mw_ui.edit_o_ui.setLayoutDirection(QtCore.Qt.RightToLeft)
		else:
			mw_ui.edit_o_ui.setLayoutDirection(QtCore.Qt.LeftToRight)

		data 			= database_controller.get_data(mw_ui.main_data_base , '"Order"', columns='name, code, packed_product, quantity, starting_date, planned_finishing_date, actual_finishing_date, done', condition=f'where id = {mw_ui.orders_list.currentItem().data(4)}')[0]
		packed_product 	= database_controller.get_data(mw_ui.main_data_base , 'PackedProduct', columns='name', condition=f'where id = {data[2]}')[0][0]

		mw_ui.edit_o_ui.name.setText(data[0])
		mw_ui.edit_o_ui.code.setText(data[1])
		mw_ui.edit_o_ui.packed_product.setText(packed_product)
		mw_ui.edit_o_ui.quantity.setText(str(data[3]))
		mw_ui.edit_o_ui.starting_date.setDate(datetime.date.fromisoformat(data[4]))
		mw_ui.edit_o_ui.planned_finishing_date.setDate(datetime.date.fromisoformat(data[5]))
		mw_ui.edit_o_ui.actual_finishing_date.setDate(datetime.date.fromisoformat(data[6]))
		mw_ui.edit_o_ui.done.setChecked(data[7])

		def done_status_changed():
			if mw_ui.edit_o_ui.done.isChecked():
				mw_ui.edit_o_ui.actual_finishing_date.setDate(datetime.date.today())

		mw_ui.edit_o_ui.done.clicked.connect(done_status_changed)

		def edit_order():
			database_controller.edit(mw_ui,'"Order"',(
						mw_ui.edit_o_ui.name.text(),
						mw_ui.edit_o_ui.code.text(),
						data[2],
						data[3],
						mw_ui.edit_o_ui.starting_date.date().toPyDate().isoformat(),
						mw_ui.edit_o_ui.planned_finishing_date.date().toPyDate().isoformat(),
						mw_ui.edit_o_ui.actual_finishing_date.date().toPyDate().isoformat(),
						mw_ui.edit_o_ui.done.isChecked(),
					)
						,mw_ui.orders_list.currentItem().data(4))
			mw_ui.edit_o_ui.close()
			views.fill_out_orders_list(mw_ui)
			views.view_all_orders(mw_ui)
			
			
		mw_ui.edit_o_ui.edit.clicked.connect(edit_order)
		mw_ui.edit_o_ui.show()
	except:
		notification(mw_ui,'NO ITEM SELECTED', f'Plaese select item to edit it')

def open_mail_window(mw_ui,mail_type):
	

	mw_ui.mail_window =QtWidgets.QDialog()
	mw_ui.mail_window.setWindowModality(QtCore.Qt.ApplicationModal)
	mw_ui.mail_ui = uic.loadUi('windows/view_mail.ui', mw_ui.mail_window)
	mw_ui.mail_ui.setStyleSheet(mw_ui.current_style)
	mw_ui.mail_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
	config = configparser.ConfigParser()
	config.read('settings.ini')

	
	


	if mail_type=='inbox':

		data = database_controller.get_data(mw_ui.main_data_base,'inbox_mail',condition=f'where id = {mw_ui.inbox_mail.currentItem().data(4)}')[0]
		if mail_type=='inbox' and not data[-1]:
			mw_ui.inbox_mail.currentItem().setIcon(QtGui.QIcon(''))
			mw_ui.new_messages_count-=1
			mw_ui.tabWidget_3.setTabText(0, f'Inbox ({mw_ui.new_messages_count})')
			
		mw_ui.mail_ui.user_from.setText(data[1])
		mw_ui.mail_ui.user_to.setText('Me')
		
	else:

		data = database_controller.get_data(mw_ui.main_data_base,'outbox_mail',condition=f'where id = {mw_ui.outbox_mail.currentItem().data(4)}')[0]
		mw_ui.mail_ui.user_to.setText(data[1])
		mw_ui.mail_ui.user_from.setText('Me')

		if data[-2]:
			if data[-1]:
				mw_ui.mail_ui.status.setText('readed')

			else:
				mw_ui.mail_ui.status.setText('received')

	if mail_type=='inbox':
		if not data[-1] :
			if mw_ui.logged_in:
				try:
					a= mw_ui.session.get(config['login-settings']['url']+config['URLs']['readmail'].format(mw_ui.inbox_mail.currentItem().data(4)))

				except:
					database_controller.add(mw_ui,'readed_mails',[mw_ui.inbox_mail.currentItem().data(4)])
			else:
				database_controller.add(mw_ui,'readed_mails',[mw_ui.inbox_mail.currentItem().data(4)])

	mw_ui.mail_ui.body.setText('<html><head/><body><p>'+data[3].replace('\\r\\n','</p><p>')+'</p></body></html>')
	mw_ui.mail_ui.subject.setText(data[2])
	mw_ui.mail_ui.date.setText(data[4].split('T')[0])
	mw_ui.mail_ui.time.setText(data[4].split('T')[1].replace('Z','').split('.')[0])
	mw_ui.mail_ui.show()


# excell

def open_export_excell(mw_ui):
	mw_ui.ee_window =QtWidgets.QDialog()
	mw_ui.ee_window.setWindowModality(QtCore.Qt.ApplicationModal)
	mw_ui.ee_ui = uic.loadUi('windows/export_excel.ui', mw_ui.ee_window)
	mw_ui.ee_ui.setStyleSheet(mw_ui.current_style)
	mw_ui.ee_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)
	mw_ui.ee_ui.pm_frame.setVisible(False)
	mw_ui.ee_ui.unpp_frame.setVisible(False)
	mw_ui.ee_ui.pp_frame.setVisible(False)
	mw_ui.ee_ui.order_frame.setVisible(False)
	mw_ui.ee_ui.rm_count.setText(str(len(database_controller.get_data(mw_ui.main_data_base, 'RawMaterials'))))
	mw_ui.ee_ui.pm_count.setText(str(len(database_controller.get_data(mw_ui.main_data_base, 'PackingMaterial'))))
	mw_ui.ee_ui.unpp_count.setText(str(len(database_controller.get_data(mw_ui.main_data_base, 'UnpackedProduct'))))
	mw_ui.ee_ui.pp_count.setText(str(len(database_controller.get_data(mw_ui.main_data_base, 'PackedProduct'))))
	mw_ui.ee_ui.orders_count.setText(str(len(database_controller.get_data(mw_ui.main_data_base, '"Order"'))))


	config = configparser.ConfigParser()
	config.read('settings.ini')

	translation.retranslate_export_excell_window(mw_ui.ee_ui , dictionary.languages[config['settings']['current_language']])
	if config['settings']['current_language']=='ar':
		mw_ui.ee_ui.setLayoutDirection(QtCore.Qt.RightToLeft)
	else:
		mw_ui.ee_ui.setLayoutDirection(QtCore.Qt.LeftToRight)

	def get_rm_data():
		columns=[]
		columns_visible_names=[]
		if  mw_ui.ee_ui.rm_name.checkState():
			columns.append('name')
			columns_visible_names.append('Name')
		
		if  mw_ui.ee_ui.rm_code.checkState():
			columns.append('code')
			columns_visible_names.append('Code')
		
		if  mw_ui.ee_ui.rm_material_type.checkState():
			columns.append('m_type')
			columns_visible_names.append('Material type')
		
		if  mw_ui.ee_ui.rm_quantity.checkState():
			columns.append('quantity,unit')
			columns_visible_names.append('Quantity , Unit')
		
		if  mw_ui.ee_ui.rm_density.checkState():
			columns.append('density')
			columns_visible_names.append('Density')

		data = ','.join(columns_visible_names)
		columns=','.join(columns)

		for i in database_controller.get_data(mw_ui.main_data_base, 'RawMaterials', columns=columns):
			l=list(i)
			for b in range(len(l)):
				l[b]=str(l[b])

			data+=' \n '+','.join(l)
		return (data)


	def get_pm_data():
		columns=[]
		columns_visible_names=[]
		if  mw_ui.ee_ui.pm_name.checkState():
			columns.append('name')
			columns_visible_names.append('Name')
		
		if  mw_ui.ee_ui.pm_code.checkState():
			columns.append('code')
			columns_visible_names.append('Code')
		
		if  mw_ui.ee_ui.pm_quantity.checkState():
			columns.append('quantity,unit')
			columns_visible_names.append('Quantity, Unit')
		

		data = ','.join(columns_visible_names)
		columns=','.join(columns)

		for i in database_controller.get_data(mw_ui.main_data_base, 'PackingMaterial', columns=columns):
			l=list(i)
			for b in range(len(l)):
				l[b]=str(l[b])

			data+=' \n '+' , '.join(l)
		return (data)

	def get_unpp_data():
		columns=[]
		columns_visible_names=[]
		if  mw_ui.ee_ui.unpp_name.checkState():
			columns.append('name')
			columns_visible_names.append('Name')
		
		if  mw_ui.ee_ui.unpp_code.checkState():
			columns.append('code')
			columns_visible_names.append('Code')
		
		if  mw_ui.ee_ui.unpp_m_type.checkState():
			columns.append('material_type')
			columns_visible_names.append('Material type')
		
		if  mw_ui.ee_ui.unpp_quantity.checkState():
			columns.append('quantity,unit')
			columns_visible_names.append('Quantity, Unit')

		data = ','.join(columns_visible_names)
		columns=','.join(columns)

		for i in database_controller.get_data(mw_ui.main_data_base, 'UnpackedProduct', columns=columns):
			l=list(i)
			for b in range(len(l)):
				l[b]=str(l[b])

			data+=' \n '+' , '.join(l)
		return (data)

	def get_pp_data():
		columns=[]
		columns_visible_names=[]
		if  mw_ui.ee_ui.pp_name.checkState():
			columns.append('name')
			columns_visible_names.append('Name')
		
		if  mw_ui.ee_ui.pp_code.checkState():
			columns.append('code')
			columns_visible_names.append('Code')
		
		if  mw_ui.ee_ui.pp_unpp.checkState():
			columns.append('unpacked_product')
			columns_visible_names.append('Unpacked product')
		
		if  mw_ui.ee_ui.pp_quantity.checkState():
			columns.append('unpacked_product_quantity_in_one,unit')
			columns_visible_names.append('Quantity, Unit')

		data = ','.join(columns_visible_names)
		columns=','.join(columns)
		main_table_data = database_controller.get_data(mw_ui.main_data_base, 'PackedProduct', columns=columns)

		if 'unpacked_product' in columns:
			id_index = columns.split(',').index('unpacked_product')
			for i in range(len(main_table_data)):
				main_table_data[i] = list(main_table_data[i])
				main_table_data[i][id_index] = database_controller.get_data(mw_ui.main_data_base, 'UnpackedProduct', columns='name', condition=f'where id = {main_table_data[i][id_index]}')[0][0]




		for i in main_table_data:
			l=list(i)
			for b in range(len(l)):
				l[b]=str(l[b])

			data+=' \n '+' , '.join(l)
		return data

	def get_order_data():
		columns=[]
		columns_visible_names=[]
		if  mw_ui.ee_ui.order_name.checkState():
			columns.append('name')
			columns_visible_names.append('Name')
		
		if  mw_ui.ee_ui.order_code.checkState():
			columns.append('code')
			columns_visible_names.append('Code')
		
		if  mw_ui.ee_ui.order_pfd.checkState():
			columns.append('planned_finishing_date')
			columns_visible_names.append('Planned finishing date')

		if  mw_ui.ee_ui.order_pp.checkState():
			columns.append('packed_product')
			columns_visible_names.append('Packed product')

		if  mw_ui.ee_ui.order_quantity.checkState():
			columns.append('quantity')
			columns_visible_names.append('Quantity')


		if  mw_ui.ee_ui.order_sd.checkState():
			columns.append('starting_date')
			columns_visible_names.append('Starting date')
		
		if  mw_ui.ee_ui.order_afd.checkState():
			columns.append('actual_finishing_date')
			columns_visible_names.append('Actual finishing date')

		data = ','.join(columns_visible_names)
		columns=','.join(columns)
		main_table_data = database_controller.get_data(mw_ui.main_data_base, '"Order"', columns=columns)

		if 'packed_product' in columns:
			id_index = columns.split(',').index('packed_product')
			for i in range(len(main_table_data)):
				main_table_data[i] = list(main_table_data[i])
				main_table_data[i][id_index] = database_controller.get_data(mw_ui.main_data_base, 'PackedProduct', columns='name', condition=f'where id = {main_table_data[i][id_index]}')[0][0]




		for i in main_table_data:
			l=list(i)
			for b in range(len(l)):
				l[b]=str(l[b])

			data+=' \n '+' , '.join(l)
		return data

	
	def export():
		file_name=QFileDialog.getSaveFileName(mw_ui.ee_ui,"create INSPP file","","Excel Files (*.csv)")

		if mw_ui.ee_ui.rm_radio_button.isChecked():
			data=get_rm_data()

		elif mw_ui.ee_ui.pm_radio_button.isChecked():
			data=get_pm_data()
		
		elif mw_ui.ee_ui.unpp_radio_button.isChecked():
			data=get_unpp_data()
		
		elif mw_ui.ee_ui.pp_radio_button.isChecked():
			data=get_pp_data()
		
		elif mw_ui.ee_ui.order_radio_button.isChecked():
			data=get_order_data()

		file = open(file_name[0]+'.csv', 'w')
		file.write(data)
		file.close()

	mw_ui.ee_ui.export_button.clicked.connect(export)
	mw_ui.ee_ui.show()

def notification(mw_ui,title, body, important=0):
	
	if mw_ui.notifications_popup:

		
		notification = notify2.Notification(title,body,"icons/INSPP_logo.png")
		
		notification.show()


	config = configparser.ConfigParser()
	config.read('settings.ini')

	if important or (not int(config['settings']['add_only_important_notifications'])):
		item = QtWidgets.QListWidgetItem()
		item.setData(2,body.replace('\n','. '))
		mw_ui.Important_notifications.insertItem(0,item)
		mw_ui.important_notifications_count+=1

				
		
		icon	= QtGui.QIcon()
		icon_folder=config['icons themes folders'][config['settings']['style']]
		if mw_ui.notifications_mode:
				icon.addPixmap(QtGui.QPixmap(f"{icon_folder}/notifications +.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
				
		else:
				icon.addPixmap(QtGui.QPixmap(f"{icon_folder}/notifications.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		mw_ui.tabWidget_2.setTabIcon(0,icon)
		mw_ui.tabWidget_2.setTabText(0, f'({mw_ui.important_notifications_count})')
	
	if mw_ui.notifications_sound:
		playsound('sounds/notification.mp3')

def OpenSettingsWindow(mw_ui):
	mw_ui.settings_win =QtWidgets.QDialog()
	mw_ui.settings_ui = uic.loadUi('windows/settings.ui', mw_ui.settings_win)
	mw_ui.settings_ui.setStyleSheet(mw_ui.current_style)
	mw_ui.settings_ui.setAttribute(QtCore.Qt.WA_DeleteOnClose)


#
	config = configparser.ConfigParser()
	config.read('settings.ini')

	translation.retranslat_settings_window(mw_ui.settings_ui , dictionary.languages[config['settings']['current_language']])
	if config['settings']['current_language']=='ar':
		mw_ui.settings_ui.setLayoutDirection(QtCore.Qt.RightToLeft)
	else:
		mw_ui.settings_ui.setLayoutDirection(QtCore.Qt.LeftToRight)


	config = configparser.ConfigParser()
	config.read('settings.ini')

	mw_ui.settings_ui.notification_sound.setChecked(int(config['settings']['notification_sound']))
	def change_notification_sound_status():
		config['settings']['notification_sound']=str(int(mw_ui.settings_ui.notification_sound.isChecked()))
		config.write(open('settings.ini','w'))
		mw_ui.notifications_sound = int(mw_ui.settings_ui.notification_sound.isChecked())
	mw_ui.settings_ui.notification_sound.clicked.connect(change_notification_sound_status)

	mw_ui.settings_ui.notification_popup.setChecked(int(config['settings']['notification_popup']))
	def change_notification_popup_status():
		config['settings']['notification_popup']=str(int(mw_ui.settings_ui.notification_popup.isChecked()))
		config.write(open('settings.ini','w'))
		mw_ui.notifications_popup = int(mw_ui.settings_ui.notification_popup.isChecked())
	mw_ui.settings_ui.notification_popup.clicked.connect(change_notification_popup_status)

	mw_ui.settings_ui.add_only_important_notifications.setChecked(int(config['settings']['add_only_important_notifications']))
	def change_add_only_important_notifications_status():
		config['settings']['add_only_important_notifications']=str(int(mw_ui.settings_ui.add_only_important_notifications.isChecked()))
		config.write(open('settings.ini','w'))
	mw_ui.settings_ui.add_only_important_notifications.clicked.connect(change_add_only_important_notifications_status)

	mw_ui.settings_ui.AutoBackup.setChecked(int(config['settings']['auto_backup']))
	mw_ui.settings_ui.auto_backup_frame.setEnabled(int(config['settings']['auto_backup']))

	def refresh_backup_timer(mw_ui):
		mw_ui.auto_backup=0
		time.sleep(mw_ui.backup_term+1)
		mw_ui.auto_backup=1
		threading.Thread(target=functions.backup_timer, args=(mw_ui,)).start()

	def change_AutoBackup_status():
		config['settings']['auto_backup']=str(int(mw_ui.settings_ui.AutoBackup.isChecked()))
		config.write(open('settings.ini','w'))
		mw_ui.auto_backup = mw_ui.settings_ui.AutoBackup.isChecked()
		if mw_ui.settings_ui.AutoBackup.isChecked() :

			threading.Thread(target=refresh_backup_timer, args=(mw_ui,)).start()

	mw_ui.settings_ui.AutoBackup.clicked.connect(change_AutoBackup_status)

	def get_backup_folder_path():
		folder_path=QFileDialog.getExistingDirectory(mw_ui.settings_ui,"open INSPP file","")
		mw_ui.settings_ui.auto_backup_path.setText(folder_path)

	def backup_time_changed(name, value):
		config['settings'][name]=str(value.value())
		config.write(open('settings.ini','w'))
	

	def apply_backup_change():
		backup_time_changed('backup_year', mw_ui.settings_ui.year_count)
		backup_time_changed('backup_month', mw_ui.settings_ui.month_count)
		backup_time_changed('backup_day', mw_ui.settings_ui.day_count)
		backup_time_changed('backup_hour', mw_ui.settings_ui.hour_count)

		config['settings']['backup_location']=mw_ui.settings_ui.auto_backup_path.text()
		config.write(open('settings.ini','w'))

		threading.Thread(target=refresh_backup_timer, args=(mw_ui,)).start()

	mw_ui.settings_ui.year_count.setValue(int(config['settings']['backup_year']))
	mw_ui.settings_ui.month_count.setValue(int(config['settings']['backup_month']))
	mw_ui.settings_ui.day_count.setValue(int(config['settings']['backup_day']))
	mw_ui.settings_ui.hour_count.setValue(int(config['settings']['backup_hour']))

	mw_ui.settings_ui.apply_backup.clicked.connect(apply_backup_change)
	

	mw_ui.settings_ui.get_backup_folder_path.clicked.connect(get_backup_folder_path)





	mw_ui.settings_ui.show()

def watting_window(mw_ui,detail):
	mw_ui.watting_win = QtWidgets.QWidget()
	mw_ui.watting_ui =uic.loadUi('windows/watting_win.ui', mw_ui.watting_win)
	mw_ui.watting_win.setWindowModality(QtCore.Qt.ApplicationModal)
	mw_ui.watting_win.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
	

	qtRectangle = mw_ui.watting_win.frameGeometry()
	centerPoint = QDesktopWidget().availableGeometry().center()
	qtRectangle.moveCenter(centerPoint)
	mw_ui.watting_win.move(qtRectangle.topLeft())
	mw_ui.watting_win.setAttribute(Qt.WA_TranslucentBackground)

	mw_ui.watting_ui.detail.setText(detail)

	mw_ui.watting_ui.movie = QMovie("GIFs/loading.gif")
	mw_ui.watting_ui.GIF.setMovie(mw_ui.watting_ui.movie)
	mw_ui.watting_ui.movie.start()
	

	
	#return mw_ui.watting_ui

def OpenChangeLanguageWindow(mw_ui):
	mw_ui.change_language_win = QtWidgets.QWidget()
	mw_ui.change_language_ui =uic.loadUi('windows/ChangeLanguage.ui', mw_ui.change_language_win)
	mw_ui.change_language_win.setWindowModality(QtCore.Qt.ApplicationModal)
	mw_ui.change_language_win.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
	mw_ui.change_language_ui.setStyleSheet(mw_ui.current_style)

	qtRectangle = mw_ui.change_language_win.frameGeometry()
	centerPoint = QDesktopWidget().availableGeometry().center()
	qtRectangle.moveCenter(centerPoint)
	mw_ui.change_language_win.move(qtRectangle.topLeft())

	languages_files = os.listdir('languages')
	
	config = configparser.ConfigParser()
	config.read('settings.ini')
	a=0
	for lang in languages_files:
		
		if lang[len(lang)-2:]=='py':
			
			lang_model_name = lang.split('.')[0]
			language_file = __import__(f'languages.{lang_model_name}', fromlist=['object'])
			mw_ui.change_language_ui.languages.addItem(language_file.Language_view_name,language_file.language_shortcut)
			if config['settings']['current_language'] == language_file.language_shortcut:
				mw_ui.change_language_ui.languages.setCurrentIndex(a)
			a=a+1
	
	def ch():
		functions.change_language(mw_ui,mw_ui.change_language_ui.languages)
		mw_ui.change_language_ui.close()

	mw_ui.change_language_ui.languages.currentIndexChanged.connect(ch)

	mw_ui.change_language_ui.show()


def ins_login(mw_ui):
	mw_ui.ins_login_win = QtWidgets.QWidget()
	mw_ui.ins_login_ui =uic.loadUi('windows/INS_login_window.ui', mw_ui.ins_login_win)
	mw_ui.ins_login_win.setWindowModality(QtCore.Qt.ApplicationModal)
	mw_ui.ins_login_ui.setStyleSheet(mw_ui.current_style)

	config = configparser.ConfigParser()
	config.read('settings.ini')#save_data_status

	mw_ui.ins_login_ui.save_data_status.setChecked(int(config['login-settings']['save']))
	if int(config['login-settings']['save']):
		mw_ui.ins_login_ui.url.setText(config['login-settings']['url'])
		mw_ui.ins_login_ui.username.setText(config['login-settings']['username'])
		mw_ui.ins_login_ui.password.setText(config['login-settings']['password'])

	def login():
		ret = INSClient.login(mw_ui,mw_ui.ins_login_ui.url.text(),mw_ui.ins_login_ui.username.text(),mw_ui.ins_login_ui.password.text())
		if ret[0]:
			
			config['login-settings']['url'] = str(mw_ui.ins_login_ui.url.text())
			config['login-settings']['username'] = str(mw_ui.ins_login_ui.username.text())
			config['login-settings']['password'] = str(mw_ui.ins_login_ui.password.text())
			config.write(open('settings.ini','w'))
			mw_ui.ins_login_ui.close()

			notification(mw_ui , 'INS Server', 'Successfully logged in to the INS server \n please wait until synchronization completed...')
			
			mw_ui.loading_gif.show()
			threading.Thread(target = synch_center.init(mw_ui.session,mw_ui)).start()
			
			
			
		else:
			mw_ui.ins_login_ui.message.setText(ret[1][1:-1])

	def change_save_status():
		config['login-settings']['save'] = str(int(mw_ui.ins_login_ui.save_data_status.isChecked()))
		config.write(open('settings.ini','w'))

	mw_ui.ins_login_ui.save_data_status.clicked.connect(change_save_status)


	mw_ui.ins_login_ui.login.clicked.connect(login)
	mw_ui.ins_login_ui.show()
