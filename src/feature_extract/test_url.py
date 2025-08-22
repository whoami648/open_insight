import csv
from tqdm import tqdm
from . import FeatureExtract

if __name__ == "__main__":
    repo_url = "https://github.com/numpy/numpy"
    feature_extract = FeatureExtract(repo_url)
    res = feature_extract.get_repo_all_mes()