#######################################################################################################################
import io
import json
import os
import pathlib
import sys
from os import remove
from time import time
import time
import psycopg2
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from ping3 import ping
from qroundprogressbar import QRoundProgressBar
import pandas as pd
########################################################################################################################
class PIDS_Command_Controller_GUI(QMainWindow):
    def __init__(self,UserAccLevel):
        super(PIDS_Command_Controller_GUI, self).__init__()
        self.UserAccessLevel = UserAccLevel
        self.Variables()
        self.Window_Settings()
        self.Load_Csv()
        self.Widgets()

    def Variables(self):
        self.Table_Headers = ("Sentry", 'Jammer', "Camera","Time")
        self.rowcount = 0
        self.Tab_Show = False
        self.Server_Status = False
        self.ShowHealthlogFlag = False
        self.Sentry_ID_List = []
        self.Sentry_IP_List = []
        self.Camera_ID_List = []
        self.Camera_IP_List = []
        self.Jammer_ID_List = []
        self.Jammer_IP_List = []
        self.sentrybuttonlist = []
        self.camerabuttonlist = []
        self.jammerbuttonlist = []

    def Window_Settings(self):
        desktopWidget = QDesktopWidget()
        self.window_Width = desktopWidget.width()
        self.window_Height = desktopWidget.height()
        self.setWindowTitle("Command Control for Airbone Threats")
        self.resize(self.window_Width, self.window_Height)
        self.setWindowIcon(QIcon("Resources/Platinum.png"))
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)

    def Widgets(self):

        self.Image_Path = "Site_Info/Site_Map.jpg"
        self.Image_Label = QLabel(self)
        self.Image_Label.setGeometry(0,70,1920,1000)
        pixmap = QPixmap(self.Image_Path)
        self.Image_Label.setPixmap(pixmap)
        self.Image_Label.hide()

        self.sentrybuttonlist.clear()
        self.camerabuttonlist.clear()
        self.jammerbuttonlist.clear()

        for i in range(len(self.sentryconfigcsv)):
            sentrybutton = QPushButton(self)
            self.sentrybuttonlist.append(sentrybutton)
            self.sentrybuttonlist[i].setToolTip(str(self.sentryconfigcsv['description'].iloc[i]))
            self.sentrybuttonlist[i].setText(self.sentryconfigcsv['description'].iloc[i])
            self.sentrybuttonlist[i].setGeometry(
                QRect(self.sentryconfigcsv['pos_x'].iloc[i], self.sentryconfigcsv['pos_y'].iloc[i],
                      self.sentryconfigcsv['width'].iloc[i],
                      self.sentryconfigcsv['height'].iloc[i]))
            #self.sentrybuttonlist[i].setIcon(QIcon("Resources/Camera.png"))
            self.sentrybuttonlist[i].setIconSize(
                QSize(self.sentryconfigcsv["icon_width"].iloc[i], self.sentryconfigcsv["icon_height"].iloc[i]))
            self.sentrybuttonlist[i].setStyleSheet("background-color:rgba(255,255,255,0)")
            self.sentrybuttonlist[i].hide()
            self.sentrybuttonlist[i].setDisabled(True)

        for i in range(len(self.cameraconfigcsv)):
            camerabutton = QPushButton(self)
            self.camerabuttonlist.append(camerabutton)
            self.camerabuttonlist[i].setToolTip(str(self.cameraconfigcsv['description'].iloc[i]))
            #self.camerabuttonlist[i].setText(self.cameraconfigcsv['description'].iloc[i])
            self.camerabuttonlist[i].setGeometry(
                QRect(self.cameraconfigcsv['pos_x'].iloc[i], self.cameraconfigcsv['pos_y'].iloc[i],
                      self.cameraconfigcsv['width'].iloc[i],
                      self.cameraconfigcsv['height'].iloc[i]))
            self.camerabuttonlist[i].setIcon(QIcon("Resources/Camera.png"))
            self.camerabuttonlist[i].setIconSize(QSize(self.cameraconfigcsv["icon_width"].iloc[i],self.cameraconfigcsv["icon_height"].iloc[i]))
            self.camerabuttonlist[i].setStyleSheet("background-color:rgba(255,255,255,0)")
            self.camerabuttonlist[i].hide()
            self.camerabuttonlist[i].setDisabled(True)

        for i in range(len(self.jammerconfigcsv)):
            jammerbutton = QPushButton(self)
            self.jammerbuttonlist.append(jammerbutton)
            self.jammerbuttonlist[i].setToolTip(str(self.jammerconfigcsv['description'].iloc[i]))
            self.jammerbuttonlist[i].setText(self.jammerconfigcsv['description'].iloc[i])
            self.jammerbuttonlist[i].setGeometry(
                QRect(self.jammerconfigcsv['pos_x'].iloc[i], self.jammerconfigcsv['pos_y'].iloc[i],
                      self.jammerconfigcsv['width'].iloc[i],
                      self.jammerconfigcsv['height'].iloc[i]))
            #self.jammerbuttonlist[i].setIcon(QIcon("Resources/Camera.png"))
            self.jammerbuttonlist[i].setIconSize(
                QSize(self.jammerconfigcsv["icon_width"].iloc[i], self.jammerconfigcsv["icon_height"].iloc[i]))
            self.jammerbuttonlist[i].setStyleSheet("background-color:rgba(255,255,255,0)")
            self.jammerbuttonlist[i].hide()
            self.jammerbuttonlist[i].setDisabled(True)
            
        # Table Widget
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(self.rowcount)
        font = QFont()
        font.setPointSizeF(8.5)
        self.tableWidget.setFont(font)
        self.tableWidget.setColumnWidth(0, 80)
        self.tableWidget.setColumnWidth(1, 80)
        self.tableWidget.setColumnWidth(2, 80)
        self.tableWidget.setColumnWidth(3, 80)
        self.tableWidget.setColumnWidth(4, 100)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setHorizontalHeaderLabels(self.Table_Headers)
        self.tableWidget.resize(480, 650)
        self.tableWidget.move(5,70)
        self.tableWidget.hide()

        # ToolBar
        self.ToolBar = QToolBar(self)
        self.ToolBar.setGeometry(QRect(0, 18, self.window_Width, 50))
        self.ToolBar.setIconSize(QSize(65, 35))
        self.ToolBar.setStyleSheet("background-color:white;")
        self.ToolBar.setMovable(False)

        self.Clear_All_Events = QAction(self)
        self.Clear_All_Events.setText("Clear All Events")
        self.Clear_All_Events.setIcon(QIcon('Resources/Clear.png'))
        self.Clear_All_Events.triggered.connect(self.Clear)

        self.Start_Server = QAction(self)
        self.Start_Server.setText("Start Server")
        self.Start_Server.triggered.connect(self.StartServer)
        self.Start_Server.setIcon(QIcon('Resources/StartServer.png'))
        self.Start_Server.setShortcut("Shift+M")

        self.Stop_Server = QAction(self)
        self.Stop_Server.setText("Stop Server")
        self.Stop_Server.triggered.connect(self.StopServer)
        self.Stop_Server.setIcon(QIcon('Resources/StopServer.png'))
        self.Stop_Server.setShortcut("Shift+S")

        self.Table_Show = QAction(self)
        self.Table_Show.setIcon(QIcon('Resources/Table.png'))
        self.Table_Show.triggered.connect(self.Table_Visible)
        self.Table_Show.setToolTip("Event Table")

        self.Reports = QAction(self)
        self.Reports.setText("View Records")
        self.Reports.setShortcut("Shift+R")
        self.Reports.setIcon(QIcon('Resources/Reports.png'))
        self.Reports.triggered.connect(self.ShowReports)

        self.About = QAction(self)
        self.About.setText("Developer's Info")
        self.About.setIcon(QIcon('Resources/About.png'))
        self.About.triggered.connect(self.Developer)
        self.About.setShortcut("Shift+I")

        self.Ping_CheckerSentry = QAction("Sentry Health Check", self)
        self.Ping_CheckerSentry.triggered.connect(self.PerformSentryLinkCheck)
        self.Ping_CheckerSentry.setIcon(QIcon('Resources/Hub_Health_check.png'))

        self.Ping_CheckerJammer = QAction("Jammer Link Check", self)
        self.Ping_CheckerJammer.triggered.connect(self.PerformJammerLinkCheck)
        self.Ping_CheckerJammer.setIcon(QIcon('Resources/Light_Health_check.png'))

        self.ShowLogData = QAction(self)
        self.ShowLogData.setText("Show Log")
        self.ShowLogData.setIcon(QIcon('Resources/Log.png'))
        self.ShowLogData.triggered.connect(self.ShowHealthLog)

        self.ShowHubEventDataLog = QCheckBox(self)
        self.ShowHubEventDataLog.setText("Event")
        # self.HubEventDataLog.setIcon(QtGui.QIcon('Resources/Healthgreen.png'))
        self.ShowHubEventDataLog.clicked.connect(self.SensorEventDataUpdate)

        self.ShowHealthDataLog = QCheckBox(self)
        self.ShowHealthDataLog.setText("Health")
        self.ShowHealthDataLog.clicked.connect(self.SensorHealthDataUpdate)

        # self.ToolBar.addAction(self.Soft_Panel_Action)
        self.ToolBar.addAction(self.Table_Show)
        self.ToolBar.addAction(self.Clear_All_Events)
        self.ToolBar.addAction(self.Start_Server)
        self.ToolBar.addAction(self.Stop_Server)
        self.ToolBar.addSeparator()
        self.ToolBar.addSeparator()
        self.ToolBar.addAction(self.Reports)
        self.ToolBar.addSeparator()
        self.ToolBar.addSeparator()
        self.ToolBar.addAction(self.ShowLogData)
        self.ToolBar.addWidget(self.ShowHubEventDataLog)
        self.ToolBar.addWidget(self.ShowHealthDataLog)
        self.ToolBar.addSeparator()
        self.ToolBar.addSeparator()
        self.ToolBar.addAction(self.About)
        self.ToolBar.addSeparator()
        self.ToolBar.addSeparator()
        # self.ToolBar.addAction(self.CSI)

        self.Exit = QAction(self)
        self.Exit.setText("Exit")
        self.Exit.setIcon(QIcon('Resources/Close.png'))
        self.Exit.triggered.connect(self.Function_Exit)
        self.Exit.setShortcut("Esc")

        self.Sentry_Configuration_Details = QAction(self)
        self.Sentry_Configuration_Details.setText("Sentry Configuration Details")
        self.Sentry_Configuration_Details.setShortcut("Alt+S")
        self.Sentry_Configuration_Details.setIcon(QIcon('Resources/Hub_Health_Check.PNG'))
        self.Sentry_Configuration_Details.triggered.connect(self.Load_Sentry_Info)

        self.Jammer_Configuration_Details = QAction(self)
        self.Jammer_Configuration_Details.setText("Jammer Configuration Details")
        self.Jammer_Configuration_Details.setShortcut("Alt+J")
        self.Jammer_Configuration_Details.setIcon(QIcon('Resources/Light_Health_check.PNG'))
        self.Jammer_Configuration_Details.triggered.connect(self.Load_Jammer_Info)

        self.Camera_Configuration_Details = QAction(self)
        self.Camera_Configuration_Details.setText("Camera Configuration Details")
        self.Camera_Configuration_Details.setShortcut("Alt+C")
        self.Camera_Configuration_Details.setIcon(QIcon('Resources/Camera.png'))
        self.Camera_Configuration_Details.triggered.connect(self.Load_Camera_Info)

        self.Mapping_Configuration_Details = QAction(self)
        self.Mapping_Configuration_Details.setText("Jammer Mapping")
        self.Mapping_Configuration_Details.setShortcut("Alt+M")
        self.Mapping_Configuration_Details.setIcon(QIcon('Resources/Intrusion.png'))
        self.Mapping_Configuration_Details.triggered.connect(self.Load_Jammer_Mapping_Info)

        self.Clear_All_Events.setDisabled(True)
        self.Table_Show.setDisabled(True)
        self.Reports.setDisabled(True)
        self.Camera_Configuration_Details.setDisabled(True)
        self.Mapping_Configuration_Details.setDisabled(True)
        self.Stop_Server.setDisabled(True)
        self.Jammer_Configuration_Details.setDisabled(True)
        self.Sentry_Configuration_Details.setDisabled(True)

        # MenuBar
        self.menubar = self.menuBar()
        self.menubar.clear()
        LoadMapMenu = QMenu("Load Map", self)
        ConfigurationMenu = QMenu("Configuration", self)
        ReportsMenu = QMenu("Reports", self)
        AboutMenu = QMenu("About", self)
        QuitMenu = QMenu("Quit", self)


        QuitMenu.addAction(self.Exit)

        LoadMapMenu.addAction(self.Start_Server)

        AboutMenu.addAction(self.About)

        ConfigurationMenu.addAction(self.Camera_Configuration_Details)
        ConfigurationMenu.addAction(self.Jammer_Configuration_Details)
        ConfigurationMenu.addAction(self.Sentry_Configuration_Details)
        ConfigurationMenu.addAction(self.Mapping_Configuration_Details)

        ReportsMenu.addAction(self.Reports)

        # self.menubar.addMenu(SoftPanelMenu)
        self.menubar.addMenu(LoadMapMenu)
        self.menubar.addMenu(ConfigurationMenu)
        self.menubar.addMenu(ReportsMenu)
        # self.menubar.addMenu(HistoryMenu)
        self.menubar.addMenu(AboutMenu)
        #  self.menubar.addMenu(HelpMenu)
        self.menubar.addMenu(QuitMenu)

        # Buttons
        #self.Light_group_button = QButtonGroup()
        #self.Light_group_button.buttonClicked[int].connect(self.handleLightClickGroupButton)

        # QRound Progress Bar
        self.progress = QRoundProgressBar(self)
        self.progress.setGeometry(QRect(847, 400, 200, 200))
        font = QFont()
        font.setBold(True)
        self.progress.setFont(font)
        self.progress.setBarStyle(QRoundProgressBar.BarStyle.DONUT)
        palette = QPalette(QColor(255, 255, 255))
        brush = QBrush(QColor(100, 180, 0))
        # brush.setStyle(Qt.Dense3Pattern)
        # palette.setBrush(QPalette.Active, QPalette.Highlight, brush)

        palette.setBrush(QPalette().Background, Qt.transparent)
        self.progress.setPalette(palette)
        self.progress.hide()

        self.TextServer = QTextEdit(self)
        self.TextServer.setGeometry(QRect(1300, 80, 600,970))
        self.TextServer.setReadOnly(True)
        # self.TextServer.hide()

        palette.setBrush(QPalette().Background, Qt.transparent)
        # QButton Group
        self.Camera_Button_Group = QButtonGroup()
        #self.Camera_Button_Group.buttonClicked[int].connect(self.Call_Soft_Panel_Video_Popup)

        self.Light_Button_Group = QButtonGroup()

        self.label_Image = QLabel(self)
        with open('Site_Info/AppLogoConfig.json') as f:
            self.LogoCongig = json.load(f)

        self.X_axis = self.LogoCongig['AppLogo']["X_axis"]
        self.Y_axis = self.LogoCongig['AppLogo']["Y_axis"]
        self.Width = self.LogoCongig['AppLogo']["Width"]
        self.Height = self.LogoCongig['AppLogo']["Height"]
        self.label_Image.setGeometry(QRect(self.X_axis, self.Y_axis, self.Width, self.Height))
        self.pixmap = QPixmap('Resources/Platinum.png')
        self.label_Image.setPixmap(self.pixmap)

        self.show()
        # self.Connect_to_db()
        self.TextServer.hide()

    def Load_Csv(self):
        self.Sentry_IP_List.clear()
        self.Sentry_ID_List.clear()

        self.Camera_IP_List.clear()
        self.Camera_ID_List.clear()

        self.Jammer_IP_List.clear()
        self.Jammer_ID_List.clear()

        self.sentryconfigcsv = pd.read_csv("sentryconfiginfo.csv")
        for i in range(len(self.sentryconfigcsv)):
            self.Sentry_ID_List.append(self.sentryconfigcsv["description"].iloc[i])
            self.Sentry_IP_List.append(self.sentryconfigcsv["ipaddress"].iloc[i])

        self.cameraconfigcsv = pd.read_csv("cameraconfiginfo.csv")
        for i in range(len(self.cameraconfigcsv)):
            self.Camera_ID_List.append(self.cameraconfigcsv["description"].iloc[i])
            self.Camera_IP_List.append(self.cameraconfigcsv["ipaddress"].iloc[i])

        self.jammerconfigcsv = pd.read_csv("jammerconfiginfo.csv")
        for i in range(len(self.jammerconfigcsv)):
            self.Jammer_ID_List.append(self.jammerconfigcsv["description"].iloc[i])
            self.Jammer_IP_List.append(self.jammerconfigcsv["ipaddress"].iloc[i])

    def Clear(self):
        self.tableWidget.clear()
        self.tableWidget.setHorizontalHeaderLabels(self.Table_Headers)
        self.row = 0
        self.tableWidget.setRowCount(self.row)

    def StartServer(self):
        self.Server_Status = True
        self.About.setEnabled(False)
        self.Start_Server.setEnabled(False)
        self.Reports.setEnabled(False)
        self.Clear_All_Events.setEnabled(False)
        self.Table_Show.setEnabled(False)
        self.Stop_Server.setEnabled(False)
        self.Ping_CheckerSentry.setDisabled(True)
        self.Ping_CheckerJammer.setDisabled(True)
        for i in range(len(self.sentryconfigcsv)):
            self.sentrybuttonlist[i].setDisabled(True)

        for i in range(len(self.cameraconfigcsv)):
            self.camerabuttonlist[i].setDisabled(True)

        for i in range(len(self.jammerconfigcsv)):
            self.jammerbuttonlist[i].setDisabled(True)
        QApplication.overrideCursor()
        self.initProcess()
        self.progress.setFormat("Loading Map")
        self.progress.setValue(95)
        qApp.processEvents()
        self.About.setEnabled(True)
        self.Start_Server.setEnabled(False)
        self.Reports.setEnabled(True)
        self.Clear_All_Events.setEnabled(True)
        self.Table_Show.setEnabled(True)
        self.Sentry_Configuration_Details.setDisabled(False)
        self.Camera_Configuration_Details.setDisabled(False)
        self.Jammer_Configuration_Details.setDisabled(False)
        self.Mapping_Configuration_Details.setDisabled(False)
        self.Stop_Server.setEnabled(True)
        self.Ping_CheckerSentry.setDisabled(False)
        self.Ping_CheckerJammer.setDisabled(False)
        for i in range(len(self.sentryconfigcsv)):
            self.sentrybuttonlist[i].show()
            self.sentrybuttonlist[i].setDisabled(False)
        for i in range(len(self.cameraconfigcsv)):
            self.camerabuttonlist[i].show()
            self.camerabuttonlist[i].setDisabled(False)
        for i in range(len(self.jammerconfigcsv)):
            self.jammerbuttonlist[i].show()
            self.jammerbuttonlist[i].setDisabled(False)
        self.progress.setFormat("Start Capture")
        self.progress.setValue(100)
        qApp.processEvents()
        self.progress.hide()

    ####################################################################################################################
    def StopServer(self):
        self.Server_Status = False
        self.Stop_Server.setDisabled(True)
        self.Clear_All_Events.setDisabled(True)
        self.Table_Show.setDisabled(True)
        self.Reports.setDisabled(True)
        self.Sentry_Configuration_Details.setDisabled(True)
        self.Camera_Configuration_Details.setDisabled(True)
        self.Jammer_Configuration_Details.setDisabled(True)
        self.Mapping_Configuration_Details.setDisabled(True)
        self.Start_Server.setDisabled(False)
        self.Ping_CheckerSentry.setDisabled(True)
        self.Ping_CheckerJammer.setDisabled(True)
        for i in range(len(self.sentryconfigcsv)):
            self.sentrybuttonlist[i].setDisabled(True)
        for i in range(len(self.cameraconfigcsv)):
            self.camerabuttonlist[i].setDisabled(True)
        for i in range(len(self.jammerconfigcsv)):
            self.jammerbuttonlist[i].setDisabled(True)

    def initProcess(self):

        with open('Site_Info/AppLogoConfig.json') as f:
            self.LogoCongig = json.load(f)
        self.X_axis = self.LogoCongig['AppLogo']["X_axis"]
        self.Y_axis = self.LogoCongig['AppLogo']["Y_axis"]
        self.Width = self.LogoCongig['AppLogo']["Width"]
        self.Height = self.LogoCongig['AppLogo']["Height"]
        self.pixmap = QPixmap('Resources/AppLogo.png')
        self.label_Image.setPixmap(self.pixmap)
        self.label_Image.setGeometry(QRect(self.X_axis-400, self.Y_axis, self.Width, self.Height))

        self.progress.show()
        self.progress.setFormat("Preparing Site...")
        self.progress.setValue(10)
        qApp.processEvents()

        self.progress.show()
        self.progress.setFormat("Loading Jammer Config...")
        self.progress.setValue(40)
        qApp.processEvents()

        try:
            with open('Site_Info/TimingConstants.JSON') as f:
                TimingConstDict = json.load(f)
            self.FireEventBlockPeriod = TimingConstDict['FireEventBlock']
            self.MagEventBlockPeriod = TimingConstDict['MagEventBlock']
            self.VibEventBlockPeriod = TimingConstDict['VibEventBlock']
            self.PIREventBlockPeriod = TimingConstDict['PIREventBlock']
            self.CameraEventBlockPeriod = TimingConstDict['CameraBlock']
            self.CameraDWellPeriod = TimingConstDict['CameraDwell']
            self.EventFetchInerval = TimingConstDict['EventFetchInerval'] * 1000
            self.EventDeltaTime = TimingConstDict['EventDelta']
            self.LightDwellTime = TimingConstDict['LightDwellTime'] * 60
            self.TimetoClearEvents = TimingConstDict['TimetoClearEvents'] * 60 * 1000
        except:
            print('TimingConstants file missing')
            QMessageBox.critical(self, "TimingConstants File Missing?",
                                           f'''TimingConstants.JSON File is not found in\n {os.getcwd()}''')

        self.progress.show()
        self.progress.setFormat("Creating SentryServer...")
        self.progress.setValue(60)
        qApp.processEvents()


        self.X_axis = self.LogoCongig['AppLogoSmall']["X_axis"]
        self.Y_axis = self.LogoCongig['AppLogoSmall']["Y_axis"]
        self.Width = self.LogoCongig['AppLogoSmall']["Width"]
        self.Height = self.LogoCongig['AppLogoSmall']["Height"]
        self.pixmap = QPixmap('Resources/PlatinumSmall.png')
        self.label_Image.setPixmap(self.pixmap)
        self.label_Image.setGeometry(QRect(self.X_axis, self.Y_axis, self.Width, self.Height))

        self.Image_Label.show()


    def Table_Visible(self):
        if self.Tab_Show == False:
            self.tableWidget.show()
            self.Tab_Show = True
        else:
            self.tableWidget.hide()
            self.Tab_Show = False

    def ShowReports(self):
        pass

    def Developer(self):
        Dialog = QDialog()
        ui = Ui_Dialog()
        ui.setupUi(Dialog)
        Dialog.exec_()

    def PerformSentryLinkCheck(self):
        pass

    def PerformJammerLinkCheck(self):
        pass

    def SensorEventDataUpdate(self):
        pass

    def SensorHealthDataUpdate(self):
        pass

    def Function_Exit(self):
        msg = QMessageBox.question(self, "Exit", f'''Do you want to exit from {self.windowTitle()} Application''')
        if msg == QMessageBox.Yes:
            exit(0)

    def Load_Sentry_Info(self):
        self.Details = Sentry_Details()
        self.Details.tablewidgetSentry.setRowCount(len(self.Sentry_IP_List))
        if self.UserAccessLevel != 'Admin':
            self.Details.PB_Modify.hide()
            self.Details.lineEdit_SentryIP.hide()
        for i in range(len(self.Sentry_IP_List)):
            self.Details.tablewidgetSentry.setItem(i, 0, QTableWidgetItem(self.Sentry_ID_List[i]))
            self.Details.tablewidgetSentry.setItem(i, 1, QTableWidgetItem(self.Sentry_IP_List[i]))
        self.Details.exec_()

    def Load_Camera_Info(self):
        self.Details = Camera_Details()
        self.Details.tableWidget.setRowCount(len(self.Camera_IP_List))
        if self.UserAccessLevel != 'Admin':
            self.Details.PB_Modify.hide()
            self.Details.lineEdit_CamIP.hide()
        for i in range(len(self.Camera_IP_List)):
            self.Details.tableWidget.setItem(i, 0, QTableWidgetItem(self.Camera_ID_List[i]))
            self.Details.tableWidget.setItem(i, 1, QTableWidgetItem(self.Camera_IP_List[i]))
        self.Details.exec_()

    def Load_Jammer_Info(self):
        self.Details = Jammer_Details()
        self.Details.tablewidgetJammer.setRowCount(len(self.Jammer_IP_List))
        if self.UserAccessLevel != 'Admin':
            self.Details.PB_Modify.hide()
            self.Details.lineEdit_JammerIP.hide()
        for i in range(len(self.Jammer_IP_List)):
            self.Details.tablewidgetJammer.setItem(i, 0, QTableWidgetItem(self.Jammer_ID_List[i]))
            self.Details.tablewidgetJammer.setItem(i, 1, QTableWidgetItem(self.Jammer_IP_List[i]))
        self.Details.exec_()

    def Load_Jammer_Mapping_Info(self):
        pass

    def ShowHealthLog(self):
        if self.ShowHealthlogFlag == True:
            self.ShowHealthlogFlag = False
            self.TextServer.hide()
        else:
            self.ShowHealthlogFlag = True
            self.TextServer.show()


