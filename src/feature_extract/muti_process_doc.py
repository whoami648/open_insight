
import os
import subprocess 
import requests
import json
import csv
from typing import List
import re
from document_metric import Industry_Support
from multiprocessing import Pool
import ast
from tqdm import tqdm
import multiprocessing
# from utils import LOG
# 3279
"""多进程处理开源项目文档的类"""
class muti_process_doc:
    def __init__(self, repo_list: List[str], version):
        self.repo_list = repo_list
        self.version = version


    def run(self):
        """
        执行多进程处理文档的函数
        :return: 返回处理后的数据
        """
        params = list(zip(self.repo_list, self.version))

        # 获取 CPU 核心数（自动适配）
        cpu_count = multiprocessing.cpu_count()//2

        # 创建进程池
        with multiprocessing.Pool(processes=cpu_count) as pool:
            # 使用 starmap 传递多个参数[1,6](@ref)
            try:
                results = pool.starmap(self.process_repo, params)
            except Exception as e:
                print(f"Error occurred during multiprocessing: {e}")
                results = []
                pass
        

    def process_repo(self, repo, versions):
        """
        处理单个仓库的文档
        :param repo: 仓库地址
        :return: 处理后的数据
        """
        # LOG.set_log_file("document_extract.log")
        print(f"Processing repository: {repo} with version: {versions}")
        
        for version in versions:
            # 这里可以添加对每个版本的处理逻辑
            print(f"Processing version: {version} for repository: {repo}")
            json_file = os.path.basename(repo) + "-" + version + ".json"

            if json_file in os.listdir("opensource_insight/tmp/json"):
                print(f"File {json_file} already exists, skipping...")
                continue

            try:

                dm = Industry_Support(123, [repo], version)
                break

            except Exception as e:
                # print(f"Error occurred while processing {repo} version {version}: {e}")
                continue

        # data = dm.get_doc_quarty()

        # return dataS
        # 假设Industry_Support有一个get_doc_quarty方法用于获取文档质量数据
        # data = dm.get_doc_quarty()
        # return data
    
def solve():

    solved = os.listdir("opensource_insight/tmp/json")
    repo_url = []
    versions = []
    with open("/home/yixiang/zyx1/Agent_test/opensource_insight/repo.csv", "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == "repo":
                continue
            inner = os.path.basename(row[0])+"-"+ast.literal_eval(row[1])[0]+".json"

            if inner in solved:
                continue
            repo_url.append(row[0])
            versions.append(ast.literal_eval(row[1]))
            # dm = muti_process_doc([repo_url], version
    print("load over")
    dm = muti_process_doc(repo_url, versions).run()
if __name__ == "__main__":
    # a = ["https://github.com/git-lfs/git-lfs","2"]
    # dm = muti_process_doc(a,['v2.7.2',"2"])
    # data = dm.run()
    # with open("doc_quarty.json", "w") as f:
    #     json.dump(data, f, indent=4)
    # print(data)
    solve()

    #opensearch-reporting-cli -u http://49.0.253.31:7601/app/dashboards#/view/7adfa750-4c81-11e8-b3d7-01146121b73d -f csv -a basic -c admin:opensearch -e ses -s <email address> -r <email address>
