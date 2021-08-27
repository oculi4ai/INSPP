
def translate_main_window(mw_ui,lang):
        item = mw_ui.all_orders.verticalHeaderItem(0)
        item.setText(lang["monthes"])
        mw_ui.rm_label.setText(lang["raw materials"])
        mw_ui.materials_and_products_widget.setTabToolTip(0,lang["raw materials"])

        mw_ui.pm_label.setText(lang["packing materials"])
        mw_ui.materials_and_products_widget.setTabToolTip(1,lang["packing materials"])

        mw_ui.upp_label.setText(lang["unpacked products"])
        mw_ui.materials_and_products_widget.setTabToolTip(2,lang["unpacked products"])

        mw_ui.pp_label.setText(lang["packed products"])
        mw_ui.materials_and_products_widget.setTabToolTip(3,lang["packed products"])

        mw_ui.tabWidget_3.setTabText(0,lang["Inbox"])
        mw_ui.tabWidget_3.setTabText(1,lang["Outbox"])
        mw_ui.label.setText(lang["To:"])
        mw_ui.label_2.setText(lang["Subject:"])
        mw_ui.mail_body.setPlaceholderText(lang['Compose mail'])

        mw_ui.add_rm.setToolTip(lang['add'])
        mw_ui.add_pm.setToolTip(lang['add'])
        mw_ui.add_unpacked_product.setToolTip(lang['add'])
        mw_ui.add_packed_product.setToolTip(lang['add'])
        mw_ui.add_order.setToolTip(lang['add'])
        mw_ui.add_rm_output.setToolTip(lang['add output'])
        mw_ui.add_rm_input.setToolTip(lang['add input'])
        mw_ui.add_pm_output.setToolTip(lang['add output'])
        mw_ui.add_pm_input.setToolTip(lang['add input'])

        mw_ui.edit_rm.setToolTip(lang['edit'])
        mw_ui.edit_pm.setToolTip(lang['edit'])
        mw_ui.edit_unpacked_product.setToolTip(lang['edit'])
        mw_ui.edit_packed_product.setToolTip(lang['edit'])
        mw_ui.edit_order.setToolTip(lang['edit'])

        mw_ui.delete_rm.setToolTip(lang['delete'])
        mw_ui.delete_pm.setToolTip(lang['delete'])
        mw_ui.delete_unpacked_product.setToolTip(lang['delete'])
        mw_ui.delete_packed_product.setToolTip(lang['delete'])
        mw_ui.delete_order.setToolTip(lang['delete'])
        mw_ui.clear_notifications.setToolTip(lang['clear all'])

        mw_ui.tabWidget.setTabText(0,lang['orders timetable'])
        mw_ui.tabWidget.setTabText(1,lang['orders'])

        mw_ui.menuFile.setTitle(lang['file'])
        mw_ui.menuExport.setTitle(lang['export'])
        mw_ui.export_excell_button.setText(lang['export excel'])
        mw_ui.actionSettings.setText(lang['settings'])



def retranslate_add_rm_window(self, lang):
        self.setWindowTitle(lang['add raw material'])
        self.label_5.setText(lang["Material Name :"])
        self.label_17.setText(lang["Matiral Types :"])
        self.label_4.setText(lang["Code :"])
        self.label_24.setText(lang["Material density :"])
        self.label_20.setText(lang["Low Quantity :"])
        self.label_19.setText(lang["Available Quantity :"])
        self.loq_warning.setText(lang["Low Quantity Warning"])

def retranslate_add_pm_window(self, lang):
        self.setWindowTitle(lang['add packing material'])
        self.label_5.setText(lang["Material Name :"])
        self.label_4.setText(lang["Code :"])
        self.label_19.setText(lang["Available Quantity :"])
        self.loq_warning.setText(lang["Low Quantity Warning"])
        self.label_20.setText(lang["Low Quantity :"])

def retranslate_add_packed_product_window(self, lang):
        self.setWindowTitle(lang['add packed product'])
        self.label_8.setText(lang["Product :"])
        self.label_2.setText(lang["Packing name :"])
        self.ddd.setText(lang["Product quantity :"])
        self.label_3.setText(lang["Code :"])


def retranslate_add_unpacked_product_window(self, lang):
        self.setWindowTitle(lang['add unpacked product'])
        self.ddd.setText(lang["Quantity :"])
        self.progressBar.setFormat(lang["%p% Composed"])
        self.label_2.setText(lang["Product Name :"])
        self.label_3.setText(lang["Code :"])
        self.label_8.setText(lang["Mateiral Types :"])
        

def retranslate_add_order_window(self, lang):
        self.setWindowTitle(lang['add order'])
        self.ddd.setText(lang["Product quantity :"])
        self.label.setText(lang["Starting date :"])
        self.label_2.setText(lang["Order name :"])
        self.label_3.setText(lang["Code :"])
        self.label_8.setText(lang["Product"])
        self.label_4.setText(lang["Planned finishing date :"])
        self.label_5.setText(lang["Actual finishing data"])
        self.done.setText(lang["DONE"])

def retranslate_add_pp_packing_material_window(self, lang):
        self.setWindowTitle(lang['add packing material'])
        self.label_8.setText(lang["Packing Matrial"])
        self.label_5.setText(lang["count in product"])
        

