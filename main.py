import shutil
import os
import sys
import subprocess
import json
import argparse
import logging  
from src.feature_extract import FeatureExtract
from src.Feature_word_paradigm_generation import FeatureWordParadigm
from src.Function_annotations import Doc_agent
from src.llm import LLMOpenInsight
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
TMP_PATH = config.get('GLOBAL_PATHS', 'tmp_path', fallback='tmp')
if not os.path.exists(TMP_PATH):    
    os.makedirs(TMP_PATH)


# Function to run a script in a subprocess
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
def feature_extract(repo_name, version):
    # shutil.copyfile("config.ini", "src/feature_extract/document_metric/config.ini")
    logging.info(f"Extracting features for {repo_name} with version {version}")
    logging.info("***********************************************************")

    FeatureExtract_instance = FeatureExtract(repo_name, version)
    result = FeatureExtract_instance.get_repo_all_mes()
    # logging.info(f"Feature extraction result: {result}")
    logging.info(f"Feature extraction completed. Ans has been saved to the {TMP_PATH} directory.")
    return result

def word_generate(repo_name, version):
    logging.info(f"Generating feature words for {repo_name} with version {version}")
    logging.info("***********************************************************")

    FeatureExtract_instance = FeatureWordParadigm(repo_name, version)
    result = FeatureExtract_instance.run()
    logging.info("Feature word generation completed.")
    return result

def function_annotations(repo_name, version):
    logging.info(f"Annotating functions for {repo_name} with version {version}")
    logging.info("***********************************************************")
    function_annotations_path = os.path.join(TMP_PATH,"doc")
    repo_url = repo_name
    
    repo_name = f"{repo_name.replace('https://github.com/', '').replace('http://gitee.com/', '').replace('.git', '').replace('/', '_')}"
    if version is not None:
        doc_path = os.path.join(function_annotations_path, repo_name+"-"+version+"_doc_num.json")
    else:
        doc_path = os.path.join(function_annotations_path, repo_name+"_doc_num.json")
    if not os.path.exists(doc_path):
        logging.error(f"Document path {doc_path} does not exist. Please ensure the document data is available.")
        return None
    result = Doc_agent(doc_path, repo_name,repo_url,version).summarize_document()
    logging.info("Function annotation completed.")
    return result

