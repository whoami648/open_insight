import shutil
import os
import sys
import subprocess
import json
import argparse
import logging  
from feature_extract import FeatureExtract
logging.basicConfig(level=logging.INFO)

# Function to run a script in a subprocess
def feature_extract(repo_name, version):
    shutil.copyfile("config.ini", "src/feature_extract/document_metric/config.ini")
    logging.info(f"Extracting features for {repo_name} with version {version}")
    logging.info("***********************************************************")

    FeatureExtract_instance = FeatureExtract(repo_name, version)
    result = FeatureExtract_instance.run()
    logging.info("Feature extraction completed.")
    return result

def word_generate(repo_name, version):
    logging.info(f"Generating feature words for {repo_name} with version {version}")
    logging.info("***********************************************************")

    FeatureExtract_instance = FeatureExtract(repo_name, version)
    result = FeatureExtract_instance.run_word_generate()
    logging.info("Feature word generation completed.")
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
    output_dir = "output"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    print(f"Cleaned up {output_dir} directory.")

def main():
    parser = argparse.ArgumentParser(description="Run a script in a subprocess with repository name and version.")
    parser.add_argument("script_path", type=str, help="Path to the script to be executed.")
    parser.add_argument("repo_name", type=str, help="Name of the repository.")
    parser.add_argument("version", type=str, help="Version of the repositories.")
    
    args = parser.parse_args()
    
    # Convert repo_list from JSON string to Python list
    repo_list = json.loads(args.repo_list)
    
    # Clean up output directory
    clean()
    
    # Run the script
    output = run_script(args.script_path, repo_list, args.version)
    print(f"Script output: {output}")

if __name__ == "__main__":
    main()
