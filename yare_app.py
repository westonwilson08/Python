# This app will allow users to view time in Yare and submit new time
# It uses stored encrypted credentials for authenticating to the ServiceNow instance via REST API.

import datetime
import sys
import json
import os.path
import requests
from requests.auth import HTTPBasicAuth
from cryptography.fernet import Fernet
from PyQt5 import QtCore, QtGui, QtWidgets

sn_username = ''
sn_password = ''

today = datetime.date.today()
has_saved_credentials = False

# Week starts on Monday returns date only
current_week_start = datetime.datetime.now().day - datetime.date.weekday(today)

# set start date to first day of week returns YYYY-MM-DD format
current_start = today.replace(day=current_week_start)
start_date = current_start

new_work_endpoint = 'https://example.service-now.com/api/now/table/x_scope_yare_project_task_time_worked' \
                    '?sysparm_query=work_week.week_start=' + str(
    start_date) + '^user.user_name=javascript:gs.getUserName();'
project_team_endpoint = 'https://example.service-now.com/api/now/table/x_scope_yare_client_project_team' \
                        '?sysparm_query=team_member.user.user_name=javascript:gs.getUserName(); '

# set user and password if found
if os.path.isfile('./.sn_pass') and os.path.isfile('./.sn_user') and os.path.isfile('./.pass_key'):
    sn_user_file = open('./.sn_user', 'r')
    pass_file = open('./.sn_pass', 'r')
    sn_key_file = open('./.pass_key', 'r')
    sn_username = sn_user_file.read()
    sn_encrypted_pass = pass_file.read()
    pass_key = sn_key_file.read()
    cipher_suite = Fernet(pass_key.encode())
    decrypted_pass = cipher_suite.decrypt(sn_encrypted_pass.encode())
    sn_password = decrypted_pass.decode()
    has_saved_credentials = True

all_clients = ''
all_projects = ''
all_tasks = ''
get_projects = ''


# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'yare.ui'
#
# Created by: PyQt5 UI code generator 5.10.1