def run_script(script_path, repo_list, version):
    """Run the script in a subprocess."""
    try:
        result = subprocess.run(
            ["python", script_path, json.dumps(repo_list), version],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logging.error(f"Script failed with error: {result.stderr}")
            return None
        logging.info(f"Script output: {result.stdout}")
        return result.stdout
    except Exception as e:
        logging.error(f"An error occurred while running the script: {e}")
        return None


def clean():
    """Clean up the output directory."""
    doc_path = os.path.join(TMP_PATH,"doc")
    filenames_path = os.path.join(TMP_PATH,"filenames")
    topics_path = os.path.join(TMP_PATH,"topics")
    tpl_path = os.path.join(TMP_PATH,"tpl")
    metadata_path = os.path.join(TMP_PATH,"metadata")

    if os.path.exists(doc_path):
        shutil.rmtree(doc_path)
        print(f"Cleaned up {doc_path} directory.")
    if os.path.exists(filenames_path):
        shutil.rmtree(filenames_path)
        print(f"Cleaned up {filenames_path} directory.")
    if os.path.exists(topics_path):
        shutil.rmtree(topics_path)
        print(f"Cleaned up {topics_path} directory.")
    if os.path.exists(tpl_path):
        shutil.rmtree(tpl_path)
        print(f"Cleaned up {tpl_path} directory.")
    if os.path.exists(metadata_path):
        shutil.rmtree(metadata_path)
        print(f"Cleaned up {metadata_path} directory.")

    # 其他清理操作
def generate_open_insight_prompt(repo_url,version=None):
    llm = LLMOpenInsight(repo_url)
    save_path = "./results"
    save_name = repo_url.replace('https://github.com/', '').replace('http://gitee.com/', '').replace('.git', '').replace('/', '_')
    save_name_tmp = os.path.join(save_path, f"{save_name}.txt")
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    res = llm.run(save_path=save_path, save_name_tmp=save_name_tmp)
    return res

def main(repo_name, version=None):
    # parser = argparse.ArgumentParser(description="Run LLMOpenInsight with repository name and version.")
    # parser.add_argument("repo_name", type=str, help="Name of the repository.")
    # parser.add_argument("version", type=str, nargs='?', default=None, help="Version of the repository. (optional, default is empty string)")

    # args = parser.parse_args()

    # data/repos_tmp/agentops-1.2
    class Args:
        def __init__(self, repo_name, version):
            self.repo_name = repo_name
            self.version = version
    # args = Args("https://github.com/AgentOps-AI/agentops", "0.4.13")
    args = Args(repo_name, version)

    logging.info(f"Running domain for repository: {args.repo_name} with version: {args.version}")

    logging.info("Starting feature extraction...")

    feature = feature_extract(args.repo_name, args.version)

    logging.info("Feature extraction completed.")
    logging.info("***********************************************************")

    if args.repo_name.replace('https://github.com/', '').replace('http://gitee.com/', '').replace('.git', '').replace('/', '_') in os.listdir("data/word_paradigm_generation"):
        logging.info(f"Repository {args.repo_name} has already been processed.")
    else:

        logging.info("Starting feature word generation...")
        word = word_generate(args.repo_name, args.version)
        if word is None:
            logging.error("ERROR: Feature word generation failed due to missing document data.Maybe generate wrong ans.")
            # return
        logging.info(f"Feature word generation result: \n{word}")
        logging.info("Feature word generation completed.")
        logging.info("******************************")


    logging.info("Starting function annotations...")
    function = function_annotations(args.repo_name, args.version)
    if function is None:
        logging.error("ERROR: Function annotations failed due to missing document data.Maybe generate wrong ans.")
        # return
    logging.info(f"Function annotations result: \n{function}")
    logging.info("Function annotations completed.")
    logging.info("***********************************************************")


    logging.info("Starting domain OpenInsight ...")
    domain_res = generate_open_insight_prompt(args.repo_name, args.version)
    logging.info("Domain OpenInsight completed.")
    logging.info("***********************************************************")

    # 开始清理tmp
    if len(os.listdir(os.path.join(TMP_PATH,"doc")))>100:
        logging.info("Starting cleanup...")
        clean()
        logging.info("Cleanup completed.")
        logging.info("All tasks completed successfully.")
    
    #重新新建中间文件
    logging.info("Recreate intermediate directories...")
    if not os.path.exists(os.path.join(TMP_PATH,"doc")):
        os.makedirs(os.path.join(TMP_PATH,"doc"))
    if not os.path.exists(os.path.join(TMP_PATH,"filenames")):
        os.makedirs(os.path.join(TMP_PATH,"filenames"))
    if not os.path.exists(os.path.join(TMP_PATH,"topics")):
        os.makedirs(os.path.join(TMP_PATH,"topics"))
    if not os.path.exists(os.path.join(TMP_PATH,"tpl")):
        os.makedirs(os.path.join(TMP_PATH,"tpl"))
    if not os.path.exists(os.path.join(TMP_PATH,"metadata")):
        os.makedirs(os.path.join(TMP_PATH,"metadata"))
    logging.info("Intermediate directories recreated.")
    logging.info("All tasks completed successfully.")

if __name__ == "__main__":
    import time
    start_time = time.time()
    # 新增参数解析
    if len(sys.argv) < 2:
        print("用法: python main.py <repo_name> [version]")
        sys.exit(1)
    repo_url = sys.argv[1]
    version = sys.argv[2] if len(sys.argv) > 2 else None
    main(repo_url, version)
    end_time = time.time()
    logging.info(f"Total time taken: {end_time - start_time} seconds")