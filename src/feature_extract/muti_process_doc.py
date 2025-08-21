from document_metric import Industry_Support

"""多进程处理开源项目文档的类"""
class muti_process_doc:
    def __init__(self, repo_url, version):
        self.repo_url = repo_url
        self.versions = version
    def run(self):
        """
        执行多进程处理文档的函数
        :return: 返回处理后的数据
        """
        return self.process_repo(self.repo_url, self.version)

    def process_repo(self, repo, version):
        """
        处理单个仓库的文档
        :repo: 仓库地址
        :version: 版本号
        :return: 处理后的数据
        """
        print(f"Processing version: {version} for repository: {repo}")

        try:
            dm = Industry_Support(123, [repo], version)
        except Exception as e:
            print(f"Error occurred while processing {repo} version {version}: {e}")
            pass
        
        return dm.get_doc_number()

def solve(repo_url, version):
    dm = muti_process_doc(repo_url, version).run()

if __name__ == "__main__":
    repo_url = "https://github.com/example/repo"
    version = "v1.0"
    solve(repo_url, version)