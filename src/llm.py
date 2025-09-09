from openai import OpenAI
import pandas as pd
import os
from tqdm import tqdm
import configparser
import shutil
import logging
import json

# 全局变量
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.ini"), encoding="utf-8")
# src/llm.py
# 领域细分
DOMAIN = config.get('DEFAULT', 'domain', fallback=None)
FINE_GRAINED_FIELDS = config.get('DEFAULT', 'fine_grained_fields', fallback=None)
# 模型参数
MODEL_NAME = config.get('DEFAULT', 'model_name', fallback="Qwen3-8B")
OPENAI_API_KEY = config.get('OPEN_CHECKService', 'openai_api_key', fallback=None)
BASE_URL = config.get('OPEN_CHECKService', 'openai_api_url', fallback=None)

# 路径设置
TMP_PATH = config.get("GLOBAL_PATHS", "tmp_path", fallback="/tmp")
TPL_PATH = os.path.join(TMP_PATH, "tpl_data")  # TPL数据
FUNCTION_ANNOTATIONS_PATH = os.path.join(TMP_PATH, "function_annotations") # 功能注解
WORD_PARADIGM_GENERATION_PATH = os.path.join(TMP_PATH, "word_paradigm_generation") # 词范式生成

# 提示词
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.info(f"Using model: {MODEL_NAME}, API Key: {OPENAI_API_KEY}, Base URL: {BASE_URL}")




