import os
import shutil
import numpy as np
import pandas as pd
import xlrd



class Part:
    def __init__(self):
        self.year = 2016  # 修改为你的年份# 读取Excel文件
        excel_path = './{}./卷内目录.xls'.format(self.year)
        df = pd.read_excel(excel_path,sheet_name='Sheet1',engine='xlrd')
        self.subfolder_names = df['文件级档号'].dropna().unique()
        self.root_names = df['案卷级档号'].dropna().unique()
        self.page_counts = df['张页号'].dropna().to_numpy()
        #print(self.subfolder_names,self.root_names)
    def make_dir(self):
        subfolder_names = self.subfolder_names
        for root_name in self.root_names:
            root_id = root_name.split('-')[-1]
            for subfolder_name in subfolder_names:
                sub_id = subfolder_name.split('-')[-2]
                if(sub_id == root_id):
                    if not os.path.exists(f'./{self.year}/{root_name}/{subfolder_name}'):
                        os.mkdir(f'./{self.year}/{root_name}/{subfolder_name}')
                    subfolder_names = subfolder_names[subfolder_names != subfolder_name]
                    #删除已经创建的文件夹后folders_name中的subfolder_name，提高运行效率
    def img_part(self):
        dit = {}
        for subfolder_name,page_count in zip(self.subfolder_names,self.page_counts):
            dit[subfolder_name] = page_count
        root_index = 0
        root_name = self.root_names[root_index]
        path = f'./{self.year}/{root_name}/'
        jpg_files = [file for file in os.listdir(path) if file.endswith('.jpg')]
        jpg_count = 1
        for i in range(len(self.subfolder_names)):
            subfolder_name = self.subfolder_names[i]
            npath = f'./{self.year}/{root_name}/{subfolder_name}/'
            try:
                jpg_strict = int(dit[self.subfolder_names[i + 1]])
                while(jpg_count < jpg_strict):
                    jpg_path = os.path.join(path,jpg_files[jpg_count - 1])
                    njpg_path = os.path.join(npath,jpg_files[jpg_count - 1])
                    shutil.move(jpg_path,njpg_path)
                    jpg_count = jpg_count + 1
            except:
                #处理倒数第二组数据
                jpg_strict = int(dit[self.subfolder_names[i + 1]].split('-')[0])
                while(jpg_count < jpg_strict):
                    jpg_path = os.path.join(path,jpg_files[jpg_count - 1])
                    njpg_path = os.path.join(npath,jpg_files[jpg_count - 1])
                    shutil.move(jpg_path,njpg_path)
                    jpg_count = jpg_count + 1
                #处理最后一组数据
                i = i + 1
                subfolder_name = self.subfolder_names[i]
                npath = f'./{self.year}/{root_name}/{subfolder_name}/'
                jpg_strict = int(dit[self.subfolder_names[i]].split('-')[1])
                while(jpg_count <= jpg_strict):
                    jpg_path = os.path.join(path,jpg_files[jpg_count - 1])
                    njpg_path = os.path.join(npath,jpg_files[jpg_count - 1])
                    shutil.move(jpg_path,njpg_path)
                    jpg_count = jpg_count + 1
                root_index = root_index + 1
                try:
                    root_name = self.root_names[root_index]
                    jpg_count = 1
                    root_name = self.root_names[root_index]
                    path = f'./{self.year}/{root_name}/'
                    jpg_files = [file for file in os.listdir(path) if file.endswith('.jpg')]
                except:
                    print("分类完成！")
                    break



if __name__ == "__main__":
    part = Part()
    part.make_dir()
    part.img_part()