class Ui_Dialog(object):
    # Save username/password
    def __init__(self):
        self.frame_3 = QtWidgets.QFrame(Dialog)
        self.frame_2 = QtWidgets.QFrame(Dialog)
        self.frame = QtWidgets.QFrame(Dialog)
        self.tableWidget = QtWidgets.QTableWidget(self.frame_3)
        self.getTime = QtWidgets.QPushButton(Dialog)
        self.username = QtWidgets.QLineEdit(self.frame_2)
        self.password = QtWidgets.QLineEdit(self.frame_2)
        self.label_3 = QtWidgets.QLabel(self.frame_2)
        self.label_2 = QtWidgets.QLabel(self.frame_2)
        self.auth = QtWidgets.QPushButton(self.frame_2)
        self.label_10 = QtWidgets.QLabel(self.frame)
        self.hours = QtWidgets.QLineEdit(self.frame)
        self.addTime = QtWidgets.QPushButton(self.frame)
        self.label_7 = QtWidgets.QLabel(self.frame)
        self.date_worked = QtWidgets.QDateEdit(self.frame)
        self.task = QtWidgets.QComboBox(self.frame)
        self.project = QtWidgets.QComboBox(self.frame)
        self.client = QtWidgets.QComboBox(self.frame)
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.time_notes = QtWidgets.QPlainTextEdit(Dialog)
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label = QtWidgets.QLabel(Dialog)
        self.project_hours = QtWidgets.QTableWidget(Dialog)
        self.label_8 = QtWidgets.QLabel(Dialog)
        self.week = QtWidgets.QDateEdit(Dialog)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)

    def save_credentials(self):
        global has_saved_credentials
        if (not os.path.isfile('./.sn_pass')) or (
                os.path.isfile('./.sn_pass') and self.password.text() != sn_password) and not has_saved_credentials:
            print('saving/updating credentials')
            key = Fernet.generate_key()
            cipher_suite = Fernet(key)
            cipher_text = cipher_suite.encrypt(self.password.text().encode())
            sn_user_file = open('./.sn_user', 'w')
            sn_user_file.write(self.username.text())
            sn_user_file.close()
            pass_file = open('./.sn_pass', 'w')
            pass_file.write(cipher_text.decode())
            pass_file.close()
            sn_key_file = open('./.pass_key', 'w')
            sn_key_file.write(key.decode())
            sn_key_file.close()
            has_saved_credentials = True

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1043, 839)
        Dialog.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.buttonBox.setGeometry(QtCore.QRect(830, 770, 164, 32))
        self.buttonBox.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.week.setGeometry(QtCore.QRect(320, 150, 231, 31))
        self.week.setMinimumDate(QtCore.QDate(2019, 1, 1))
        self.week.setCalendarPopup(True)
        self.week.setCurrentSectionIndex(0)
        self.week.setObjectName("week")
        self.label_8.setGeometry(QtCore.QRect(330, 130, 59, 16))
        self.label_8.setObjectName("label_8")
        self.project_hours.setGeometry(QtCore.QRect(20, 190, 1001, 181))
        self.project_hours.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.ForbiddenCursor))
        self.project_hours.setObjectName("project_hours")
        self.project_hours.setColumnCount(9)
        self.project_hours.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.project_hours.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.project_hours.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.project_hours.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.project_hours.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.project_hours.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.project_hours.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.project_hours.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.project_hours.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.project_hours.setHorizontalHeaderItem(8, item)
        self.project_hours.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.label.setGeometry(QtCore.QRect(250, 550, 59, 16))
        self.label.setObjectName("label")
        self.label_4.setGeometry(QtCore.QRect(450, 550, 59, 16))
        self.label_4.setObjectName("label_4")
        self.label_5.setGeometry(QtCore.QRect(650, 550, 59, 16))
        self.label_5.setObjectName("label_5")
        self.time_notes.setGeometry(QtCore.QRect(250, 620, 591, 71))
        self.time_notes.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.time_notes.setObjectName("time_notes")
        self.label_6.setGeometry(QtCore.QRect(250, 600, 59, 16))
        self.label_6.setObjectName("label_6")
        self.frame.setGeometry(QtCore.QRect(90, 490, 861, 261))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.client.setGeometry(QtCore.QRect(150, 80, 201, 32))
        self.client.setObjectName("client")
        self.project.setGeometry(QtCore.QRect(350, 80, 201, 32))
        self.project.setObjectName("project")
        self.task.setGeometry(QtCore.QRect(550, 80, 201, 32))
        self.task.setObjectName("task")
        self.date_worked.setGeometry(QtCore.QRect(260, 30, 191, 22))
        self.date_worked.setMinimumDate(QtCore.QDate(2019, 1, 1))
        self.date_worked.setCalendarPopup(True)
        self.date_worked.setObjectName("date_worked")
        self.label_7.setGeometry(QtCore.QRect(270, 10, 151, 16))
        self.label_7.setObjectName("label_7")
        self.addTime.setGeometry(QtCore.QRect(390, 220, 114, 32))
        self.addTime.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.addTime.setObjectName("addTime")
        self.hours.setGeometry(QtCore.QRect(490, 30, 181, 21))
        self.hours.setMaxLength(5)
        self.hours.setObjectName("hours")
        self.label_10.setGeometry(QtCore.QRect(490, 10, 59, 16))
        self.label_10.setObjectName("label_10")
        self.frame_2.setGeometry(QtCore.QRect(300, 10, 431, 111))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.auth.setGeometry(QtCore.QRect(310, 50, 114, 32))
        self.auth.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.auth.setObjectName("auth")
        self.label_2.setGeometry(QtCore.QRect(10, 60, 81, 16))
        self.label_2.setObjectName("label_2")
        self.label_3.setGeometry(QtCore.QRect(10, 10, 111, 16))
        self.label_3.setObjectName("label_3")
        self.password.setGeometry(QtCore.QRect(10, 80, 291, 21))
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setObjectName("password")
        self.username.setGeometry(QtCore.QRect(10, 30, 291, 21))
        self.username.setObjectName("username")
        self.getTime.setGeometry(QtCore.QRect(570, 150, 114, 31))
        self.getTime.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.getTime.setObjectName("getTime")
        self.frame_3.setGeometry(QtCore.QRect(10, 130, 1021, 341))
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.tableWidget.setGeometry(QtCore.QRect(75, 250, 845, 56))
        self.tableWidget.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.ForbiddenCursor))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(8)
        self.tableWidget.setRowCount(1)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(7, item)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.frame_3.raise_()
        self.frame.raise_()
        self.frame_2.raise_()
        self.buttonBox.raise_()
        self.week.raise_()
        self.label_8.raise_()
        self.project_hours.raise_()
        self.label.raise_()
        self.label_4.raise_()
        self.label_5.raise_()
        self.time_notes.raise_()
        self.label_6.raise_()
        self.getTime.raise_()
        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        self.auth.clicked.connect(self.authenticate)

        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.username, self.password)
        Dialog.setTabOrder(self.password, self.week)
        Dialog.setTabOrder(self.week, self.project_hours)
        Dialog.setTabOrder(self.project_hours, self.date_worked)
        Dialog.setTabOrder(self.date_worked, self.hours)
        Dialog.setTabOrder(self.hours, self.client)
        Dialog.setTabOrder(self.client, self.project)
        Dialog.setTabOrder(self.project, self.task)
        Dialog.setTabOrder(self.task, self.time_notes)
        Dialog.setTabOrder(self.time_notes, self.addTime)
        Dialog.setTabOrder(self.addTime, self.tableWidget)

        self.week.setDate(current_start)
        self.date_worked.setDate(today)
        self.client.addItems(['--Select Client--'])

        if has_saved_credentials:
            self.username.setText(sn_username)
            self.password.setText(sn_password)
            self.get_time()

        if self.username.text() != '' and self.password.text() != '':
            self.getTime.clicked.connect(self.get_time)
            global all_clients
            global all_projects
            global all_tasks
            if all_clients == '':
                all_clients = self.get_all_clients()
            if all_projects == '':
                all_projects = self.get_all_projects()
            if all_tasks == '':
                all_tasks = self.get_all_tasks()
            self.client.currentIndexChanged.connect(lambda: self.resolve_projects(all_projects))
            self.project.currentIndexChanged.connect(lambda: self.resolve_tasks(all_tasks))
            self.addTime.clicked.connect(self.add_time)
        else:
            self.getTime.clicked.connect(self.authenticate)
            self.client.currentIndexChanged.connect(self.authenticate)
            self.project.currentIndexChanged.connect(self.authenticate)
            self.addTime.clicked.connect(self.authenticate)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Yare Time Tracking"))
        self.week.setDisplayFormat(_translate("Dialog", "MM/dd/yyyy"))
        self.label_8.setText(_translate("Dialog", "Week"))
        item = self.project_hours.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "Project"))
        item = self.project_hours.horizontalHeaderItem(1)
        item.setText(_translate("Dialog", "Monday"))
        item = self.project_hours.horizontalHeaderItem(2)
        item.setText(_translate("Dialog", "Tuesday"))
        item = self.project_hours.horizontalHeaderItem(3)
        item.setText(_translate("Dialog", "Wednesday"))
        item = self.project_hours.horizontalHeaderItem(4)
        item.setText(_translate("Dialog", "Thursday"))
        item = self.project_hours.horizontalHeaderItem(5)
        item.setText(_translate("Dialog", "Friday"))
        item = self.project_hours.horizontalHeaderItem(6)
        item.setText(_translate("Dialog", "Saturday"))
        item = self.project_hours.horizontalHeaderItem(7)
        item.setText(_translate("Dialog", "Sunday"))
        item = self.project_hours.horizontalHeaderItem(8)
        item.setText(_translate("Dialog", "Total"))
        self.label.setText(_translate("Dialog", "Client"))
        self.label_4.setText(_translate("Dialog", "Project"))
        self.label_5.setText(_translate("Dialog", "Task"))
        self.label_6.setText(_translate("Dialog", "Notes"))
        self.date_worked.setDisplayFormat(_translate("Dialog", "MM/dd/yyyy"))
        self.label_7.setText(_translate("Dialog", "Date Worked"))
        self.addTime.setText(_translate("Dialog", "Add time"))
        self.label_10.setText(_translate("Dialog", "Hours"))
        self.auth.setText(_translate("Dialog", "Authenticate"))
        self.label_2.setText(_translate("Dialog", "Password"))
        self.label_3.setText(_translate("Dialog", "Username"))
        self.getTime.setText(_translate("Dialog", "Get Time"))
        item = self.tableWidget.verticalHeaderItem(0)
        item.setText(_translate("Dialog", "Totals"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "Monday"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("Dialog", "Tuesday"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("Dialog", "Wednesday"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("Dialog", "Thursday"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("Dialog", "Friday"))
        item = self.tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("Dialog", "Saturday"))
        item = self.tableWidget.horizontalHeaderItem(6)
        item.setText(_translate("Dialog", "Sunday"))
        item = self.tableWidget.horizontalHeaderItem(7)
        item.setText(_translate("Dialog", "Weekly Total"))

    # Send authentication by clicking Authenticate. Pull up current week
    def authenticate(self):
        if self.username.text() != '' and self.password.text() != '':
            self.save_credentials()
            self.get_time()

        # Username or password missing
        else:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Please provide a username and password')
            error_dialog.setWindowTitle('Missing Credentials')
            error_dialog.exec_()

    # Add time for specified day
    def add_time(self):
        try:
            user = self.username.text()
            passw = self.password.text()
            user_id = self.get_user()
            team_member = self.get_team_member()
            if (self.hours.text() != '' and self.time_notes.toPlainText() != '' and str(
                    self.project.currentData()) != '' and str(self.task.currentData()) != '' and str(
                self.client.currentData()) != ''):
                headers = {"Content-Type": "application/json", "Accept": "application/json"}
                payload = json.dumps(
                    {'date_worked': str(self.date_worked.date().toPyDate()), 'hours': self.hours.text(),
                     'notes': self.time_notes.toPlainText(), 'client_project': self.project.currentData(),
                     'client': self.client.currentData(), 'project_task': self.task.currentData(), 'user': user_id,
                     'team_member': team_member})
                with requests.Session() as request_add_time:
                    request_add_time = requests.post(new_work_endpoint, auth=HTTPBasicAuth(user, passw),
                                                     headers=headers, data=payload)
                    self.get_time()
                    self.reset()
            else:
                self.require_fields()
                # print('Please enter all data')

        except:
            print('Add time failed: \n', sys.exc_info())

    # Get time for specified week
    def get_time(self):
        global all_projects
        global all_clients
        global all_tasks
        global get_projects
        if all_clients == '':
            all_clients = self.get_all_clients()
        if all_projects == '':
            all_projects = self.get_all_projects()
        if all_tasks == '':
            all_tasks = self.get_all_tasks()
        self.resolve_clients(all_clients)
        # clients_array = self.resolve_clients(projects_array)
        try:
            # global start_date
            task_time_fields = 'sysparm_fields=hours,team_member,project_task,date_worked,client_project,user,' \
                               'day_of_week '
            start_date = self.week.date().toPyDate()
            time_worked_endpoint = 'https://example.service-now.com/api/now/table' \
                                   '/x_scope_yare_project_task_time_worked?sysparm_query=team_member.team_member.user' \
                                   '.user_name=' + self.username.text() + '^work_week.week_start=' + str(
                start_date) + '&' + task_time_fields
            weekly_hours_endpoint = 'https://example.service-now.com/api/now/table/x_scope_yare_weekly_hours' \
                                    '?sysparm_query=team_member.user.user_name=' + self.username.text() + \
                                    '^week_start=' + str(
                start_date)
            user = self.username.text()
            passw = self.password.text()
            with requests.Session() as request_get_week:
                request_get_week = requests.get(time_worked_endpoint, auth=HTTPBasicAuth(user, passw))
                if (request_get_week.status_code == 200):
                    # Set week data
                    request_get_week_json = request_get_week.json()
                    results_obj = {}

                    # Loop through time entries for slected week
                    for result in request_get_week_json['result']:
                        # Add new SysID if it does not exist in the dictionary
                        if result['client_project']['value'] not in results_obj:
                            results_obj[result['client_project']['value']] = {}
                        # Add new key for day of week
                        if result['day_of_week'] in results_obj[result['client_project']['value']]:
                            result_hours = float(result['hours'])
                            obj_hours = float(
                                results_obj[result['client_project']['value']][result['day_of_week']]['hours'])
                            tot_hours = result_hours + obj_hours
                            results_obj[result['client_project']['value']][result['day_of_week']]['hours'] = tot_hours

                        else:
                            results_obj[result['client_project']['value']][result['day_of_week']] = result

                    # Loop through project sysIDs in object
                    self.project_hours.setRowCount(0)
                    for project in results_obj:
                        total_hours = []
                        day_number = 0
                        rowPosition = self.project_hours.rowCount()
                        self.project_hours.insertRow(rowPosition)
                        # Loop through day keys in the project - find day number for corresponding cell location
                        for day in results_obj[project]:
                            if day == 'monday':
                                day_number = 1
                            elif day == 'tuesday':
                                day_number = 2
                            elif day == 'wednesday':
                                day_number = 3
                            elif day == 'thursday':
                                day_number = 4
                            elif day == 'friday':
                                day_number = 5
                            elif day == 'saturday':
                                day_number = 6
                            elif day == 'sunday':
                                day_number = 7
                            # add number of hours to the total_hours array
                            total_hours.append(float(results_obj[project][day]['hours']))

                            # Set the value of the hours according to the day_number
                            self.project_hours.setItem(rowPosition, day_number, QtWidgets.QTableWidgetItem(
                                str(results_obj[project][day]['hours'])))
                            # Loop through projects to find project name
                            i = 0
                            project_cell = ''
                            while i < len(all_projects['result']):
                                if all_projects['result'][i]['sys_id'] == project:
                                    project_string = str(all_projects['result'][i]['name'])
                                    project_string = project_string.replace(': ', '\n')
                                    project_cell += project_string
                                    break
                                i += 1
                            # Loop through tasks to find task name
                            j = 0
                            while j < len(all_tasks['result']):
                                if all_tasks['result'][j]['project_id'] == project and all_tasks['result'][j][
                                    'sys_id'] == results_obj[project][day]['project_task']['value']:
                                    project_cell += '\n' + str(all_tasks['result'][j]['name'])
                                    break
                                j += 1
                            # Add project information to table
                            self.project_hours.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(project_cell))
                            self.project_hours.resizeRowToContents(rowPosition)
                            self.project_hours.resizeColumnToContents(0)

                        total_sum = sum(total_hours)
                        self.project_hours.setItem(self.project_hours.rowCount() - 1, 8,
                                                   QtWidgets.QTableWidgetItem(str(total_sum)))

                # Status code was not 200 for the GET request
                else:
                    print('Get week failed: ', request_get_week.status_code)

            with requests.Session() as request_weekly_hours:
                request_weekly_hours = requests.get(weekly_hours_endpoint, auth=HTTPBasicAuth(user, passw))
                if request_weekly_hours.status_code == 200:
                    weekly_hours_json = request_weekly_hours.json()
                    weekly_response = weekly_hours_json['result'][0]
                    self.tableWidget.setItem(0, 0, QtWidgets.QTableWidgetItem(weekly_response['monday']))
                    self.tableWidget.setItem(0, 1, QtWidgets.QTableWidgetItem(weekly_response['tuesday']))
                    self.tableWidget.setItem(0, 2, QtWidgets.QTableWidgetItem(weekly_response['wednesday']))
                    self.tableWidget.setItem(0, 3, QtWidgets.QTableWidgetItem(weekly_response['thursday']))
                    self.tableWidget.setItem(0, 4, QtWidgets.QTableWidgetItem(weekly_response['friday']))
                    self.tableWidget.setItem(0, 5, QtWidgets.QTableWidgetItem(weekly_response['saturday']))
                    self.tableWidget.setItem(0, 6, QtWidgets.QTableWidgetItem(weekly_response['sunday']))
                    self.tableWidget.setItem(0, 7, QtWidgets.QTableWidgetItem(weekly_response['total']))

                # Status code was not 200 for the GET request
                else:
                    print('Weekly hours failed: ', request_weekly_hours.status_code)

        except:
            print('Get request for week failed \n', sys.exc_info())

        # return clients_array

    def get_projects(self):
        try:
            user = self.username.text()
            passw = self.password.text()
            clients = []
            projects = []
            tasks = []
            with requests.Session() as request_get_projects:
                request_get_projects = requests.get(project_team_endpoint, auth=HTTPBasicAuth(user, passw))
                if request_get_projects.status_code == 200:
                    projects_json = request_get_projects.json()
                    i = 0
                    while i < len(projects_json['result']):
                        if projects_json['result'][i]['client_project']['value'] not in projects:
                            projects.append(projects_json['result'][i]['client_project']['value'])
                        if projects_json['result'][i]['client']['value'] not in clients:
                            clients.append(projects_json['result'][i]['client']['value'])
                        split_tasks = projects_json['result'][i]['project_tasks'].split(',')
                        for task in split_tasks:
                            if task not in tasks:
                                tasks.append(task)
                        i += 1
                    return projects_json
                else:
                    print('Get Projects failed ', request_get_projects.status_code)
        except:
            print('Get projects failed: \n', sys.exc_info())

    def resolve_clients(self, all_clients):
        global get_projects
        if get_projects == '':
            get_projects = self.get_projects()
        clients_list = get_projects
        clients = clients_list['result']
        i = 0
        while i < len(clients):
            # loop through all_clients with clients
            j = 0
            while j < len(all_clients['result']):
                if clients[i]['client']['value'] == all_clients['result'][j]['sys_id']:
                    # if not already in list
                    k = 0
                    duplicate = False
                    while k < self.client.count():
                        if self.client.itemData(k) == all_clients['result'][j]['sys_id']:
                            duplicate = True
                        k += 1
                    if not duplicate:
                        self.client.addItem(all_clients['result'][j]['client_name'], all_clients['result'][j]['sys_id'])
                        break
                j += 1
            i += 1

    def resolve_projects(self, all_projects):
        global get_projects
        if self.client.currentText() != '--Select Client--':
            self.project.clear()
            self.project.addItems(['--Select Project--'])
            if get_projects == '':
                get_projects = self.get_projects()
            projects = get_projects
            i = 0

            client = str(self.client.currentData())
            while i < len(projects['result']):
                current_client = projects['result'][i]['client']['value']
                current_project = projects['result'][i]['client_project']['value']
                if current_client == client:
                    j = 0
                    while j < len(all_projects['result']):
                        if all_projects['result'][j]['sys_id'] == current_project:
                            self.project.addItem(all_projects['result'][j]['project_name'],
                                                 all_projects['result'][j]['sys_id'])
                        j += 1
                i += 1

    def resolve_tasks(self, all_tasks):
        global get_projects
        if self.project.currentText() != '--Select Project--' and self.client.currentText() != '--Select Client--':
            self.task.clear()
            self.task.addItems(['--Select Task--'])
            if get_projects == '':
                get_projects = self.get_projects
            tasks = get_projects
            project = str(self.project.currentData())
            i = 0
            while i < len(tasks['result']):
                # current_client = tasks['result'][i]['client']['value']
                current_project = tasks['result'][i]['client_project']['value']
                if current_project == project:
                    j = 0
                    while j < len(all_tasks['result']):
                        if all_tasks['result'][j]['sys_id'] in tasks['result'][i]['project_tasks']:
                            self.task.addItem(all_tasks['result'][j]['name'], all_tasks['result'][j]['sys_id'])
                        j += 1
                i += 1

    def get_user(self):
        user = self.username.text()
        passw = self.password.text()
        get_user = requests.get(
            'https://example.service-now.com/api/now/table/sys_user?sysparm_query=user_name=javascript:gs.getUserName();',
            auth=HTTPBasicAuth(user, passw))
        if get_user.status_code == 200:
            get_user_json = get_user.json()
            return get_user_json['result'][0]['sys_id']
            # self.user.addItem(get_user_json['result'][0]['user_name'], get_user_json['result'][0]['sys_id'])

    def get_team_member(self):
        global get_projects
        if get_projects == '':
            get_projects = self.get_projects()
        user = self.username.text()
        passw = self.password.text()
        req_team_member = requests.get(
            'https://example.service-now.com/api/now/table/x_scope_yare_client_project_team?sysparm_query=team_member.user=javascript:gs.getUserID();^client_project=' + self.project.currentData() + '^client=' + self.client.currentData(),
            auth=HTTPBasicAuth(user, passw))

        if req_team_member.status_code == 200:
            team_member_json = req_team_member.json()
            print(team_member_json)
            return team_member_json['result'][0]['sys_id']

    def get_all_clients(self):
        try:
            user = self.username.text()
            passw = self.password.text()
            # returns client_name and sys_id
            req_all_clients = requests.get(
                'https://example.service-now.com/api/now/table/x_scope_yare_client?sysparm_query=active=true&sysparm_fields=client_name,sys_id',
                auth=HTTPBasicAuth(user, passw))
            if req_all_clients.status_code == 200:
                clients_json = req_all_clients.json()
                return clients_json
                # clients_obj = clients_json['result']
                # print(type(clients_obj))
        except:
            print('Get all clients failed: \n', sys.exc_info())

    def get_all_projects(self):
        try:
            user = self.username.text()
            passw = self.password.text()
            # returns project_name, name, sys_id, and client_id
            req_all_projects = requests.get(
                'https://example.service-now.com/api/now/table/x_scope_yare_client_project?sysparm_query=active=true&sysparm_fields=client,sys_id,name,project_name',
                auth=HTTPBasicAuth(user, passw))
            if req_all_projects.status_code == 200:
                projects_json = req_all_projects.json()
                i = 0
                while i < len(projects_json['result']):
                    # set client sys_id as new key
                    projects_json['result'][i]['client_id'] = projects_json['result'][i]['client']['value']
                    del (projects_json['result'][i]['client'])
                    i += 1

                return projects_json

        except:
            print('Get all projects failed: \n', sys.exc_info())

    def get_all_tasks(self):
        try:
            user = self.username.text()
            passw = self.password.text()
            # returns sys_id, name, client_id, and project_id
            req_all_tasks = requests.get(
                'https://example.service-now.com/api/now/table/x_scope_yare_client_project_task_type?sysparm_query=active=true&sysparm_fields=sys_id,name,client,project',
                auth=HTTPBasicAuth(user, passw))
            if req_all_tasks.status_code == 200:
                tasks_json = req_all_tasks.json()
                i = 0
                while i < len(tasks_json['result']):
                    # set client and project sys_ids as new key
                    tasks_json['result'][i]['client_id'] = tasks_json['result'][i]['client']['value']
                    del (tasks_json['result'][i]['client'])
                    tasks_json['result'][i]['project_id'] = tasks_json['result'][i]['project']['value']
                    del (tasks_json['result'][i]['project'])
                    i += 1
                return tasks_json
        except:
            print('Get all tasks failed: \n', sys.exc_info())

    def reset(self):
        # self.project.currentIndex(0)
        self.hours.clear()
        self.task.setCurrentIndex(0)
        self.time_notes.clear()

    def require_fields(self):
        error_dialog = QtWidgets.QErrorMessage()
        error_dialog.showMessage('Please provide all fields in the add time section')
        error_dialog.setWindowTitle('Add time error')
        error_dialog.exec_()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