class LLMOpenInsight(OpenAI):
    """LLMOpenInsight类用于处理开源项目的细粒度技术领域判定。"""
    def __init__(self, repo_url):
        self.model = MODEL_NAME
        self.openai_api_key = OPENAI_API_KEY
        self.openai_api_url = BASE_URL
        self.domain = DOMAIN
        self.repo_url = repo_url


    def run(self, save_path, save_name_tmp):
        client = OpenAI(
                base_url= self.openai_api_url,
                api_key= self.openai_api_key,
        )
        content = ""

        item_chunks = self.prepare_input().replace("\n", "")
        # item_chunks = self.chunk_text(item_chunks, max_length=50000)

        # for item in tqdm(item_chunks):
        response = client.chat.completions.create(
        messages=[
            {
            "role": "system",
            "content": f"{self.get_prompts()} "
            },
            {
            "role": "user",
            "content": item_chunks
            }
        ],
            model=self.model,
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
                if chunk.choices and chunk.choices[0].delta.content:
                    # 如果有内容，写入文件ssssss
                    # print(chunk.choices[0].delta.content, end="", flush=True)
                    f.write(chunk.choices[0].delta.content)
                    content += chunk.choices[0].delta.content
                    print(chunk.choices[0].delta.content, end="", flush=True)
                    # f.write("\n")
                else:
                    # 如果没有内容，跳过写入
                    continue
        return content
  
        
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
    
    def prepare_input(self):
        word_paradigm_generation, function_annotations_content, tpl_content = self.process_LLM_feature_extract()
        item_chunks = f"""
        repo_url:{self.repo_url}, 宏领域技术领域：{word_paradigm_generation}。功能注解数据：{function_annotations_content} TPL数据：{tpl_content} 词范式生成数据：{word_paradigm_generation}
        """
        return item_chunks
    


    def get_prompts(self):
        prompts = f"""
        假如你是一位开源项目技术领域的专家，接下来会有一个任务，任务的目标是针对一个开源项目进行细粒度技术领域判定。在之前的任务中我们已经完成了{DOMAIN}技术领域的判别，接下来请你针对更细粒度方向的领域进行判别，
        给你的输入主要包括三个部分，分别是宏领域划分结果，功能注解数据和TPL数据。其中宏领域划分结果是利用LLM模型对开源项目进行宏领域划分的结果以及划分依据,同时还有部分特征词（注意其中可能因为数据不足，导致宏领域划分错误，
        你需要依靠功能注解和其他信息仔细甄别,如果错误请你将宏技术领域改为正确的），功能注解数据是对开源项目中的函数进行注解的结果其中包含了项目的功能描述等信息，TPL数据是对开源项目中的第三组件信息进行提取的结果。
        请你利用这些数据进行推理判断当前开源项目种更细粒度的技术领域。细粒度技术领域主要包括{FINE_GRAINED_FIELDS}，你可以根据这些领域进行判断。但是不局限于这些领域，你可以根据开源项目的实际情况进行判断。
        你需要输出当前开源项目的宏领域技术领域划分结果，细粒度技术领域划分结果以及判断依据。

        你可以采用下面4个步骤进行单步思考：
        1.首先对宏领域划分结果进行分析，判断当前开源项目的基础宏领域。
        2.然后对功能注解数据和TPL数据进行分析，判断当前开源项目的细粒度技术领域划分是否正确，同时根据功能注解的结果以及宏领域划分的结果提取其中的特征词，如果不正确请。给出正确的宏领域技术领域划分结果。宏领域只能是{DOMAIN}或者非{DOMAIN}
        3.之后针对细粒度技术领域划分，一个开源项目可以包括1-3个细粒度技术领域划分的结果，但最多不能超过三个，同时也不仅限制{FINE_GRAINED_FIELDS}这些细粒度领域，可以利用技术栈来多架构判别，最后输出当前开源项目的细粒度技术领域划分结果。
        4.最后输出当前开源项目的宏领域技术领域划分结果，细粒度技术领域划分结果以及判断依据。
        4.输出格式为“宏领域技术领域+细粒度技术分类+特征词+细粒度技术分类原因”，其中技术领域是一个具体的领域名称，原因是你判断该领域的依据。

        以下是案例：
        Example:

        输入：repo_url:https://github.com/01-ai/YiDong, 宏领域技术领域：AI技术领域，原因：该项目使用了很多AI相关的技术栈，如TensorFlow、PyTorch等。功能注解数据：该项目中有很多函数注解为AI相关的功能，如自然语言处理等。 TPL数据：该项目中有很多TPL数据，如TensorFlow、PyTorch等。

        输出：
        ### 宏领域技术领域：AI技术领域 
        ### 细粒度技术领域： 生成式人工智能 (AIGC)，自然语言处理 (NLP)
        ### 可能存在的其他领域：多模态处理 (MM)，计算机视觉 (CV)
        ### 特征词结果：生成式人工智能（AIGC）、多模态处理、API集成、SDK工具链、多媒体内容生成与编辑、HuggingFace Spaces 

        **详细判断逻辑**  
        1. **宏领域修正依据**  
        - 初始分类认为"未提及AI相关框架"而划为非AI域存在偏差：项目明确声明服务于"Yi系列多模态模型"（即大语言模型），且通过CLI/API调用预训练LLM完成多媒体内容生成编辑任务；其底层依赖Hugging Face Spaces平台（专为ML/AI部署设计），符合典型AIGC应用场景特征；  
        - TPL数据中包含`jsonargparse`/`pydantic`等配置管理组件说明其具备构建复杂参数化调用流程的能力——这是大规模参数化AIGC服务的标准架构特征  

        2. **细粒度分类推导过程**  
        - **生成式人工智能 (AIGC)**: 核心定位是作为"SDK工具链实现模型调用与资源管理"，直接服务于文本/图像/视频等内容创作自动化场景；项目文档明确指出解决"多媒体内容生成与编辑任务自动化执行"问题域  
        - **自然语言处理 (NLP)**: 虽未显式提及NLP算法实现细节，但基于LLM进行文本理解/创建必然涉及NLP核心技术栈（如tokenization/embedding）；同时需注意该分类涵盖更广义的语言智能应用场景  
        - **多模态处理 (MM)**: 由于项目明确支持图像/视频等非文本数据处理，故需将其纳入多模态应用范畴；此分类强调跨模态信息融合与处理能力

        

        """
        return prompts


    def process_LLM_feature_extract(self):
        
        # 进行特征提取
        logging.info("Starting LLM feature reading...")
        # 这里进行具体的特征提取操作
        # ...
        

        logging.info("Starting LLM feature extraction...")

        meta_name = f"{self.repo_url.replace('https://github.com/', '').replace('https://gitee.com/', '').replace('/', '_')}"
        meta_feature_path = os.path.join(WORD_PARADIGM_GENERATION_PATH, meta_name)


        if not os.path.exists(meta_feature_path):
            logging.error(f"Meta feature path does not exist: {meta_feature_path}, perhaps the feature extraction has not been run yet.")
            raise ValueError(f"Meta feature path does not exist: {self.repo_url},perhaps the feature extraction has not been run yet.")


        with open(os.path.join(meta_feature_path,"output.txt"), "r", encoding="utf-8") as f:
            word_paradigm_generation = f.read()
        
        logging.info("Read meta feature data successfully.")
        logging.info("************************************************************")
        # 读取功能注解数据
        logging.info("Starting function annotations reading...")

        # 获取功能路径
        function_annotations_name = self.repo_url.replace('https://github.com/', '').replace('https://gitee.com/', '').replace('/', '_')
        function_path = os.path.join(FUNCTION_ANNOTATIONS_PATH, function_annotations_name)

        if not os.path.exists(function_path):
            logging.error(f"Function path does not exist: {function_path}, perhaps the function annotations have not been run yet.")
            raise ValueError(f"Function path does not exist: {function_path}")
        
        with open(os.path.join(function_path, "output_tmp.txt"), "r", encoding="utf-8") as f:
            function_annotations_content = f.read()

            if not function_annotations_content:
                logging.error(f"Function annotations content is empty: {function_path}, perhaps the function annotations have not been run yet.")
                # raise ValueError(f"Function annotations content is empty: {function_path}")
                function_annotations_content = ""
        if len(function_annotations_content) > 30000:
            function_annotations_content = function_annotations_content[:30000]


        logging.info("Read function data successfully.")


        logging.info("************************************************************")

        
        logging.info("Feature extraction reading completed.")


        # 获取TPL数据
        logging.info("Starting TPL data reading...")

        tpl_name = self.repo_url.replace('https://github.com/', '').replace('https://gitee.com/', '_').replace('/', '_')
        tpl_path = os.path.join(TPL_PATH, tpl_name+".json")

        if not os.path.exists(tpl_path):
            logging.error(f"warning: TPL path does not exist: {tpl_path}, perhaps the TPL data has not been run yet.")
            # raise ValueError(f"TPL path does not exist: {tpl_path}, perhaps the TPL data has not been run yet.")
            tpl_content = ""
        else:

            tpl_content = ""

            with open(tpl_path, "r", encoding="utf-8") as f:
                tpl_content1 = json.load(f)

            for key,value in tpl_content1.items():
                if key == "dependencies":
                    for dep in value:
                        tpl_content = tpl_content + dep.get("name","") + "," + dep.get("description","") + "。"
                    

        # 检查TPL内容是否为空    
        if not tpl_content:
            logging.error(f"warning: TPL content is empty: {tpl_path}, perhaps the TPL data has not been run yet.")
            # raise ValueError(f"TPL content is empty: {tpl_path}, perhaps the TPL data has not been run yet.")
            tpl_content = ""
        logging.info("Read TPL data successfully.")

        return word_paradigm_generation, function_annotations_content, tpl_content


def main():
    # 示例用法
    repo_url_list  = os.listdir(r"data/function_annotations")
    solved = os.listdir(r"results")
    for repo_url in tqdm(repo_url_list):
        if repo_url+".txt" in solved:
            print(f"Repository {repo_url} already processed, skipping...")
            continue

        repo_url = repo_url.replace(".json", "")
        llm = LLMOpenInsight(repo_url)
        save_path = "./results"
        save_name_tmp = os.path.join(save_path, f"{repo_url}.txt")
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        llm.run(save_path=save_path, save_name_tmp=save_name_tmp)



if __name__ == "__main__":
    # 示例用法
    # repo_url = "https://github.com/bayesflow-org/bayesflow"
    # llm = LLMOpenInsight(repo_url)
    # llm.run(save_path="./results", save_name_tmp="./results/bayesflow.txt")
    main()
