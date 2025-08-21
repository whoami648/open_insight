import os

from .utils import save_json,clone_repo,clone_repo_not_version,TMP_PATH,JSON_REPOPATH, DOC_NUM_PATH
import re

def count_documents_from_folder(path, extensions=None)->tuple:
    if extensions is None:
        extensions = [".md", ".yaml", ".pdf", ".yml", ".html", ".doc", ".docx",".txt",".rst"]
    
    document_count = 0
    document_details = []

    for root, dirs, files in os.walk(path):
        for file in files:
            if "requirements" in file:
                continue
            if any(file.endswith(ext) for ext in extensions):
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        content = f.read()
                    document_count += 1
                    document_details.append({
                        "name": file,
                        "path": os.path.join(root, file).replace(TMP_PATH, "")[1:].replace("\\", "/"),
                        "content": content
                    })
                except:
                    continue
    return document_count, document_details

def count_documents_from_Readme(markdown)->tuple:
    link_count = 0
    links = []
    video_sites = ["youtube.com", "vimeo.com", "dailymotion.com","blibli.com","img","gif","jpg","jpeg","png","svg"]
    markdown_split = markdown.split('\n')
    for line in markdown_split:
        # Check for links in <a> tags
        if "<a href" in line:
            link = line.split('href="')[1].split('"')[0].replace(")", "")
            if not any(video_site in link for video_site in video_sites):
                link_count += 1
                links.append(
                    {
                    "name": link.replace("http://", "").replace("https://", ""),
                    "path" : link
                    }
                    )
        # Check for plain text links
        else:
            urls = re.findall(r'(https?://\S+)', line)
            for url in urls:
                url = url.split(')')[0]
                if not any(video_site in url for video_site in video_sites):
                    link_count += 1
                    links.append({
                    "name": url.replace("http://", "").replace("https://", ""),
                    "path" : url
                    })
    return link_count, links

def search_readme_in_folder(path)->tuple:
    readme_files = ["README.md", "README.txt", "README.rst","README","readme.md", "readme.txt", "readme.rst","readme"]
    readme_contents = ""
    flag = False

    for files in os.listdir(path):
        if not os.path.isfile(files):
            continue
        

        if files in readme_files:
            flag = True # README file found
            with open(os.path.join(path, files), 'r', encoding='utf-8') as f:
                readme_contents=f.read()
                break
    
    return flag,readme_contents

def get_documentation_and_links_from_repo(repo_url,version=None):
    if version is None:
        repo_name = os.path.basename(repo_url)  # os.path.basename 获取路径中的文件名部分
    else:
        repo_name = os.path.basename(repo_url) + "-" + version

    if repo_name not in os.listdir(TMP_PATH): # 查找 TMP_PATH 下所有文件夹
        if version is not None:
            print("begin repository clone with version")
            flag,readme_path = clone_repo(repo_url,version)
            if not flag:
                ValueError("Repository clone failed.")
            else:
                print(f"Repository cloned to {readme_path}")
        else:
            print("begin repository clone without version")
            flag,readme_path = clone_repo_not_version(repo_url)
            if not flag:
                ValueError("Repository without version clone failed.")
            else:
                print(f"Repository cloned to {readme_path}")

    readme_path = os.path.join(TMP_PATH, repo_name)
    if readme_path:
        print(f"Repository has already cloned to {readme_path}")
        flag,readme = search_readme_in_folder(readme_path)
    else:
        ValueError("README file not found in folder.")
    

    document_count, document_details = count_documents_from_folder(readme_path)
    link_count, links = count_documents_from_Readme(readme)

    doc_number = {
        "doc_number": document_count+link_count,
        "folder_document_details": document_details,
        "links_document_details": links
    }

    save_json(doc_number,os.path.join(DOC_NUM_PATH,f'{repo_name}_doc_num.json'))
    return doc_number


if __name__ == '__main__':
    print(get_documentation_and_links_from_repo('https://github.com/numpy/numpy'))
    