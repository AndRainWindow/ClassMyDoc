import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PySide6.QtCore import QThread, Signal
import pandas as pd
import shutil

class FileProcessingThread(QThread):
    progress = Signal(int)
    error_signal = Signal(list)
    result_signal = Signal(list)
    def __init__(self, excelDir, fileDir):
        super().__init__()
        self.fileDir = fileDir
        if os.path.exists(excelDir):
            self.dpFileInternal = pd.read_excel(excelDir)
        else:
            self.dpFileInternal = None
        self.listErr = []   # 错误信息列表
        self.movedImgList = []

    def checkExcel(self):
        '''
        检查卷内Excel表中是否有错误
        '''
        is_excel_right = True
        if self.dpFileInternal.empty:
            self.listErr.append('Excel文件为空，请检查。')
        else:
            self.fileID_list = self.dpFileInternal.groupby("案卷级档号")
            self.fileID_list = self.fileID_list.size().index  # 获取案卷批号
            fileID_index = [int(fileID.split('-')[-1]) for fileID in self.fileID_list]
            for fileID_index_index in range(1, len(fileID_index)):
                if fileID_index[fileID_index_index] - fileID_index[fileID_index_index-1] != 1:
                    self.listErr.append(f'{self.fileID_list[fileID_index_index]}案卷级档号不连续。')
            total_files =  len(self.fileID_list)       
            for i,fileID in enumerate(self.fileID_list):

                progress_percentage = round(((i+1) / total_files) * 10)  # 设置进度
                self.progress.emit(progress_percentage)

                dpFilter = self.dpFileInternal['案卷级档号'].isin([fileID]) # 筛选每一行
                dpSingleFile = self.dpFileInternal[dpFilter]
                
                FileNum = dpSingleFile.shape[0]  # 获取分卷数量

                page = 0    # 张页号
                pageNumber = 1 # 文件页数

                for i, (_, row) in enumerate(dpSingleFile.iterrows()):    # 循环一个分卷任务
                    pastFileID = fileID + '-' + str(i+1).rjust(5, '0') # 案卷级档号
                    serialNumber = i + 1   # 顺序号
                    cpage = page + pageNumber #张页号+文件页数（初始值为0+1）
                    pageNumber = row.loc['文件页数']
                    if i + 1 == FileNum :   # 判断是否为最后一行
                        page = row.loc['张页号']
                        page1 = int(page.split('-')[0])
                        page2 = int(page.split('-')[1])
                        if page2 - page1 + 1 != pageNumber:
                            self.listErr.append(f'{pastFileID}张页号或文件页数匹配错误。')
                            break
                    else:
                        page = int(row.loc['张页号'])
                        if pastFileID != row.loc['文件级档号']:
                            self.listErr.append(f'{pastFileID}文件级档号匹配错误或不存在。')
                            break
                        elif serialNumber != row.loc['顺序号']:
                            self.listErr.append(f'{pastFileID}顺序号匹配错误。')
                            break
                        elif cpage != page :
                            self.listErr.append(f'{pastFileID}张页号或文件页数匹配错误。')
                            break
        if self.listErr:
            is_excel_right = False
        return is_excel_right

    def movImage(self):
        total_files = len(self.fileID_list)
        for i,fileID in enumerate(self.fileID_list):

            progress_percentage = round(((i+1) / total_files) * 80) + 20  # 设置进度
            self.progress.emit(progress_percentage)
            
            dpFilter = self.dpFileInternal['案卷级档号'].isin([fileID])
            dpSingleFile = self.dpFileInternal[dpFilter]
            external_picture_count = 1
            for i, (_, row) in enumerate(dpSingleFile.iterrows()):
                fileExternal_name = row.loc['案卷级档号']
                fileInternal_name = row.loc['文件级档号']
                InternalDir_path = os.path.join(self.fileDir, fileExternal_name,fileInternal_name)
                if not os.path.exists(InternalDir_path):
                    os.makedirs(InternalDir_path)
                file_page = row.loc['张页号']
                file_count = row.loc['文件页数']
                is_last_file = False

                if '-' in file_page:
                    file_page = int(file_page.split('-')[0])
                    is_last_file = True
                while (int(external_picture_count) <= int(file_page) + int(file_count) - 1):
                    jpg_name = str(external_picture_count).rjust(3, '0') + '.jpg'
                    path = os.path.join(self.fileDir, fileExternal_name, jpg_name)
                    npath = os.path.join(self.fileDir, fileExternal_name, fileInternal_name, jpg_name)

                    try:
                        shutil.move(path, npath)
                    except:
                        self.listErr.append(f'{fileExternal_name}文件夹下的{jpg_name}不存在,请检查。')
                    external_picture_count += 1

                PDFname = fileInternal_name + '.pdf'
                fileInternalpath = os.path.join(self.fileDir, fileExternal_name, fileInternal_name)
                
                nPDFpath = os.path.join(os.path.dirname(self.fileDir),'PDF', fileExternal_name)
                self.generatePDF(fileInternalpath,nPDFpath,PDFname)

                if is_last_file:
                    continue
    
    def check_jpg(self):
        for fileID in self.fileID_list:
            dpFilter = self.dpFileInternal['案卷级档号'].isin([fileID])
            dpSingleFile = self.dpFileInternal[dpFilter]
            file_now_list = os.listdir(os.path.join(self.fileDir, fileID))
            jpg_files = [file for file in file_now_list if file.endswith('.jpg')]
            if jpg_files:
                self.listErr.append(f'{fileID}文件夹下有多余图片。')
            for i, (_, row) in enumerate(dpSingleFile.iterrows()):
                fileExternal_name = row.loc['案卷级档号']
                fileInternal_name = row.loc['文件级档号']
                jpg_files_should = row.loc['文件页数']
                file_now_list = os.listdir(os.path.join(self.fileDir, fileExternal_name, fileInternal_name))
                jpg_files = [file for file in file_now_list if file.endswith('.jpg')]
                if not len(jpg_files) == jpg_files_should:
                    self.listErr.append(f'{fileExternal_name}文件夹下的{fileInternal_name}文件夹下的图片数量错误。')

    def returnErr(self):
        return self.listErr

    def generatePDF(self,fileInternalpath,nPDFpath,pdfname):
        if os.path.exists(nPDFpath):
            pass
        else:
           os.makedirs(nPDFpath)
        self.jpg2pdf(fileInternalpath,os.path.join(nPDFpath,pdfname))

    def jpg2pdf(self,image_folder,output_pdf):
          # 获取文件夹下所有图片文件
        image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif'))]
        image_files.sort()  # 按顺序排列文件

        if not image_files:
            print("没有找到任何图片文件。")
            return

        c = None  # Canvas 对象的初始化为空
        for image_file in image_files:
            img_path = os.path.join(image_folder, image_file)
            img = Image.open(img_path)
            
            # 获取图片的原始尺寸
            pdf_width, pdf_height = img.size

            # 如果没有初始化Canvas对象，则使用第一张图片的大小进行初始化
            if c is None:
                c = canvas.Canvas(output_pdf)

            # 设置页面大小并添加图片
            c.setPageSize((pdf_width, pdf_height))
            c.drawImage(img_path, 0, 0, pdf_width, pdf_height)

            # 添加透明文字层
            c.setFont("Helvetica", 12)
            c.setFillColorRGB(1, 1, 1, alpha=0)  # 透明文字颜色
            c.drawString(10, 10, "")  # 空字符串，后续可替换为实际内容

            # 完成当前页面，准备下一页
            c.showPage()
        
        # 保存PDF文件
        c.save()
        print(f"PDF文件已成功保存为 {output_pdf}")

    def start(self):
        is_excel_right = True
        try:
            is_excel_right = self.checkExcel()  
        except:
            self.listErr.append("检查案卷目录表格出现错误，请检查案卷目录文件是否关闭或授予管理员权限!")
            is_excel_right = False

        if is_excel_right:  
            self.movImage()
            self.check_jpg()
        
            self.result_signal.emit(self.listErr)
            self.quit()
        else:
            self.error_signal.emit(self.listErr)

    def stop(self):
        self._is_running = False       

