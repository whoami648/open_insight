import os
import sys
from opensearchpy import OpenSearch
from .utils import TOPICS_URL, TOPICS_PATH, save_json, check_github_gitee


def get_opensearch_client(opensearch_url = TOPICS_URL):

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
        "_source": ["topics"],
        "size": 10000
    }
    try:
        platform = check_github_gitee(repo_url)
        response = client.search(
            index=f"{platform}_event_repository*",
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

def solve(repo_url):
    """
    主函数，用于获取指定仓库的主题信息。
    """
    topics = get_topics(repo_url)
    repo_name = os.path.basename(repo_url)
    save_json(topics, os.path.join(TOPICS_PATH, f'{repo_name}_topics.json'))
    return topics


            
if __name__ == "__main__":
    topics = solve("https://github.com/pytorch/pytorch")
    print("Topics:", topics)


