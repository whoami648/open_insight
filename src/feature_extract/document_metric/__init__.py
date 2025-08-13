'''
Descripttion: 
version: V1.0
Author: zyx
Date: 2025-03-04 18:01:38
LastEditors: zyx
LastEditTime: 2025-03-26 17:04:36
'''
'''
Descripttion: 
version: V1.0
Author: zyx
Date: 2025-03-04 10:23:24
LastEditors: zyx
LastEditTime: 2025-03-20 17:04:55
'''
from document_metric.doc_quarty import doc_quarty_all
# from document_metric.doc_chinese_support import doc_chinexe_support_git
from document_metric.doc_num import get_documentation_links_from_repo
# from document_metric.organizational_contribution import organizational_contribution
from document_metric.utils import save_json
import os
PATH = os.path.dirname(os.path.abspath(__file__))
class Industry_Support:
    '''get the documentation quality, documentation number, Chinese documentation files, and organizational contribution of a repository'''

    def __init__(self,client,repo_list,version):
        self.repo_list = repo_list
        self.version = version
        self.client = client
        self.doc_number = {}
        self.doc_quarty = {}
        self.zh_files = {}
        for repo_url in self.repo_list:
            self.doc_number[repo_url] = get_documentation_links_from_repo(repo_url,version)
            

    
    def get_doc_quarty(self):
        for repo_url in self.repo_list:
            self.doc_quarty[repo_url] = doc_quarty_all(repo_url,self.version)
        get_doc_quarty = self.doc_quarty

        ans = {"doc_quarty":0, "doc_quarty_details":[]}
        for key,doc_quarty in get_doc_quarty.items():
            ans["doc_quarty"] += doc_quarty["doc_quarty"] / len(self.repo_list)
            ans["doc_quarty_details"].append(
                {
                    "repo_url": key,
                    "doc_quarty_details": doc_quarty
                }
            )
            # if ans["doc_quarty_details"].get(key) is None:
            #     ans["doc_quarty_details"][key] = {}
            # ans["doc_quarty_details"][key]["doc_quarty_details"] = doc_quarty["doc_quarty_details"]
        
        save_json(ans,os.path.join(PATH,"doc_quarty.json"))

        return ans # {"doc_quarty":0, "doc_quarty_details":{}}

    
    def get_doc_number(self):
        get_doc_number = self.doc_number
        ans = {"doc_number":0, "folder_document_details":[]}
        for key,doc_number in get_doc_number.items():
            ans["doc_number"] += doc_number["doc_number"] / len(self.repo_list)
            ans["folder_document_details"].append(
                {
                    "repo_url": key,
                    "folder_document_details": doc_number
                }
            )
         
        save_json(ans,os.path.join(PATH,"doc_number.json"))
        return ans 

    
if __name__ == '__main__':
    a = ["https://github.com/git-lfs/git-lfs"]
    dm = Industry_Support(123,a,'v2.7.2')