########################################################################################################################
class Sentry_Details(QDialog):
    def __init__(self):
        super(Sentry_Details, self).__init__()
        self.setWindowTitle("Sentry Configuration Details")
        self.setWindowIcon(QIcon("Resources/Platinum.png"))
        self.setFixedSize(600, 600)

        self.tablewidgetSentry = QTableWidget(self)
        self.tablewidgetSentry.setGeometry(QRect(10, 10, 580, 530))
        self.tablewidgetSentry.setColumnCount(6)
        self.tablewidgetSentry.setHorizontalHeaderLabels(('SENTRY ID', 'SENTRY IP'))
        font = QFont()
        font.setBold(True)
        font.setItalic(True)
        self.tablewidgetSentry.setFont(font)
        self.tablewidgetSentry.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablewidgetSentry.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablewidgetSentry.hideColumn(5)
        self.tablewidgetSentry.hideColumn(4)
        self.tablewidgetSentry.hideColumn(3)
        self.tablewidgetSentry.hideColumn(2)
        self.tablewidgetSentry.setSelectionMode(self.tablewidgetSentry.SingleSelection)

        self.lineEdit_SentryIP = QLineEdit(self)
        self.lineEdit_SentryIP.setGeometry(70, 550, 200, 30)
        self.lineEdit_SentryIP.setAlignment(Qt.AlignHCenter)
        self.lineEdit_SentryIP.setInputMask("000.000.000.000")

        self.PB_Modify = QPushButton('Modify', self)
        self.PB_Modify.setIcon(QIcon("Resources/modify.png"))
        self.PB_Modify.setGeometry(QRect(380, 550, 130, 31))
        self.PB_Modify.clicked.connect(self.Modify)

        self.tablewidgetSentry.cellClicked.connect(self.cell_was_clicked)

    def cell_was_clicked(self):
        self.row = self.tablewidgetSentry.currentRow()
        self.lineEdit_SentryIP.setText(self.tablewidgetSentry.item(self.row, 1).text())
        self.sentryid = self.tablewidgetSentry.item(self.row, 0).text()

    def Modify(self):
        self.tablewidgetSentry.setItem(self.row, 1, QTableWidgetItem(self.lineEdit_SentryIP.text()))
        '''
        try:
            connection = psycopg2.connect(
                user='postgres',
                password='Platinum0435#',
                host='localhost',
                database='hawkeye-pids',
                port=6543
            )
            print('***************  Connection Established  *****************')
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)
            QMessageBox.warning(self,'Warning!!!',f'failed to update {self.sentryid} ip address')
            return
        if connection:
            hubdb = ConfigHubDatabase(connection)
            print(self.lineEdit_SentryIP.text())
            status, msg = hubdb.UpdateHubIP(description=self.sentryid,ipaddress=self.lineEdit_SentryIP.text())
            QMessageBox.information(self,'Information!!!',msg)
            if status == True:
                self.tablewidgetSentry.setItem(self.row, 1, QTableWidgetItem(self.lineEdit_SentryIP.text()))
            connection.close()
        '''
    ####################################################################################################################
