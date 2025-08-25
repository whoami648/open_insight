from .doc_num import get_documentation_and_links_from_repo
import os

PATH = os.path.dirname(os.path.abspath(__file__))

class Industry_Support:
    def __init__(self,repo_url,version=None):
        self.repo_url = repo_url
        self.version = version
        self.doc_number = {}
        #self.doc_quarty = {}
        self.doc_number = get_documentation_and_links_from_repo(self.repo_url,self.version) # 字典格式
        #self.doc_quarty = doc_quarty_all(self.repo_url,self.version)

    def get_doc_quarty(self):
        return self.doc_quarty

    def get_doc_number(self):
        return self.doc_number
    
    def get_doc_all_mes(self):
        return self.get_doc_number()

