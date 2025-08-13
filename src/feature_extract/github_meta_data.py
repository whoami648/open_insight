import os
import sys
import json
from opensearchpy import OpenSearch
import csv
import pandas as pd
from tqdm import tqdm


def get_opensearch_client(opensearch_url):
    """
    获取 OpenSearch 客户端。
    
    Returns:
        OpenSearch: OpenSearch 客户端实例。
    """
    try:
        client = OpenSearch(
            hosts=[opensearch_url],
            use_ssl=False,
            verify_certs=False,
            timeout=30  # 增加超时时间
        )
        return client
    except Exception as e:
        print(f"Error connecting to OpenSearch: {e}")
        sys.exit(1)

def get_query(index,repo_url):
    """
    获取指定仓库的主题信息。
    
    Args:
        index (str): OpenSearch索引名称
        repo_url (str): 仓库的URL
        
    Returns:
        list: 包含主题的列表
    """
    query = {
        "query": {
            "term": {
                "repository_url": repo_url
            }
        }
    }
    
    return query


class GitHubMetadata:
    def __init__(self, opensearch_url, repo_url):
        self.client = get_opensearch_client(opensearch_url)
        self.repo_url = repo_url

    def get_metadata(self,index,repo_url):
        """        获取指定仓库的元数据。"""

        query = get_query(index, repo_url)
        response = self.client.search(index=index, body=query)

        if response['hits']['hits']:
            return response['hits']['hits'][0]['_source']
        else:
            return {}
        
    def get_metadata(self, index):
        """
        获取指定索引中的所有仓库元数据。
        
        Args:
            index (str): OpenSearch索引名称
            
        Returns:
            list: 包含所有仓库元数据的列表
        """
        all_metadata = []
        scroll_query = {
            "query": {
                "match_all": {
                    "boost": 1.0,
                    "minimum_should_match": "1",
                    "should": [
                        {
                            "term": {
                                "tag": self.repo_url
                            }
                        },
                        {
                            "term": {
                                "tag_name": index
                            }
                        }
                    ]


                }
            },
            # "_source": ["repository_url", "language", "version", "release_notes", "repo_name", "commit_message", "issues"],
            "size": 1000
        }
        
        # response = self.client.search(index=index, scroll="5m", body=scroll_query)
        # scroll_id = response["_scroll_id"]


        # while len(response["hits"]["hits"]):
        #     all_metadata.extend([hit["_source"] for hit in response["hits"]["hits"]])
        #     response = self.client.scroll(scroll_id=scroll_id, scroll="5m")
        #     scroll_id = response["_scroll_id"]

        return all_metadata
    
    def get_release_notes(self):
        """        获取指定索引中的所有仓库的发布说明。"""
        # 获取所有仓库的元数据
        get_metadata = self.get_metadata("github_repo_raw")
        release_notes = []
        for item in get_metadata:
            release_notes.append(item.get("release_notes", ""))
        return release_notes