class Camera_Details(QDialog):
    def __init__(self):
        super(Camera_Details, self).__init__()
        self.setWindowTitle("Camera Configuration Details")
        self.setWindowIcon(QIcon("Resources/Platinum.png"))
        self.setFixedSize(600, 600)

        self.tableWidget = QTableWidget(self)
        self.tableWidget.setGeometry(QRect(10, 10, 580, 530))
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(("Camera ID", "Camera IP"))
        font = QFont()
        font.setBold(True)
        font.setItalic(True)
        self.tableWidget.setFont(font)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.hideColumn(5)
        self.tableWidget.hideColumn(4)
        self.tableWidget.hideColumn(3)
        self.tableWidget.hideColumn(2)
        self.tableWidget.setSelectionMode(self.tableWidget.SingleSelection)

        self.lineEdit_CamIP = QLineEdit(self)
        self.lineEdit_CamIP.setGeometry(70, 550, 200, 30)
        self.lineEdit_CamIP.setAlignment(Qt.AlignHCenter)
        self.lineEdit_CamIP.setInputMask("000.000.000.000")

        self.PB_Modify = QPushButton('Modify', self)
        self.PB_Modify.setIcon(QIcon("Resources/modify.png"))
        self.PB_Modify.setGeometry(QRect(380, 550, 130, 31))

        self.tableWidget.cellClicked.connect(self.cell_was_clicked)
        self.PB_Modify.clicked.connect(self.Modify)

    def cell_was_clicked(self):
        self.row = self.tableWidget.currentRow()
        self.lineEdit_CamIP.setText(self.tableWidget.item(self.row, 1).text())
        self.camid = self.tableWidget.item(self.row, 0).text()

    def Modify(self):
        self.tableWidget.setItem(self.row, 1, QTableWidgetItem(self.lineEdit_CamIP.text()))
        '''
        try:
            connection = psycopg2.connect(
                user='postgres',
                password='Platinum0435#',
                host='localhost',
                database='hawkeye-pids',
                port=6543
            )
            print('***************  Connection Established  *****************')
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)
            QMessageBox.warning(self,'Warning!!!',f'failed to update {self.camid} ip address')
            return
        if connection:
            camdb = ConfigCameraDatabase(connection)
            status, msg = camdb.UpdateCameraIP(description=self.camid,ipaddress=self.lineEdit_CamIP.text())
            QMessageBox.information(self,'Information!!!',msg)
            if status == True:
                self.tableWidget.setItem(self.row, 1, QTableWidgetItem(self.lineEdit_CamIP.text()))
            ConfigSensorDatabase(connection).UpdateCameraIP(camera_id=self.camid,ipaddress=self.lineEdit_CamIP.text())
            connection.close()
        '''
    ####################################################################################################################