def retranslate_add_unpp_raw_material_window(self, lang):
        self.setWindowTitle(lang['add raw material'])
        self.label_8.setText(lang["Matiral"])
        self.label_5.setText(lang["Percent"])

def retranslate_edit_rm_window(self, lang):
        self.setWindowTitle(lang['edit raw material'])
        self.label_19.setText(lang["Available Quantity :"])
        self.label_5.setText(lang["Material Name :"])
        self.loq_warning.setText(lang["Low Quantity Warning"])
        self.label_17.setText(lang["Matiral Types :"])
        self.label_24.setText(lang["Material density :"])
        self.label_20.setText(lang["Low Quantity :"])
        self.label_4.setText(lang["Code :"])
        self.label.setText(lang["Input"])
        self.label_2.setText(lang["Output"])


def retranslate_edit_pm_window(self, lang):
        self.setWindowTitle(lang['edit packing material'])
        self.label_5.setText(lang["Material Name :"])
        self.label_4.setText(lang["Code :"])
        self.label_19.setText(lang["Available Quantity :"])
        self.loq_warning.setText(lang["Low Quantity Warning"])
        self.label_20.setText(lang["Low Quantity :"])
        self.label.setText(lang["Input"])
        self.label_2.setText(lang["Output"])
  

def retranslate_edit_up_window(self, lang):
        self.setWindowTitle(lang['edit unpacked product'])
        self.ddd.setText(lang["Quantity :"])
        self.progressBar.setFormat(lang["%p% Composed"])
        self.label_2.setText(lang["Product Name :"])
        self.label_3.setText(lang["Code :"])
        self.label_8.setText(lang["Mateiral Types :"])
        

def retranslate_edit_packed_product_window(self, lang):
        self.setWindowTitle(lang['edit packed product'])
        self.label_8.setText(lang["Product :"])
        self.label_2.setText(lang["Packing name :"])
        self.ddd.setText(lang["Product quantity :"])
        self.label_3.setText(lang["Code :"])
    

def retranslate_edit_order_window(self, lang):
        self.setWindowTitle(lang['edit order'])
        self.ddd.setText(lang["Product quantity :"])
        self.label_5.setText(lang["Actual finishing data"])
        self.label_4.setText(lang["Planned finishing date :"])
        self.label_8.setText(lang["Product :"])
        self.label_2.setText(lang["Order name :"])
        self.label_3.setText(lang["Code :"])
        self.label.setText(lang["Starting date :"])
        self.done.setText(lang["DONE"])


def retranslate_export_excell_window(self, lang):
        self.setWindowTitle(lang["Export Excel"])
        self.export_button.setText(lang["Export"])
        self.unpp_radio_button.setText(lang["Unpacked products"])
        self.pm_radio_button.setText(lang["Packing materials"])
        self.pp_radio_button.setText(lang["Packed products"])
        self.rm_radio_button.setText(lang["Raw materials"])
        self.pp_unpp.setText(lang["Unpacked product"])
        self.pp_name.setText(lang["Name"])
        self.pp_code.setText(lang["Code"])
        self.pp_quantity.setText(lang["quantity"])
        self.label_3.setText(lang["Products count"])
        self.unpp_name.setText(lang["Name"])
        self.unpp_code.setText(lang["Code"])
        self.unpp_quantity.setText(lang["Quantity"])
        self.unpp_m_type.setText(lang["Material type"])
        self.label_6.setText(lang["Products count"])
        self.pm_quantity.setText(lang["Quantity"])
        self.pm_code.setText(lang["Code"])
        self.pm_name.setText(lang["Name"])
        self.label.setText(lang["Materials count"])
        self.rm_density.setText(lang["Density"])
        self.rm_name.setText(lang["Name"])
        self.rm_code.setText(lang["Code"])
        self.rm_material_type.setText(lang["Material type"])
        self.rm_quantity.setText(lang["Quantity"])
        self.label_2.setText(lang["Materials count"])
        self.order_sd.setText(lang["starting date"])
        self.order_code.setText(lang["Code"])
        self.order_pp.setText(lang["Packed product"])
        self.order_quantity.setText(lang["quantity"])
        self.order_name.setText(lang["Name"])
        self.order_pfd.setText(lang["Planned finishing date"])
        self.order_afd.setText(lang["Actual finishing date"])
        self.label_5.setText(lang["Orders"])
        self.order_radio_button.setText(lang["Orders"])
        self.cancel.setText(lang["Cancel"])


def retranslat_settings_window(self, lang):
        self.setWindowTitle(lang["Settings"])
        self.groupBox.setTitle(lang["Notifications"])
        self.notification_sound.setText(lang["Sound ON"])
        self.notification_popup.setText(lang["Popup"])
        self.add_only_important_notifications.setText(lang["Show only important notifications in 'Notifications section'"])
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), lang["General"])
        self.AutoBackup.setText(lang["Auto backup"])
        self.label.setText(lang["Year"])
        self.label_2.setText(lang["Month"])
        self.label_3.setText(lang["Day"])
        self.label_5.setText(lang["Backup every :"])
        self.get_backup_folder_path.setText("...")
        self.label_4.setText(lang["Hour"])
        self.apply_backup.setText(lang["Apply"])
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), lang["backup"])