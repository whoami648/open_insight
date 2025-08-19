from openai import OpenAI
import pandas as pd
import os
from tqdm import tqdm
import configparser
import shutil
import logging


# 全局变量
config = configparser.ConfigParser()
config.read('config.ini')
OPENAI_API_KEY = config.get('OPEN_CHECKService', 'openai_api_key', fallback=None)
BASE_URL = config.get('OPEN_CHECKService', 'openai_api_url', fallback=None)
DOMAIN = config.get('DEFAULT', 'domain', fallback=None)
MODEL_NAME = config.get('DEFAULT', 'model_name', fallback="Qwen3-8B")
TMP_PATH = config.get("TMP_PATH", "tmp_path", fallback="/tmp")

FUNCTION_ANNOTATIONS_PATH = os.path.join(TMP_PATH, "function") # 功能注解
WORD_PARADIGM_GENERATION_PATH = os.path.join(TMP_PATH, "word_paradigm_generation") # 词范式生成

# 提示词
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

prompts = f"""
假如你是一位开源项目技术领域的专家，接下来会有一个任务，任务的目标是针对一个开源项目进行技术领域判定，给你的输入主要包括六个部分，分别是repo_list（仓库链接），release_data(当前项目版本的信息)，
commit_data提交信息，PR_data(pull request信息),topics项目主题信息，language（主语言信息），仓库名，仓库中的所有文件名称。

你可以采用下面两个步骤进行单步思考：
1.针对当前给定的六种输入进行特征。
2.首先根据不同的特征进行不同的处理方案，提取其中的特征范式，具体而言，可以将repo_list中的仓库链接提取为特征1，将release_data中的版本信息提取为特征2，将commit_data中的提交信息提取为特征3
，将PR_data中的pull request信息提取为特征4，将topics中的项目主题信息提取为特征5，将language中的主语言信息提取为特征6，将仓库名提取为特征7，将仓库中的所有文件名称提取为特征8。其中特征1，5，6，8
不需要在进行过滤.如果含有外部链接展示不做处理

3.根据特征进行推理，判断该项目的技术领域。
4.输出格式为“技术领域+原因”，其中技术领域是一个具体的领域名称，原因是你判断该领域的依据。


以下是案例：

Example:

例子1：repo_list:https://github.com/minoca/os，repo_name:minoca,repo_version:1.0.0, release_data:[], PR_data:[], commit_data:[], language:C, files:['kernel.c', 'fs.c', 'README.md']

输入：操作系统领域。原因是该项目是一个操作系统的开源项目，主要用于操作系统的开发和研究。该项目的代码主要使用C语言编写，包含多个重要的C语言文件，如kernel.c、fs.c等。

"""

class LLMOpenInsight(OpenAI):
    def __init__(self, repo_url):
        self.model = MODEL_NAME
        self.openai_api_key = OPENAI_API_KEY
        self.openai_api_url = BASE_URL
        self.domain = DOMAIN
        self.repo_url = repo_url
    def run(self, item_chunks, save_path):
        client = OpenAI(
                base_url= self.openai_api_url,
                api_key= self.openai_api_key,
        )
        content = ""
       

        for item in tqdm(item_chunks):
            response = client.chat.completions.create(
            messages=[
                {
                "role": "system",
                "content": f"{prompts} "
                },
                {
                "role": "user",
                "content": item
                }
            ],
                model="Qwen3-8B",
                stream=True,
                max_tokens=1024,
                temperature=0.3,
                top_p=0.8,
                extra_body={
            "top_k": 20,
            },
            frequency_penalty=1.1,
            )
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            # for chunk in response:
            for chunk in response:
                with open(save_name_tmp, "a+", encoding="utf-8") as f:
                    if chunk.choices[0].delta.content:
                        # 如果有内容，写入文件ssssss
                        # print(chunk.choices[0].delta.content, end="", flush=True)
                        f.write(chunk.choices[0].delta.content)
                        content += chunk.choices[0].delta.content+"\n"
                        # f.write("\n")
                    else:
                        # 如果没有内容，跳过写入
                        continue
  
        
    def chunk_text(text, max_length=50000):
        chunks = []
        while len(text) > max_length:
            split_pos = text.rfind(',', 0, max_length)
            if split_pos == -1:
                split_pos = max_length
            chunks.append(text[:split_pos])
            text = text[split_pos:]
        if text:
            chunks.append(text)
        return chunks
    


    def get_prompts(self):
        prompts = f"""
        假如你是一位开源项目技术领域的专家，接下来会有一个任务，任务的目标是针对一个开源项目进行技术领域判定，针对的主要目标是AI类项目，划分的类别请你集中在下面几个类别，在之前的判定种，我们已经利用参数
        """
        return prompts
    
    def get_feature_extract(self, input_text):
        """
        获取特征提取的结果
        Args:
            input_text (str): 输入文本，通常是开源项目链接。
        Returns:
            tuple: 包含技术领域分类结果、细分领域分类结果、词云图路径、关键词列表和功能注解的元组。
        """
        # 进行特征提取
        logging.info("Starting feature extraction...")
        # 这里进行具体的特征提取操作
        # ...

        save_name_tmp = os.path.join(save_path, "output.txt")
        if os.path.exists(save_name_tmp):
            os.remove(save_name_tmp)
        logging.info("Feature extraction completed.")

    def process_LLM_feature_extract(self, save_path):
        
        # LLMfeature
        if not os.path.exists(save_path):
            os.makedirs(save_path)


        # 进行特征提取
        logging.info("Starting LLM feature reading...")
        # 这里进行具体的特征提取操作
        # ...
        

        logging.info("Starting LLM feature extraction...")

        meta_name = f"{self.repo_url.replace('https://github.com/', '').replace('https://gitee.com/', '_').replace('/', '_')}"
        meta_feature_path = os.path.join(WORD_PARADIGM_GENERATION_PATH, meta_name)


        if not os.path.exists(meta_feature_path):
            logging.error(f"Meta feature path does not exist: {meta_feature_path}, perhaps the feature extraction has not been run yet.")
            raise ValueError(f"Meta feature path does not exist: {self.repo_url},perhaps the feature extraction has not been run yet.")


        with open(os.path.join(meta_feature_path,"output.txt"), "r", encoding="utf-8") as f:
            word_paradigm_generation = f.read()
        
        logging.info("Read meta feature data successfully.")

        # 获取功能路径


        function_annotations_name = self.repo_url.replace('https://github.com/', '').replace('https://gitee.com/', '_').replace('/', '_')
        function_path = os.path.join(FUNCTION_ANNOTATIONS_PATH, function_annotations_name)

        if not os.path.exists(function_path):
            logging.error(f"Function path does not exist: {function_path}, perhaps the function annotations have not been run yet.")
            raise ValueError(f"Function path does not exist: {function_path}")
        
        with open(os.path.join(function_path, "output_tmp.txt"), "r", encoding="utf-8") as f:
            function_annotations_content = f.read()



        logging.info("Read function data successfully.")



        logging.info("************************************************************")

        
        logging.info("Feature extraction reading completed.")
