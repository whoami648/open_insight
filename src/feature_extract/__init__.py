from github_meta_data import GitHubMetadata
from
from document_metric import Industry_Support,save_json
from typing import List
import os
import configparser

config = configparser.ConfigParser()
config.read("config.ini")  # 假设文件名为 config，但没有后suffix


# 全局变量
OPENSEARCH = config.get("OPEN_CHECKService", "open_search_url", fallback="")
TMP_PATH = config.get("TMP_PATH", "tmp_path", fallback="/tmp")

# Temporary paths
JSON_REPOPATH = os.path.join(TMP_PATH, "json_repo")
if not os.path.exists(JSON_REPOPATH):
    os.makedirs(JSON_REPOPATH)




class FeatureExtract:
    def __init__(self, repo_name, version):
        self.repo_name = repo_name
        self.version = version
        self.doc_number = {}
        self.language = ""
        self.gitub_metadata = None
        self.repo_file = ""
        self.topics = ""


    def run(self, opensearch_url):
        """执行特征提取"""
        # github meatadata 从osscompass中获取
        self.client = GitHubMetadata(opensearch_url, self.repo_name, self.version)


        # 获取文档数据
        self.doc_number = Industry_Support(self.client, [self.repo_name], self.version).get_doc_number()
        save_json(self.doc_number, os.path.join(JSON_REPOPATH, f'{self.repo_name}-{self.version}_doc_number.json'))


        # 获取第三方库信息
        pass

        # 获取语言信息和元数据
        self.language = self.client.get_metadata(self.repo_name, self.version).get("language", "")

        self.gitub_metadata = self.client.get_metadata(self.repo_name, self.version)

        # 获取仓库文件信息
        self.repo_file = self.client.get_metadata(self.repo_name, self.version).get("repo_file", "")






        return {
            "doc_number": self.doc_number,
            "doc_quarty": self.doc_quarty
        }
    