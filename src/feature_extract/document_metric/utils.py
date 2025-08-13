'''
Descripttion: 
version: V1.0
Author: zyx
Date: 2025-01-16 17:34:10
LastEditors: zyx
LastEditTime: 2025-03-04 17:44:17
'''
import json
import os
import sys
import requests
import tqdm
import markdown
import configparser


config = configparser.ConfigParser()
NOW_PATH =  os.path.dirname(os.path.abspath(__file__))
config.read(os.path.join(NOW_PATH,r'config.ini'))
GITEE_TOKEN = config.get('OPEN_CHECKService', 'GITEE_TOKEN')
GITHUB_TOKEN = config.get('OPEN_CHECKService', 'GITHUB_TOKEN')



DATA_PATH = config.get('OPEN_CHECKService', 'tmp_path')

TMP_PATH = os.path.join(DATA_PATH,'repos_tmp')
JSON_REPOPATH = os.path.join(DATA_PATH,'json')


if not os.path.exists(TMP_PATH):
    os.makedirs(TMP_PATH)
if not os.path.exists(JSON_REPOPATH):
    os.makedirs(JSON_REPOPATH)

def get_github_readme(repo):
    url = f'https://api.github.com/repos/{repo}/readme'
    headers = {'Authorization': f'token {get_github_token()}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return markdown.markdown(response.json()['content'])
    
    else:
        response.raise_for_status()

def get_gitee_readme(repo):
    url = f'https://gitee.com/api/v5/repos/{repo}/readme'
    headers = {'Authorization': f'token {get_gitee_token()}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['content']
    else:
        response.raise_for_status()

def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)
        return True

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)
    
def get_github_token():
    return os.getenv('GITHUB_TOKEN', GITHUB_TOKEN)

def get_gitee_token():
    return  os.getenv('GITEE_TOKEN', GITEE_TOKEN)

def clone_repo_not_version(repo_url):
    """
    Clone a repository from GitHub or Gitee without specifying a version.
    Args:
        repo_url (str): The URL of the repository to clone.
    Returns:
        tuple: A tuple containing a boolean and a string. The boolean indicates 
               whether the cloning was successful, and the string is the path 
               to the cloned repository if successful, otherwise None.
    Raises:
        ValueError: If the platform is not 'github' or 'gitee'.
    """
    repo_url = repo_url.replace('https://', '')
    platform = check_github_gitee(repo_url)
    
    if platform == 'github':
        token = get_github_token()
    elif platform == 'gitee':
        token = get_gitee_token()
    else:
        raise ValueError("Unsupported platform. Use 'github' or 'gitee'.")

    repo_name = repo_url.split('/')[-1]
    clone_path = os.path.join(TMP_PATH, repo_name)

    clone_command = f'git clone https://{token}@{repo_url} {clone_path}'
    
    result = os.system(clone_command)

    if result == 0:
        return True, clone_path
    else:
        return False, None
def clone_repo(repo_url,version):
    """
    Clone a repository from GitHub or Gitee.
    Args:
        repo_url (str): The URL of the repository to clone.
    Returns:
        tuple: A tuple containing a boolean and a string. The boolean indicates 
               whether the cloning was successful, and the string is the path 
               to the cloned repository if successful, otherwise None.
    Raises:
        ValueError: If the platform is not 'github' or 'gitee'.
    """
    repo_url = repo_url.replace('https://', '')
    platform = check_github_gitee(repo_url)
    
    if platform == 'github':
        token = get_github_token()
    elif platform == 'gitee':
        token = get_gitee_token()
    else:
        raise ValueError("Unsupported platform. Use 'github' or 'gitee'.")

    repo_name = repo_url.split('/')[-1]
    clone_path = os.path.join(TMP_PATH, repo_name)
    new_clone_path = os.path.join(TMP_PATH, repo_name + "-"+version)

    clone_command = f'git clone --branch {version} https://{token}@{repo_url} {clone_path}'


    result = os.system(clone_command)



    if result == 0:
        if os.path.exists(clone_path):
            os.rename(clone_path, new_clone_path)
        return True,new_clone_path
    else:
        return False, None
    
