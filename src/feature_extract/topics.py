import os
import sys
import json
from opensearchpy import OpenSearch
# user_name = "admin"
# code = "opensearch"

import pandas as pd
import configparser
import shutil

config = configparser.ConfigParser()
config.read("config.ini")  # 假设文件名为 config，但没有后缀
print(config.sections())  # 输出为空列表 []
OPENSEARCH = config.get("OPEN_CHECKService", "open_search_url_topics", fallback="")


def get_opensearch_client(opensearch_url = OPENSEARCH):
    
    """
    获取 OpenSearch 客户端。
    
    Returns:
        OpenSearch: OpenSearch 客户端实例。
    """
    try:
        client = OpenSearch(
            hosts=[opensearch_url],
            # http_auth=(user_name, code),
            use_ssl=False,
            verify_certs=False
        )
        return client
    except Exception as e:
        print(f"Error connecting to OpenSearch: {e}")
        sys.exit(1)



def get_topics(repo_url = "opensource_insight"):
    """
    获取 OpenSearch 中的所有主题信息。
    
    Returns:
        list: 包含所有主题的列表。
    """
    client = get_opensearch_client()

    query = {
        "query": {
            "term": {
                "html_url.keyword": {
                    "value": repo_url
                }
            }
        },
        "_source": [""],
        "size": 10000
    }
    try:
        response = client.search(
            index="github_event_repository*",
            body=query
        )
        
        topics = []
        hits = response.get('hits', {}).get('hits', [])
        for bucket in hits:
            topics+=bucket["_source"].get("topics", [])
        
        return topics
    
    except Exception as e:
        print(f"Error fetching topics: {e}")
        return []

def solve():
    """
    主函数，用于获取指定仓库的主题信息。
    """
    with open("/home/yixiang/zyx1/Agent_test/opensource_insight/repo.csv", "r") as f:
        reader = pd.read_csv(f)
        for row in reader.itertuples():
            if row.repo == "repo":
                continue
            repo_url = row.repo
            topics = get_topics(repo_url)
            print(f"Repository: {repo_url}, Topics: {topics}")


            
if __name__ == "__main__":
    topics = get_topics("https://github.com/pytorch/pytorch")
    print("Topics:", topics)


