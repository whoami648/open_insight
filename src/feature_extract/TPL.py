""""""
import requests
import os

from .utils import TPL_PATH, save_json

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
        case "Python":
            api_url = pypi_api_url
        case "Java":
            api_url = maven_api_url
        case "JavaScript":
            api_url = npm_api_url
        case _:
            print(f"Unsupported language: {language}")
            return {"error": f"Unsupported language: {language}"}

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

        save_json(res, os.path.join(TPL_PATH, f'{package_name}-{version}_dependencies.json'))
        return res

    except Exception as e:
        print(f"Error fetching dependencies for {package_name} version {version}: {e}")
        return {"error": f"Error fetching dependencies for {package_name} version {version}: {e}"}

def solve(repo_url, version, language):
    package_name = repo_url.split("/")[-1]
    if version is not None:
        version = version.replace("v", "")
    else:
        print("获得依赖必须指定版本号！")
        return {"error": "not get your version"}

    if language is None:
        print("获得依赖必须指定编程语言！")
        return {"error": "not get your language"}

    print(f"Fetching dependencies for {package_name} version {version}")
    return fetch_dependencies(package_name, version, language)
    

if __name__ == "__main__":
    repo_url = "https://github.com/numpy/numpy"
    version = "v2.3.2"
    language = "python"
    solve(repo_url, version, language)
