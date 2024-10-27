import os.path
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import QStringListModel
from fileControl import FileBunding

# 在QApplication之前先实例化
uiLoader = QUiLoader()

class Main:

    def __init__(self):
        # 再加载界面
        self.ui = uiLoader.load('main.ui')
        self.ui.file_choose_button.clicked.connect(self.file_choose)
        self.ui.excel_choose_button.clicked.connect(self.excel_choose)
        self.ui.start_button.clicked.connect(self.start)
        self.ui.start_button.setEnabled(False)
        self.error_model = QStringListModel()
        self.ui.error_listView.setModel(self.error_model)
        self.error_model.setStringList([])


    def file_choose(self):
        self.file_path = QFileDialog.getExistingDirectory(self.ui, '选择文件夹', './')
        self.ui.file_choose_line.clear()
        self.ui.file_choose_line.setText(self.file_path)
        if not self.file_path:
            self.ui.file_choose_line.clear()
            self.ui.file_choose_line.setText("未成功选择文件夹路径，请重新选择。")
        if self.file_path and self.excel_path:
            self.ui.start_button.setEnabled(True)
        return

    def excel_choose(self):
        self.excel_path, _  = QFileDialog.getOpenFileName(
            self.ui,             # 父窗口对象
            "清选择你的卷内目录文件", # 标题
            r'./',        # 起始目录
            "Excel Files (*.xlsx *.xls *.csv);;All Files (*)"  # 选择类型
        )
        self.ui.excel_choose_line.clear()
        self.ui.excel_choose_line.setText(self.excel_path)
        if not self.excel_path:
            self.ui.excel_choose_line.clear()
            self.ui.excel_choose_line.setText("未成功选择卷内目录路径，请重新选择。")
        if self.file_path and self.excel_path:
            self.ui.start_button.setEnabled(True)
        return

    def start(self):
        is_excel_right = True
        try:
            self.fb = FileBunding(fileDir=self.file_path,excelDir=self.excel_path)
            is_excel_right = self.fb.checkExcel()
        except:
            self.error_model.setStringList(["检查案卷目录表格出现错误，请检查案卷目录文件是否关闭或授予管理员权限!"])
        if is_excel_right:
            self.fb.movImage()
            self.fb.checkExcel()
            QMessageBox.information(self.ui, '提示', '处理完成！')
        errno_list = self.fb.returnErr()


        if errno_list:
            with open(os.path.join(self.file_path, '错误信息.log'), 'w') as f:
                for i, errno_text in enumerate(errno_list, start=1):
                    f.write(f"{i}. {errno_text}\n")
                    self.error_model.insertRows(self.error_model.rowCount(), 1)
                    index = self.error_model.index(self.error_model.rowCount() - 1)
                    self.error_model.setData(index, errno_text)

            QMessageBox.information(self.ui, '提示', f'共发现{len(errno_list)}条错误！请进一步查看本路径下的错误日志来查看错误信息。')
        else:
            self.error_model.setStringList(["此组数据处理完成!"])


app = QApplication([])
main = Main()
main.ui.show()
app.exec()