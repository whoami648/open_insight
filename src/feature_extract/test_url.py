import csv
from tqdm import tqdm
from . import FeatureExtract

if __name__ == "__main__":
    repo_url = "https://gitee.com/deep-spark/deepsparkinference"
    feature_extract = FeatureExtract(repo_url)
    res = feature_extract.get_topics()
    print(res)