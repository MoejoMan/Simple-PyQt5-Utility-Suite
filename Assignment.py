import sys
import os
import PyQt5
import NewIcons
import random
import socket
import ftplib
import requests
from ftplib import FTP
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow,QInputDialog, QMessageBox, QStackedWidget, QDialog

class Dashboard1(QMainWindow):
    def __init__(self):
        super(Dashboard1, self).__init__()
        loadUi('Dashboard.ui', self)
        self.setWindowTitle("Dashboard")
        self.setMaximumSize(1920, 1080)
        self.setMinimumSize(930, 580)
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
        self.id_mapping = {}

        self.timeLabel.setText("Welcome to the Dashboard")
        self.calendarWidget.hide()

        self.buttonDateTime.clicked.connect(self.time_update)
        self.buttonIP.clicked.connect(self.ip_address)
        self.buttonDirList.clicked.connect(self.list_remote_home_directory)
        self.buttonRemoteFile.clicked.connect(self.show_backup_dialog)
        self.buttonSaveWeb.clicked.connect(self.web_page)
        self.MenuPushButton.clicked.connect(self.hide_menu)


        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.is_updating_time = False
        self.is_ip_visible = False
    
    FTP_HOST = "localhost" # a localhost FTP server will work here
    FTP_USER = "Placeholder"
    FTP_PASS = "Placeholder"

    def hide_menu(self):
        if self.frame_3.isHidden():
            self.frame_3.show()
        else:
            self.frame_3.hide()

    def show_backup_dialog(self):
        self.backup_dialog = FTPBackup()
        self.backup_dialog.exec_()

    def list_remote_home_directory(self):
        if getattr(self, 'is_ftp_list_shown', False): 
            self.RemoteLabel.setText("Remote Home Dir Hidden")
            self.is_ftp_list_shown = False
        else:
            try:
                ftp = ftplib.FTP(self.FTP_HOST)
                ftp.login(self.FTP_USER, self.FTP_PASS)
                print("Connected to FTP server")
                
                files = ftp.nlst()
                print("Retrieved directory listing")
                directory_listing = "\n".join(files)
                self.RemoteLabel.setText(f"Remote Home\nDirectory Listing:\n\n{directory_listing}")                
                self.is_ftp_list_shown = True
                ftp.quit()
                print("Disconnected from FTP server")
            except Exception as e:
                self.RemoteLabel.setText(f"An error occurred: {e}")
                print(f"An error occurred: {e}")


    def time_update(self):
        if self.is_updating_time:
            self.timer.stop()
            self.timeLabel.setText("Time update stopped")
            self.is_updating_time = False
            self.calendarWidget.hide()

        else:
            self.calendarWidget.show()
            current_time = QTime.currentTime().toString("HH:mm:ss")
            self.timeLabel.setText(f"Current Time: {current_time}\n")
            self.timer.start(1000)
            self.is_updating_time = True

    def update_time(self):
        current_time = QTime.currentTime().toString("HH:mm:ss")
        self.timeLabel.setText(f"Current Time: {current_time}\n")

    
    def ip_address(self):
        if self.is_ip_visible:
            self.is_ip_visible = False
            self.IPLabel.setText("IP Address hidden")
        else:
            self.show_ip_address()
            self.is_ip_visible = True

    def show_ip_address(self):
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        self.IPLabel.setText(f"IP Address: {ip_address}\n")
        self.IPLabel.show()

    def web_page(self):
        url, ok = QInputDialog.getText(self, "Save Web Page", "Enter the URL of the web page to save:")
        if not ok or not url.strip():
            self.show_message("Operation canceled", "You didn't enter a URL.")
            return

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            options = QFileDialog.Options()
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Web Page",
                "",
                "HTML Files (*.html);;All Files (*.*)",
                options=options
            )

            if save_path:
                with open(save_path, "w", encoding="utf-8") as file:
                    file.write(response.text)
                self.show_message("Success", f"Web page saved successfully to:\n{save_path}")
            else:
                self.show_message("Operation canceled", "You didn't choose a save location.")

        except requests.RequestException as e:
            self.show_message("Error", f"Failed to fetch the web page:\n{e}")

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)


class FTPBackup(QDialog):
    def __init__(self):
        super().__init__()

        self.FTP_HOST = "localhost"
        self.FTP_USER = "Placeholder"
        self.FTP_PASS = "Placeholder"
        self.center_window()
        self.setWindowTitle("FTP Backup")

        
    def center_window(self):
        screen_geometry = QApplication.desktop().screenGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        x_pos = (screen_width - 1275) // 2
        y_pos = (screen_height - 290) // 2

        self.move(x_pos, y_pos)

        self.layout = QVBoxLayout(self)
        self.file_list_widget = QListWidget(self)
        self.layout.addWidget(self.file_list_widget)

        self.backup_button = QPushButton("Backup Selected File", self)
        self.layout.addWidget(self.backup_button)

        self.backup_button.clicked.connect(self.trigger_backup)
        self.list_files_on_ftp()

    def list_files_on_ftp(self):
        try:
            ftp = ftplib.FTP(self.FTP_HOST)
            ftp.login(self.FTP_USER, self.FTP_PASS)

            files = ftp.nlst()  
            for file in files:
                self.file_list_widget.addItem(file)  

            ftp.quit()

        except Exception as e:
            print(f"An error occurred: {e}")

    def trigger_backup(self):
        selected_item = self.file_list_widget.currentItem()
        if selected_item:
            remote_file_path = selected_item.text()
            self.backup(remote_file_path)
        else:
            print("No file selected for backup.")

    def backup(self, remote_file_path):
        try:
            ftp = ftplib.FTP(self.FTP_HOST)
            ftp.login(self.FTP_USER, self.FTP_PASS)

            local_file_path = "/Placeholder/Placeholder/Placeholder/" + remote_file_path #change to the file path you wish to save to
            with open(local_file_path, "wb") as local_file:
                ftp.retrbinary(f"RETR {remote_file_path}", local_file.write)

            backup_file_path = remote_file_path + ".old"
            with open(local_file_path, "rb") as local_file:
                ftp.storbinary(f"STOR {backup_file_path}", local_file)

            os.remove(local_file_path)  
            self.show_confirmation_popup(f"Backup of {remote_file_path} was successful!")
            QTimer.singleShot(500, self.close)
            

            ftp.quit()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.show_error_popup("An error occurred while performing the backup.")
            QTimer.singleShot(500, self.close)

    def show_confirmation_popup(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Backup Success")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def show_error_popup(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Backup Error")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


widget = None

def create_main_window():
    global widget
    mainwindow = Dashboard1()
    widget = QStackedWidget()
    widget.addWidget(mainwindow)
    widget.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    create_main_window()
    sys.exit(app.exec_())