def check_github_gitee(url):
    if 'github.com' in url:
        return 'github'
    elif 'gitee.com' in url:
        return 'gitee'
    else:
        return None

import requests
from urllib.parse import urlparse

def get_owner_and_repo_from_url(url):
    """从仓库 URL 中提取仓库所有者和仓库名称"""
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')
    if len(path_parts) < 2:
        raise ValueError("Invalid repository URL")
    owner = path_parts[0]
    repo = path_parts[1]
    return owner, repo

def get_github_tag_commit_date(url, tag_name, token=None):
    """获取 GitHub 仓库中指定 tag 的提交时间"""
    try:
        owner, repo = get_owner_and_repo_from_url(url)
        # 获取 tags 列表
        tags_url = f"https://api.github.com/repos/{owner}/{repo}/tags"
        headers = {}
        if token:
            headers["Authorization"] = f"token {token}"
        response = requests.get(tags_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to get tags. Status code: {response.status_code}")
            return None
        tags = response.json()
        # 查找指定的 tag
        for tag in tags:
            if tag["name"] == tag_name:
                commit_sha = tag["commit"]["sha"]
                # 获取 commit 的详细信息
                commit_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}"
                commit_response = requests.get(commit_url, headers=headers)
                if commit_response.status_code != 200:
                    print(f"Failed to get commit info for {commit_sha}. Status code: {commit_response.status_code}")
                    return None
                commit_data = commit_response.json()
                return commit_data["commit"]["committer"]["date"]
        print(f"Tag '{tag_name}' not found")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_gitee_tag_commit_date(url, tag_name, token=None):
    """获取 Gitee 仓库中指定 tag 的提交时间"""
    try:
        owner, repo = get_owner_and_repo_from_url(url)
        # 获取 tags 列表
        tags_url = f"https://gitee.com/api/v5/repos/{owner}/{repo}/tags"
        headers = {}
        if token:
            headers["Authorization"] = f"token {token}"
        params = {"access_token": token} if token else None
        response = requests.get(tags_url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Failed to get tags. Status code: {response.status_code}")
            return None
        tags = response.json()
        # 查找指定的 tag
        for tag in tags:
            if tag["name"] == tag_name:
                commit_sha = tag["commit"]["sha"]
                # 获取 commit 的详细信息
                commit_url = f"https://gitee.com/api/v5/repos/{owner}/{repo}/commits/{commit_sha}"
                commit_params = {"access_token": token} if token else None
                commit_response = requests.get(commit_url, headers=headers, params=commit_params)
                if commit_response.status_code != 200:
                    print(f"Failed to get commit info for {commit_sha}. Status code: {commit_response.status_code}")
                    return None
                commit_data = commit_response.json()
                return commit_data["committer"]["date"]
        print(f"Tag '{tag_name}' not found")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_tag_commit_date(url, tag_name, token=None):
    """根据仓库 URL 获取指定 tag 的提交时间"""
    if "github.com" in url:
        return get_github_tag_commit_date(url, tag_name, token)
    elif "gitee.com" in url:
        return get_gitee_tag_commit_date(url, tag_name, token)
    else:
        print("Unsupported repository platform")
        return None



if __name__ == '__main__':
        # 替换为你的仓库 URL 和 tag 名称
    repo_url = "https://github.com/apache/kafka"
    # repo_url = "https://gitee.com/your_gitee_username/your_repository_name"
    tag_name = "v1.0.0"
    token = "your_personal_access_token"  # 如果需要，替换为你的 GitHub 或 Gitee 个人访问令牌

    commit_date = get_tag_commit_date(repo_url, tag_name, token)
    if commit_date:
        print(f"Tag: {tag_name}, Commit Date: {commit_date}")
    