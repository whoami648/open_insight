import csv
from tqdm import tqdm
from . import FeatureExtract

if __name__ == "__main__":
    csv_path = "./src/feature_extract/filtered_ground_truth.csv"
    results = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
        for row in tqdm(reader, desc="处理仓库"):
            repo_url = row["id"]
            print(f"处理仓库: {repo_url}")
            feature_extract = FeatureExtract(repo_url)
            all_data = feature_extract.get_repo_all_mes()
            results.append({"repo_url": repo_url, "all_data": all_data})