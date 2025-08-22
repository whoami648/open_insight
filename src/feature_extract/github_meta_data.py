import os
import sys
from opensearchpy import OpenSearch

from .utils import METADATA_URL, METADATA_PATH, save_json, check_github_gitee

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

def get_query_repo_name(repo_url):
    query = {
        "query": {
            "term": {
                "repo_name": f"{repo_url}.git"
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
        if index == "github-git_enriched" or index == "gitee-git_enriched":
            query = get_query_repo_name(repo_url)
        else:
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
        platform = check_github_gitee(self.repo_url)

        get_metadata = {
            "release_notes": self.get_metadata(f"{platform}-repo_raw", self.repo_url),
            "pull_title": self.get_metadata(f"{platform}-event_enriched", self.repo_url),
            "commit_message": self.get_metadata(f"{platform}-git_enriched", self.repo_url),
        }
        
        repo_name = os.path.basename(self.repo_url)
        #save_json(get_metadata, os.path.join(METADATA_PATH, f'{repo_name}_release_notes.json'))

        metadata_new = self.get_mes_from_metadata(get_metadata)
        save_json(metadata_new, os.path.join(METADATA_PATH, f'{repo_name}_metadata.json'))

        return metadata_new

    def get_mes_from_metadata(self, get_metadata):
        """从元数据中提取所需的信息。"""
        metadata_new = {
            "release_notes": {},
            "language": None,
            "pull_title": "",
            "commit_message": ""
        }
        try:
            releases = get_metadata.get("release_notes", {}).get("data", {}).get("releases", [])
            metadata_new["release_notes"] = {
                "version": releases[0].get("tag_name", ""),
                "body": releases[0].get("body", "")
            }
            metadata_new["language"] = get_metadata.get("release_notes", {}).get("data", {}).get("language", None)
            metadata_new["pull_title"] = get_metadata.get("pull_title", {}).get("title", "")
            metadata_new["commit_message"] = get_metadata.get("commit_message", {}).get("message", "")
            return metadata_new
        except Exception as e:
            print(f"提取元数据时出错: {e}")

        return metadata_new

    def get_version_and_language(self):
        """获取指定索引中的仓库的版本信息和编程语言。"""
        import json
        import os
        repo_name = os.path.basename(self.repo_url)
        json_path = os.path.join(METADATA_PATH, f"{repo_name}_metadata.json")
        if not os.path.exists(json_path):
            print(f"文件不存在: {json_path}")
            return None
        
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 查找版本信息
        try:
            release = data.get("release_notes", {})
            if release and "version" in release:
                version = release["version"]
                language = data.get("language", None)
                return version, language
            else:
                print("未找到信息")
                return None, None
        except Exception as e:
            print(f"解析版本信息出错: {e}")
            return None, None

if __name__ == "__main__":
    repo_url = "https://gitee.com/JianYong0726/ragflow"
    metadata = GitHubMetadata(repo_url)
    release_notes = metadata.get_release_notes()