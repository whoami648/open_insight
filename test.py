from main import main
from tqdm import tqdm
import os
# def feature_extract(repo_name, version):
#     FeatureExtract_instance = FeatureExtract(repo_name, version)
#     result = FeatureExtract_instance.get_repo_all_mes()
#     return result

# if __name__ == "__main__":
#     feature_extract("https://github.com/numpy/numpy","v2.3.2")

def solve():
    
    saved_path = "results"
    solved = [i.replace(".txt","") for i in os.listdir(saved_path) if i.endswith(".txt")]
    with open("rust.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            try:
                repo_info = line.strip().split(",")
                
                repo_info = line.strip().split(",")
                if len(repo_info) == 2:
                    repo_name, version = repo_info
                elif len(repo_info) == 1:   
                    repo_name = repo_info[0]
                    version = None
                else:
                    print(f"Invalid line format: {line}")
                    continue
                if repo_name.replace('https://github.com/', '').replace('https://gitee.com/', '').replace('.git', '').replace('/', '_') in solved:
                    print(f"Repository {repo_name} has already been processed.")
                    continue
                print(f"Processing repository: {repo_name} with version: {version}")

                main(repo_name, version)
            except Exception as e:
                print(f"Error processing line: {line}. Error: {e}")
                continue
if __name__ == "__main__":
    solve()
