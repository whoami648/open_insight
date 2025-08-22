import os
import subprocess
import logging
import json

import pandas as pd
from opensearchpy import OpenSearch
import shutil
from pathlib import Path
import configparser

config = configparser.ConfigParser()
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
read_files = config.read(os.path.join(PROJECT_ROOT, 'config.ini'))
DATA_PATH = config.get('GLOBAL_PATHS', 'tmp_path')
SAVE_PATH = config.get('GLOBAL_PATHS', 'save_path')

TMP_PATH = os.path.join(DATA_PATH,'repos_tmp')
JSON_REPOPATH = os.path.join(SAVE_PATH,'doc')
DOC_NUM_PATH = JSON_REPOPATH
METADATA_PATH = os.path.join(SAVE_PATH,'metadata')
TOPICS_PATH = os.path.join(SAVE_PATH, 'topics')
TPL_PATH = os.path.join(SAVE_PATH, 'tpl')

RES_PATH = os.path.join(SAVE_PATH, 'res')

if not os.path.exists(TMP_PATH):
    os.makedirs(TMP_PATH)
if not os.path.exists(JSON_REPOPATH):
    os.makedirs(JSON_REPOPATH)
if not os.path.exists(DOC_NUM_PATH):
    os.makedirs(DOC_NUM_PATH)
if not os.path.exists(METADATA_PATH):
    os.makedirs(METADATA_PATH)
if not os.path.exists(TOPICS_PATH):
    os.makedirs(TOPICS_PATH)
if not os.path.exists(TPL_PATH):
    os.makedirs(TPL_PATH)
if not os.path.exists(RES_PATH):
    os.makedirs(RES_PATH)

METADATA_URL = config.get('OPEN_CHECKService', 'open_search_url_metadata')
TOPICS_URL = config.get('OPEN_CHECKService', 'open_search_url_topics')

class LOG:
    """Logging class for handling log messages."""
    def __init__(self, log_file: str = "app.log"):
        logging.basicConfig(filename=log_file, level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
    def set_log_file(self, log_file: str):
        """Set the log file for logging."""
        logging.basicConfig(filename=log_file, level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
    def info(self, message: str):
        logging.info(message)

    def error(self, message: str):
        logging.error(message)

    def debug(self, message: str):
        logging.debug(message)



"""多进程类模板"""
class MultiProcessTemplate:
    def __init__(self, repo_list: list, version: str,scrpt_path: str = None):

        self.repo_list = repo_list # List of repositories

        self.version = version # Version of the repositories

        self.package_name = repo_list.split("/")[-1] # Package name extracted from the repository URL

        self.user = repo_list.split("/")[-2] # User or organization name extracted from the repository URL

        self.scrpt_path = scrpt_path # Path to the script to be executed in the subprocess

        self.log = LOG()  # Initialize the logging class

    def run_script(self):
        """Run the script in a subprocess."""
        if not self.scrpt_path:
            raise ValueError("Script path is not set.")
        
        try:
            result = subprocess.run(
                ["python", self.scrpt_path, self.repo_list, self.version],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise RuntimeError(f"Script failed with error: {result.stderr}")
            return result.stdout
        except Exception as e:
            self.log.error(f"Error running script: {e}")
            raise
    def control_process(self):
        """Control the subprocess execution."""
        try:
            output = self.run_script()
            self.log.info(f"Script executed successfully: {output}")
            return output
        except Exception as e:
            self.log.error(f"Error in control_process: {e}")
            return None


def daochu_data():
    # 1. 连接OpenSearch
    client = OpenSearch(
        hosts=[{"host": "localhost", "port": 9200}],
        http_auth=("admin", "admin"),
        use_ssl=False
    )

    # 2. 分页查询数据
    all_data = []
    scroll_query = {"query": {"match_all": {}}}
    response = client.search(index="github-release_enriched", scroll="5m", size=1000, body=scroll_query)
    scroll_id = response["_scroll_id"]

    while len(response["hits"]["hits"]):
        all_data.extend([hit["_source"] for hit in response["hits"]["hits"]])
        response = client.scroll(scroll_id=scroll_id, scroll="5m")
        scroll_id = response["_scroll_id"]

    # 3. 导出CSV
    df = pd.DataFrame(all_data)
    df.to_csv("github_release_export.csv", index=False, encoding="utf-8")
    print("导出成功！")

def delete_oldest_dirs(base_dir: str, num_to_delete: int = 1000):
    base_path = Path(base_dir)
    if not base_path.exists() or not base_path.is_dir():
        print(f"{base_dir} does not exist or is not a directory.")
        return

    # List all directories in base_path
    dirs = [d for d in base_path.iterdir() if d.is_dir()]
    # Sort by creation time (oldest first)
    dirs.sort(key=lambda d: d.stat().st_ctime)
    # Select the oldest num_to_delete directories
    to_delete = dirs[:num_to_delete]

    for d in to_delete:
        try:
            shutil.rmtree(d)
            print(f"Deleted: {d}")
        except Exception as e:
            print(f"Failed to delete {d}: {e}")

def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)
        return True

def check_github_gitee(url):
    if 'github.com' in url:
        return 'github'
    elif 'gitee.com' in url:
        return 'gitee'
    else:
        return None

    # Example usage:
if __name__ == "__main__":
    # daochu_data()
    # Example usage of MultiProcessTemplate

    delete_oldest_dirs("", 1000)

