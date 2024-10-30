import os.path,sys
from PySide6.QtWidgets import *
from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import QStringListModel,Qt
from fileControl import FileMoveProcessingThread,PDFMoveProcessingThread
from main_ui import Ui_ClassForm

class Main(QWidget):

    def __init__(self,parent = None):
        super().__init__(parent)
        self.ui = Ui_ClassForm()
        self.ui.setupUi(self)

        self.ui.file_choose_button.clicked.connect(self.file_choose)    # 选择文件按钮
        self.ui.excel_choose_button.clicked.connect(self.excel_choose)  # 选择excel路径
        self.ui.start_button.clicked.connect(self.start_task_file)           # 开启任务线程

        self.error_model = QStringListModel()
        self.ui.error_listView.setModel(self.error_model)               # 设置列表模型
        self.error_model.setStringList([])
        #self.ui.pushButton_stop.clicked.connect(self.start_task_pdf)        # 按钮绑定停止处理任务

        self.ui.progressBar.setMinimum(0)                               # 设置进度条样式
        self.ui.progressBar.setMaximum(100)
        self.ui.progressBar.setStyleSheet('''
            QProgressBar {
                border: 2px solid #000;
                text-align:center;
                background:#aaa;
                color:#fff;
                height: 15px;
                border-radius: 8px;
                width:150px;
            }
            QProgressBar::chunk {
                background: #333;
                width:1px;
            }
        ''')


        self.file_path = ""
        self.excel_path = ""

        self.task_thread1 = None                                         # 初始化线程

    def file_choose(self):
        self.file_path = QFileDialog.getExistingDirectory(self, '选择文件夹')
        self.ui.file_choose_line.clear()
        self.ui.file_choose_line.setText(self.file_path)
        if not self.file_path:
            self.ui.file_choose_line.clear()
            self.ui.file_choose_line.setText("未成功选择文件夹路径，请重新选择。")

    def excel_choose(self):
        self.excel_path, _  = QFileDialog.getOpenFileName(
            self,             # 父窗口对象
            "清选择你的卷内目录文件", # 标题
            "",        # 起始目录
            "Excel Files (*.xlsx *.xls *.csv);;All Files (*)"  # 选择类型
        )
        self.ui.excel_choose_line.clear()
        self.ui.excel_choose_line.setText(self.excel_path)
        if not self.excel_path:
            self.ui.excel_choose_line.clear()
            self.ui.excel_choose_line.setText("未成功选择卷内目录路径，请重新选择。")
    def start_task_pdf(self):
        if self.file_path != "" and self.excel_path != "":
            self.task_thread2 = PDFMoveProcessingThread(self,fileDir=self.file_path,excelDir=self.excel_path)
            self.task_thread2.progress.connect(self.update_progress)                     # 更新进度条信号
            self.task_thread2.error_signal.connect(self.handle_error)                    # 异常处理信号
            self.task_thread2.result_signal.connect(self.handle_results)                 # 处理完成信号
            self.task_thread2.start()                                                    # 启动线程
    def start_task_file(self):
        if self.file_path != "" and self.excel_path != "":
            self.task_thread1 = FileMoveProcessingThread(self,fileDir=self.file_path,excelDir=self.excel_path)
            self.task_thread1.progress.connect(self.update_progress)                     # 更新进度条信号
            self.task_thread1.error_signal.connect(self.handle_error)                    # 异常处理信号
            self.task_thread1.result_signal.connect(self.handle_results)                 # 处理完成信号
            self.task_thread1.start()# 启动线程
            self.task_thread1.result_signal.connect(self.start_task_pdf)


    def update_progress(self, value):
        # 更新进度条和标签
        self.ui.progressBar.setValue(value)
       
    def stop_processing(self):
        i = self.task_thread1.isRunning()
        if self.task_thread1 is not None and self.task_thread1.isRunning():
            self.task_thread1.requestInterruption()  # 调用线程的 stop 方法停止线程
            self.ui.progressBar.setValue(0)

    def handle_error(self, error_message):
        # 显示错误信息并停止线程
        if self.task_thread1:
            self.stop_processing()  # 确保线程在错误时停止
            with open(os.path.join(self.file_path, '错误信息.log'), 'w') as f:
                for i, errno_text in enumerate(error_message, start=1):
                    f.write(f"{i}. {errno_text}\n")
                    self.error_model.insertRows(self.error_model.rowCount(), 1)
                    index = self.error_model.index(self.error_model.rowCount() - 1)
                    self.error_model.setData(index, errno_text)
            self.task_thread1 = None
            QMessageBox.information(self, '提示', f'共发现{len(error_message)}条错误！请进一步查看本路径下的错误日志来查看错误信息。')
    
    def handle_results(self, results):
    # 处理任务完成后返回的结果
        if results:
            with open(os.path.join(self.file_path, '错误信息.log'), 'w') as f:
                for i, errno_text in enumerate(results, start=1):
                    f.write(f"{i}. {errno_text}\n")
                    self.error_model.insertRows(self.error_model.rowCount(), 1)
                    index = self.error_model.index(self.error_model.rowCount() - 1)
                    self.error_model.setData(index, errno_text)

            QMessageBox.information(self, '提示', f'共发现{len(results)}条错误！请进一步查看本路径下的错误日志来查看错误信息。')
        else:
            self.error_model.setStringList(["此组数据处理完成!"])
        self.task_thread1 = None  # 清除线程引用

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Main()
    win.show()
    app.exit(app.exec())
