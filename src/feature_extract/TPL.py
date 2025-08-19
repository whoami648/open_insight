""""""

import requests
import json
import sys  
import os
import csv
import ast
from tqdm import tqdm
def fetch_dependencies(package_name, version,language):
    """
    Fetch dependencies from deps.dev API and save to a JSON file.
    
    Args:
        url (str): The URL to fetch dependencies for.
    """
    pypi_api_url = f"https://deps.dev/_/s/pypi/p/{package_name}/v/{version}/dependencies"
    npm_api_url = f"https://deps.dev/_/s/npm/p/{package_name}/v/{version}/dependencies"
    maven_api_url = f"https://deps.dev/_/s/maven/p/{package_name}/v/{version}/dependencies"
    go_api_url = f"https://deps.dev/_/s/go/p/{package_name}/v/{version}/dependencies"
    c_api_url = f"https://deps.dev/_/s/c/p/{package_name}/v/{version}/dependencies"

    match language:
        case "python":
            api_url = pypi_api_url
        case "Java":
            api_url = maven_api_url
        case "JavaScript":
            api_url = npm_api_url
        case _:
            # print(f"Unsupported language: {language}")
            return
        
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for bad responses
        dependencies_data = response.json()["dependencies"]

        res = {
            "package_name": package_name,
            "version": version,
            "dependencies": [],
            "description": ""
        }

        for dependency in dependencies_data:
            ans = {}
            if dependency["package"]["name"] == package_name:
                res["description"] = dependency.get("description", "")
                continue

            ans["name"] = dependency["package"]["name"]
            ans["system"] = dependency["package"]["system"]
            ans["version"] = dependency["version"]
            ans["description"] = dependency.get("description", "")
            res["dependencies"].append(ans)

        save_name = os.path.join( f"{package_name}-{version}_dependencies.json")
        with open(save_name, 'w') as json_file:
            json.dump(res, json_file, indent=4)
        
        return True

        # # Save the data to a JSON file
        # output_file = "dependencies.json"
        # with open(output_file, 'w') as json_file:
        #     json.dump(dependencies_data, json_file, indent=4)
        
        # print(f"Dependencies for {package_name} version {version} saved to {output_file}")
        
    except:
        # print(f"Error fetching dependencies: {e}")
        with open("error_log.txt", "a") as error_file:
            error_file.write(f"Error fetching dependencies for {package_name} version {version}\n")
        
        return False
    
def solve():
    repo_csv =""

    with open(repo_csv, "r") as f:
        reader = csv.reader(f)
        for row in tqdm(reader):
            if row[0] == "repo":
                continue
            repo_url = row[0]
            version = ast.literal_eval(row[1])[0].replace("v", "")
            package_name = repo_url.split("/")[-1]
            language = ast.literal_eval(row[2])
            # print(f"Fetching dependencies for {package_name} version {version}")
            fetch_dependencies(package_name, version, language)

def solve1():
    repo_csv =""

    with open(repo_csv, "r") as f:
        reader = csv.reader(f)
        for row in tqdm(reader):
            if row[0] == "repo":
                continue
            repo_url = row[0]
            version_list = ast.literal_eval(row[1])#[0].replace("v", "")
            version_old = version_list[0].replace("v", "")
            package_name = repo_url.split("/")[-1]
            language = ast.literal_eval(row[2])
            # print(f"Fetching dependencies for {package_name} version {version}")
            if f"{package_name}-{version_old}_dependencies.json" in os.listdir(r"/home/yixiang/zyx1/Agent_test/opensource_insight/data/TPC"):
                continue
            for version in version_list:
                version = version.replace("v", "")
                # print(f"Fetching dependencies for {package_name} version {version}")
                flag = fetch_dependencies(package_name, version, language)
                if flag:
                    break

if __name__ == "__main__":
    # file_path = os.path.join(os.path.dirname(__file__), "dependencies.csv")
    # with open(file_path, 'r') as f:
    #     data = csv.reader(f)
    #     for row in data:
    #         if row[0] == "package_name":
    #             continue
    #         package_name = row[0]
    #         version = row[1]
    #         print(f"Fetching dependencies for {package_name} version {version}")
    #         fetch_dependencies(package_name, version)
    
    # fetch_dependencies()
    solve1()
