import os.path
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QFileDialog
from Function import Part

# 在QApplication之前先实例化
uiLoader = QUiLoader()

class Main:

    def __init__(self):
        # 再加载界面
        self.ui = uiLoader.load('main.ui')
        self.ui.file_choose_button.clicked.connect(self.file_choose)
        self.ui.file_choose_text.setPlaceholderText('请点击右边的按钮选择你想要分卷的文件夹。注意:请在分卷前备份一份当前文件夹！')
        self.ui.excel_choose_button.clicked.connect(self.excel_choose)
        self.ui.excel_choose_text.setPlaceholderText('请点击右边的按钮选择你的表格文件,如果未选择，默认为当前目录下的excel文件。注意:请在分卷前备份一份当前文件夹！')
        self.ui.start_button.clicked.connect(self.start)

    def file_choose(self):
        self.file_path = QFileDialog.getExistingDirectory(self.ui, '选择文件夹', './')
        self.ui.file_choose_text.clear()
        self.ui.file_choose_text.setPlainText("已选择的文件夹路径为：\"{}\"，请确定文件夹路径无误。请确定文件路径无误。注意:请在分卷前备份一份当前文件夹！".format(self.file_path))
        if not self.file_path:
            self.ui.file_choose_text.clear()
            self.ui.file_choose_text.setPlainText("未成功选择文件夹路径，请重新选择。")
            return
        else:
            if os.path.exists(os.path.join(self.file_path,'卷内目录.xls')) or os.path.exists(os.path.join(self.file_path,'卷内目录.xlsx')):
                self.excel_path = os.path.join(self.file_path,'卷内目录.xls')
                self.ui.excel_choose_text.clear()
                self.ui.excel_choose_text.setPlainText("已选择的表格文件路径为：\"{}\"，请确定文件路径无误。注意:请在分卷前备份一份当前文件夹！".format(self.excel_path))
        return

    def excel_choose(self):
        self.excel_path, _  = QFileDialog.getOpenFileName(
        self.ui,             # 父窗口对象
        "清选择你的表格文件", # 标题
        r'./',        # 起始目录
        "Excel Files (*.xlsx *.xls *.csv);;All Files (*)"  # 选择类型
        )
        self.ui.excel_choose_text.clear()
        self.ui.excel_choose_text.setPlainText("已选择的表格文件路径为：\"{}\"，请确定文件路径无误。注意:请在分卷前备份一份当前文件！".format(
            self.excel_path))

    def start(self):
        self.part = Part(self.file_path,self.excel_path)
        self.part.make_dir()
        self.part.img_part()
        QMessageBox.information(self.ui, '提示', '处理完成！')
        errno_list = self.part.errno_return()
        self.ui.errno_return_text.clear()
        if errno_list:
            for errno_text in errno_list:
                self.ui.errno_return_text.setPlainText(errno_list.__str__())
            QMessageBox.information(self.ui, '提示', '发现错误!')
        else:
            self.ui.errno_return_text.setPlainText("此组数据处理完成!")


app = QApplication([])
main = Main()
main.ui.show()
app.exec()