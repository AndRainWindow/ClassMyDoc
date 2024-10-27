import os.path,sys
from PySide6.QtWidgets import *
from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import QStringListModel,Qt
from fileControl import FileProcessingThread
from main_ui import Ui_ClassForm

class Main(QWidget):

    def __init__(self,parent = None):
        # 再加载界面
        super().__init__(parent)
        self.ui = Ui_ClassForm()
        self.ui.setupUi(self)
        self.ui.file_choose_button.clicked.connect(self.file_choose)
        self.ui.excel_choose_button.clicked.connect(self.excel_choose)
        self.ui.start_button.clicked.connect(self.start_task)
        # self.ui.start_button.setEnabled(False)
        self.error_model = QStringListModel()
        self.ui.error_listView.setModel(self.error_model)
        self.error_model.setStringList([])
        self.ui.pushButton.clicked.connect(self.stop_processing)

        self.ui.progressBar.setMinimum(0)
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

        self.ui.verticalLayout.addWidget(self.ui.progressBar)

        self.file_path = ""
        self.excel_path = ""

        self.task_thread = None

    def file_choose(self):
        self.file_path = QFileDialog.getExistingDirectory(self, '选择文件夹')
        self.ui.file_choose_line.clear()
        self.ui.file_choose_line.setText(self.file_path)
        if not self.file_path:
            self.ui.file_choose_line.clear()
            self.ui.file_choose_line.setText("未成功选择文件夹路径，请重新选择。")
        # if self.file_path and self.excel_path:
        #     self.ui.start_button.setEnabled(True)
        # return

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
        # if self.file_path and self.excel_path:
        #     self.ui.start_button.setEnabled(True)
        # return

    def start_task(self):
        if self.file_path != "" and self.excel_path != "":
            self.task_thread = FileProcessingThread(fileDir=self.file_path,excelDir=self.excel_path)
            self.task_thread.progress.connect(self.update_progress)
            self.task_thread.error_signal.connect(self.handle_error)
            self.task_thread.result_signal.connect(self.handle_results)
            self.task_thread.start()
            # self.error_model.setStringList(["此组数据处理完成!"])
            
    def update_progress(self, value):
        # 更新进度条和标签
        self.ui.progressBar.setValue(value)
       
    def stop_processing(self):
        if self.task_thread and self.task_thread.isRunning():
            self.task_thread.stop()  # 调用线程的 stop 方法停止线程

    def handle_error(self, error_message):
        # 显示错误信息并停止线程
        # self.progress_label.setText(f"错误：{error_message}")
        if self.task_thread:
            self.stop_processing()  # 确保线程在错误时停止
            with open(os.path.join(self.file_path, '错误信息.log'), 'w') as f:
                for i, errno_text in enumerate(error_message, start=1):
                    f.write(f"{i}. {errno_text}\n")
                    self.error_model.insertRows(self.error_model.rowCount(), 1)
                    index = self.error_model.index(self.error_model.rowCount() - 1)
                    self.error_model.setData(index, errno_text)
            self.task_thread = None
            QMessageBox.information(self.ui, '提示', f'共发现{len(error_message)}条错误！请进一步查看本路径下的错误日志来查看错误信息。')
    
    def handle_results(self, results):
    # 处理任务完成后返回的结果
        if results:
            with open(os.path.join(self.file_path, '错误信息.log'), 'w') as f:
                for i, errno_text in enumerate(results, start=1):
                    f.write(f"{i}. {errno_text}\n")
                    self.error_model.insertRows(self.error_model.rowCount(), 1)
                    index = self.error_model.index(self.error_model.rowCount() - 1)
                    self.error_model.setData(index, errno_text)

            QMessageBox.information(self.ui, '提示', f'共发现{len(results)}条错误！请进一步查看本路径下的错误日志来查看错误信息。')
        else:
            self.error_model.setStringList(["此组数据处理完成!"])
        self.task_thread = None  # 清除线程引用

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Main()
    win.show()
    app.exit(app.exec())