class FileBunding():
    def __init__(self,excelDir, fileDir) -> None:
        self.fileDir = fileDir
        if os.path.exists(excelDir):
            self.dpFileInternal = pd.read_excel(excelDir)
        else:
            self.dpFileInternal = None
        self.listErr = []   # 错误信息列表
        self.movedImgList = []


    def checkExcel(self):
        '''
        检查卷内Excel表中是否有错误
        '''
        is_excel_right = True
        if self.dpFileInternal.empty:
            self.listErr.append('Excel文件为空，请检查。')
        else:
            self.fileID_list = self.dpFileInternal.groupby("案卷级档号")
            self.fileID_list = self.fileID_list.size().index  # 获取案卷批号
            fileID_index = [int(fileID.split('-')[-1]) for fileID in self.fileID_list]
            for fileID_index_index in range(1, len(fileID_index)):
                if fileID_index[fileID_index_index] - fileID_index[fileID_index_index-1] != 1:
                    self.listErr.append(f'{self.fileID_list[fileID_index_index]}案卷级档号不连续。')
            for fileID in self.fileID_list:

                dpFilter = self.dpFileInternal['案卷级档号'].isin([fileID]) # 筛选每一行
                dpSingleFile = self.dpFileInternal[dpFilter]
                
                FileNum = dpSingleFile.shape[0]  # 获取分卷数量

                page = 0    # 张页号
                pageNumber = 1 # 文件页数

                for i, (_, row) in enumerate(dpSingleFile.iterrows()):    # 循环一个分卷任务
                    pastFileID = fileID + '-' + str(i+1).rjust(5, '0') # 案卷级档号
                    serialNumber = i + 1   # 顺序号
                    cpage = page + pageNumber #张页号+文件页数（初始值为0+1）
                    pageNumber = row.loc['文件页数']
                    if i + 1 == FileNum :   # 判断是否为最后一行
                        page = row.loc['张页号']
                        page1 = int(page.split('-')[0])
                        page2 = int(page.split('-')[1])
                        if page2 - page1 + 1 != pageNumber:
                            self.listErr.append(f'{pastFileID}张页号或文件页数匹配错误。')
                            break
                    else:
                        page = int(row.loc['张页号'])
                        if pastFileID != row.loc['文件级档号']:
                            self.listErr.append(f'{pastFileID}文件级档号匹配错误或不存在。')
                            break
                        elif serialNumber != row.loc['顺序号']:
                            self.listErr.append(f'{pastFileID}顺序号匹配错误。')
                            break
                        elif cpage != page :
                            self.listErr.append(f'{pastFileID}张页号或文件页数匹配错误。')
                            break
        if self.listErr:
            is_excel_right = False
        return is_excel_right

    def movImage(self):
        for fileID in self.fileID_list:
            dpFilter = self.dpFileInternal['案卷级档号'].isin([fileID])
            dpSingleFile = self.dpFileInternal[dpFilter]
            external_picture_count = 1
            for i, (_, row) in enumerate(dpSingleFile.iterrows()):
                fileExternal_name = row.loc['案卷级档号']
                fileInternal_name = row.loc['文件级档号']
                InternalDir_path = os.path.join(self.fileDir, fileExternal_name,fileInternal_name)
                if not os.path.exists(InternalDir_path):
                    os.makedirs(InternalDir_path)
                file_page = row.loc['张页号']
                file_count = row.loc['文件页数']
                is_last_file = False

                
                
                if '-' in file_page:
                    file_page = int(file_page.split('-')[0])
                    is_last_file = True
                while (int(external_picture_count) <= int(file_page) + int(file_count) - 1):
                    jpg_name = str(external_picture_count).rjust(3, '0') + '.jpg'
                    path = os.path.join(self.fileDir, fileExternal_name, jpg_name)
                    npath = os.path.join(self.fileDir, fileExternal_name, fileInternal_name, jpg_name)

                    try:
                        shutil.move(path, npath)
                    except:
                        self.listErr.append(f'{fileExternal_name}文件夹下的{jpg_name}不存在,请检查。')
                    external_picture_count += 1

                PDFname = fileInternal_name + '.pdf'
                fileInternalpath = os.path.join(self.fileDir, fileExternal_name, fileInternal_name)
                
                nPDFpath = os.path.join(os.path.dirname(self.fileDir),'PDF', fileExternal_name)
                self.generatePDF(fileInternalpath,nPDFpath,PDFname)

                if is_last_file:
                    continue
    
    def check_jpg(self):
        for fileID in self.fileID_list:
            dpFilter = self.dpFileInternal['案卷级档号'].isin([fileID])
            dpSingleFile = self.dpFileInternal[dpFilter]
            file_now_list = os.listdir(os.path.join(self.fileDir, fileID))
            jpg_files = [file for file in file_now_list if file.endswith('.jpg')]
            if jpg_files:
                self.listErr.append(f'{fileID}文件夹下有多余图片。')
            for i, (_, row) in enumerate(dpSingleFile.iterrows()):
                fileExternal_name = row.loc['案卷级档号']
                fileInternal_name = row.loc['文件级档号']
                jpg_files_should = row.loc['文件页数']
                file_now_list = os.listdir(os.path.join(self.fileDir, fileExternal_name, fileInternal_name))
                jpg_files = [file for file in file_now_list if file.endswith('.jpg')]
                if not len(jpg_files) == jpg_files_should:
                    self.listErr.append(f'{fileExternal_name}文件夹下的{fileInternal_name}文件夹下的图片数量错误。')

    def returnErr(self):
        return self.listErr

    def generatePDF(self,fileInternalpath,nPDFpath,pdfname):
        if os.path.exists(nPDFpath):
            pass
        else:
           os.makedirs(nPDFpath)
        self.jpg2pdf(fileInternalpath,os.path.join(nPDFpath,pdfname))


    def jpg2pdf(self,image_folder,output_pdf):
          # 获取文件夹下所有图片文件
        image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif'))]
        image_files.sort()  # 按顺序排列文件

        if not image_files:
            print("没有找到任何图片文件。")
            return

        c = None  # Canvas 对象的初始化为空
        for image_file in image_files:
            img_path = os.path.join(image_folder, image_file)
            img = Image.open(img_path)
            
            # 获取图片的原始尺寸
            pdf_width, pdf_height = img.size

            # 如果没有初始化Canvas对象，则使用第一张图片的大小进行初始化
            if c is None:
                c = canvas.Canvas(output_pdf)

            # 设置页面大小并添加图片
            c.setPageSize((pdf_width, pdf_height))
            c.drawImage(img_path, 0, 0, pdf_width, pdf_height)

            # 添加透明文字层
            c.setFont("Helvetica", 12)
            c.setFillColorRGB(1, 1, 1, alpha=0)  # 透明文字颜色
            c.drawString(10, 10, "")  # 空字符串，后续可替换为实际内容

            # 完成当前页面，准备下一页
            c.showPage()
        
        # 保存PDF文件
        c.save()
        print(f"PDF文件已成功保存为 {output_pdf}")
        
        pass

if __name__ == '__main__':
    fb = FileProcessingThread("卷内目录（给档案馆用）2022年度.xlsx",
                     "C:/Users/alant/Desktop/2、提供给档案馆用（需分件）20241021/提供给档案馆用（仅扫描，未分件，供分件测试用）")
    fb.start()
    print(fb.listErr)
