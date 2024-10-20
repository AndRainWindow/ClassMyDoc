import os
import shutil
import sys
import pandas as pd



class Part:
    def __init__(self,file_path,excel_path):
        # 读取Excel文件
        self.file_path = file_path
        self.excel_path = excel_path
        self.errno_list = []
        df = pd.read_excel(excel_path, sheet_name='Sheet1', engine='xlrd')
        self.subfolder_names = df['文件级档号'].dropna().unique()
        self.root_names = df['案卷级档号'].dropna().unique()
        self.page_counts = df['张页号'].dropna().to_numpy()
        self.folds_count = df['文件页数'].dropna().to_numpy()
        del df
    def make_dir(self):
        """根据根文件夹和子文件夹名称创建目录"""
        for root_name in self.root_names:
            root_id = root_name.split('-')[-1]
            root_path = os.path.join(self.file_path,root_name)
            for subfolder_name in self.subfolder_names:
                sub_id = subfolder_name.split('-')[-2]
                if sub_id == root_id:
                    # 使用 makedirs 简化目录创建，exist_ok=True 防止重复创建时报错
                    folder_path = os.path.join(root_path,subfolder_name)
                    os.makedirs(folder_path, exist_ok=True)

    def img_part(self):
        """处理图片移动的主逻辑"""
        # 构建子文件夹和页数的映射
        page_count_dit = {subfolder_name: page_count for subfolder_name, page_count in zip(self.subfolder_names, self.page_counts)}
        root_index = 0
        jpg_count = 1   #判断当前母目录下的图片数量
        sub_jpg_should_count_dit = {subfolder_name: folds_count for subfolder_name, folds_count in zip(self.subfolder_names, self.folds_count)}
        # 初始路径和文件列表
        root_name = self.root_names[root_index]
        path = os.path.join(self.file_path, root_name)
        jpg_files = [file for file in os.listdir(path) if file.endswith('.jpg')]#获取当前目录下的所有jpg文件
        subfolder_name_index = 0
        while subfolder_name_index < len(self.subfolder_names):
            npath = os.path.join(path, self.subfolder_names[subfolder_name_index])
            try:
                # 正常处理数据
                jpg_strict = int(page_count_dit[self.subfolder_names[subfolder_name_index + 1]])  #获取当前子文件下可以存放的图片数量
                sub_jpg_should_count = sub_jpg_should_count_dit[self.subfolder_names[subfolder_name_index]]  #应该有的图片数量
                jpg_count,sub_jpg_count = self.move_images(jpg_files, path, jpg_count, jpg_strict, npath)
                self.check_jpg_count(npath, sub_jpg_should_count, sub_jpg_count)
                subfolder_name_index += 1
            except:
                # 处理每组root_folder下倒数第二组数据（范围处理）
                jpg_strict_start = int(page_count_dit[self.subfolder_names[subfolder_name_index + 1]].split('-')[0])
                sub_jpg_should_count = sub_jpg_should_count_dit[self.subfolder_names[subfolder_name_index]]
                jpg_count,sub_jpg_count = self.move_images(jpg_files, path, jpg_count, jpg_strict_start, npath)
                self.check_jpg_count(npath, sub_jpg_should_count, sub_jpg_count)
                # 处理最后一组数据
                subfolder_name_index += 1
                subfolder_name = self.subfolder_names[subfolder_name_index]
                npath = os.path.join(self.file_path,root_name,subfolder_name)
                jpg_strict_end = int(page_count_dit[self.subfolder_names[subfolder_name_index]].split('-')[1]) + 1
                sub_jpg_should_count = sub_jpg_should_count_dit[self.subfolder_names[subfolder_name_index]]
                jpg_count,sub_jpg_count = self.move_images(jpg_files, path, jpg_count, jpg_strict_end, npath)
                self.check_jpg_count(npath, sub_jpg_should_count, sub_jpg_count)
                # 切换到下一个 root_folder
                root_index += 1
                if root_index >= len(self.root_names):
                    return  # 结束处理
                    sys.exit(1)

                # 更新下一个 root_folder 的路径和文件列表
                root_name = self.root_names[root_index]
                path = os.path.join(self.file_path, root_name)
                jpg_files = [file for file in os.listdir(path) if file.endswith('.jpg')]
                jpg_count = 1  # 重置计数器
                subfolder_name_index += 1

    def move_images(self, jpg_files, path, jpg_count, jpg_strict, npath):
        """公共的图片移动逻辑"""
        sub_jpg_count = 0
        while jpg_count < jpg_strict and jpg_count <= len(jpg_files):
            jpg_path = os.path.join(path, jpg_files[jpg_count - 1])
            njpg_path = os.path.join(npath, jpg_files[jpg_count - 1])
            if jpg_count >= 2 and jpg_count <= len(jpg_files) - 1:
                jpg_info = jpg_files[jpg_count - 1].split('-')[0].split('.')[0]
                jpg_info_pre = jpg_files[jpg_count - 2].split('-')[0].split('.')[0]
                if((int(jpg_info) - int(jpg_info_pre)) != 1):
                    self.errno_list.append("{}图片命名出现异常,请检查图片数量以及命名是否正确无误。".format(npath))
                    sys.exit(1)
            shutil.move(jpg_path, njpg_path)
            jpg_count += 1
            sub_jpg_count += 1
        return jpg_count,sub_jpg_count

    def check_jpg_count(self,npath,sub_jpg_should_count,sub_jpg_count):
        if(sub_jpg_count != sub_jpg_should_count):
            self.errno_list.append("{}路径下图片数量异常！".format(npath))
        else:
            return

    def errno_return(self):
        return self.errno_list




if __name__ == "__main__":
    part = Part()
    part.make_dir()
    part.img_part()
    part.errno_list()