class Jammer_Details(QDialog):
    def __init__(self):
        super(Jammer_Details, self).__init__()
        self.setWindowTitle("Jammer Configuration Details")
        self.setWindowIcon(QIcon("Resources/Platinum.png"))
        self.setFixedSize(600, 600)

        self.tablewidgetJammer = QTableWidget(self)
        self.tablewidgetJammer.setGeometry(QRect(10, 10, 580, 530))
        self.tablewidgetJammer.setColumnCount(6)
        self.tablewidgetJammer.setHorizontalHeaderLabels(('SENTRY ID', 'SENTRY IP'))
        font = QFont()
        font.setBold(True)
        font.setItalic(True)
        self.tablewidgetJammer.setFont(font)
        self.tablewidgetJammer.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tablewidgetJammer.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablewidgetJammer.hideColumn(5)
        self.tablewidgetJammer.hideColumn(4)
        self.tablewidgetJammer.hideColumn(3)
        self.tablewidgetJammer.hideColumn(2)
        self.tablewidgetJammer.setSelectionMode(self.tablewidgetJammer.SingleSelection)

        self.lineEdit_JammerIP = QLineEdit(self)
        self.lineEdit_JammerIP.setGeometry(70, 550, 200, 30)
        self.lineEdit_JammerIP.setAlignment(Qt.AlignHCenter)
        self.lineEdit_JammerIP.setInputMask("000.000.000.000")

        self.PB_Modify = QPushButton('Modify', self)
        self.PB_Modify.setIcon(QIcon("Resources/modify.png"))
        self.PB_Modify.setGeometry(QRect(380, 550, 130, 31))
        self.PB_Modify.clicked.connect(self.Modify)

        self.tablewidgetJammer.cellClicked.connect(self.cell_was_clicked)

    def cell_was_clicked(self):
        self.row = self.tablewidgetJammer.currentRow()
        self.lineEdit_JammerIP.setText(self.tablewidgetJammer.item(self.row, 1).text())
        self.jammerid = self.tablewidgetJammer.item(self.row, 0).text()

    def Modify(self):
        '''
        try:
            connection = psycopg2.connect(
                user='postgres',
                password='Platinum0435#',
                host='localhost',
                database='hawkeye-pids',
                port=6543
            )
            print('***************  Connection Established  *****************')
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)
            QMessageBox.warning(self,'Warning!!!',f'failed to update {self.jammerid} ip address')
            return
        if connection:
            hubdb = ConfigHubDatabase(connection)
            print(self.lineEdit_JammerIP.text())
            status, msg = hubdb.UpdateHubIP(description=self.jammerid,ipaddress=self.lineEdit_JammerIP.text())
            QMessageBox.information(self,'Information!!!',msg)
            if status == True:
                self.tablewidgetJammer.setItem(self.row, 1, QTableWidgetItem(self.lineEdit_JammerIP.text()))
            connection.close()
        '''
    ####################################################################################################################

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 200)
        Dialog.setWindowOpacity(1.0)
        Dialog.setWindowTitle("Developer's Info")
        Dialog.setWindowIcon(QIcon('Resources/PlatinumSmall.png'))

        Developer_Details = QLabel(Dialog)
        Developer_Details.setText('Developed by:\nI SQUARE SYSTEMS,\nHyderabad')
       # Developer_Details.setAlignment(QtCore.Qt.AlignCenter)
        Developer_Details.setGeometry(QRect(170,50,220,100))
        font = QFont()
        font.setFamily('Arial')
        #font.setItalic(True)
        font.setWeight(12)
        font.setPointSize(12)
        Developer_Details.setFont(font)

        self.label_Image = QLabel(Dialog)
        self.label_Image.setGeometry(20,-40,400,300)
        self.pixmap = QPixmap('Resources/PlatinumSmall.png')
        self.label_Image.setPixmap(self.pixmap)
    ####################################################################################################################
if __name__ == "__main__":
    App = QApplication(sys.argv)
    window = PIDS_Command_Controller_GUI('Admin')
    window.showMaximized()
    sys.exit(App.exec())
    ####################################################################################################################