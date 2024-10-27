import os
import shutil
import pandas as pd



class FileBunding():
    def __init__(self,excelDir, fileDir) -> None:
        self.fileDir = fileDir
        if os.path.exists(excelDir):
            self.dpFileInternal = pd.read_excel(excelDir)
        else:
            self.dpFileInternal = None
        self.listErr = []   # 错误信息列表


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

if __name__ == '__main__':
    fb = FileBunding()
    is_excel_right = fb.checkExcel()
    if is_excel_right:
        fb.movImage()
    fb.returnErr()
    fb.check_jpg()
    print(fb.listErr)
