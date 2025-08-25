from .document_metric import Industry_Support
from .utils import save_json, RES_PATH
from .github_meta_data import GitHubMetadata
from .TPL import solve as solve_tpl
from .topics import solve as solve_topics

import os

class FeatureExtract:
    def __init__(self, repo_url, version=None, language=None):
        self.repo_url = repo_url
        self.version = version
        self.language = language
        self.github_metadata = {}
        self.topics = {}
        self.tpl = {}
        self.doc = {}

    def get_doc(self):
        dm = Industry_Support(self.repo_url, self.version)
        self.doc = dm.get_doc_all_mes()
        return self.doc

    def get_topics(self):
        topics = solve_topics(self.repo_url)
        self.topics = topics
        return self.topics
    
    def get_metadata(self):
        metadata = GitHubMetadata(self.repo_url)
        self.github_metadata = metadata.get_release_notes()
        if self.version is None:
            self.version, _ = metadata.get_version_and_language()
            print(f"get version is {self.version}")

        if self.language is None:
            _, self.language = metadata.get_version_and_language()
            print(f"get language is {self.language}")

        return self.github_metadata

    def get_tpl(self):
        tpl = solve_tpl(self.repo_url, self.version, self.language)
        self.tpl = tpl
        return self.tpl


    def get_repo_all_mes(self):
        res =  {
            "doc": self.get_doc(),
            "topics": self.get_topics(),
            "metadata": self.get_metadata(),
            "tpl": self.get_tpl()
        }
        save_json(res, os.path.join(RES_PATH, f'{self.repo_url.split("/")[-1]}.json'))
        return res