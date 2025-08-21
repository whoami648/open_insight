import os
import sys
from opensearchpy import OpenSearch

from .utils import METADATA_URL, METADATA_PATH, save_json

def get_opensearch_client(opensearch_url):
    try:
        client = OpenSearch(
            hosts=[opensearch_url],
            use_ssl=False,
            verify_certs=False,
            timeout=60  # 增加超时时间
        )
        return client
    except Exception as e:
        print(f"Error connecting to OpenSearch: {e}")
        sys.exit(1)

def get_query(repo_url):
    query = {
        "query": {
            "term": {
                "tag": repo_url
            }
        }
    }
    
    return query


class GitHubMetadata:
    def __init__(self, repo_url):
        self.client = get_opensearch_client(METADATA_URL)
        self.repo_url = repo_url

    def get_metadata(self, index, repo_url):
        """获取指定仓库的元数据。"""

        query = get_query(repo_url)
        response = self.client.search(index=index, body=query)

        if response['hits']['hits']:
            return response['hits']['hits'][0]['_source']
        else:
            return {}
        
    def get_metadata_from_index(self, index):
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
            "_source": ["repository_url", "language", "version", "release_notes", "repo_name", "commit_message", "issues"],
            "size": 1000
        }
        
        return all_metadata
    
    def get_release_notes(self):
        """获取指定索引中的仓库的发布说明。"""
        get_metadata = self.get_metadata("github-repo_raw", self.repo_url)
        repo_name = os.path.basename(self.repo_url)
        save_json(get_metadata, os.path.join(METADATA_PATH, f'{repo_name}_release_notes.json'))
        return get_metadata

    def get_version(self):
        """获取指定索引中的仓库的版本信息。"""
        import json
        import os
        repo_name = os.path.basename(self.repo_url)
        json_path = os.path.join(METADATA_PATH, f"{repo_name}_release_notes.json")
        if not os.path.exists(json_path):
            print(f"文件不存在: {json_path}")
            return None
        
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 查找版本信息
        try:
            releases = data.get("data", {}).get("releases", [])
            if releases and "tag_name" in releases[0]:
                return releases[0]["tag_name"]
            else:
                print("未找到版本信息")
                return None
        except Exception as e:
            print(f"解析版本信息出错: {e}")
            return None

if __name__ == "__main__":
    repo_url = "https://github.com/pytorch/pytorch"
    metadata = GitHubMetadata(repo_url)
    release_notes = metadata.get_release_notes()