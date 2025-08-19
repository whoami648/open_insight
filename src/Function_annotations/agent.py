import os
import json
from utils import read_json_file,chunk_text
from openai import OpenAI
import multiprocessing
from multiprocessing import Pool, cpu_count
from markdown_filter import MarkdownFilter
import shutil
from tqdm import tqdm
import configparser
config = configparser.ConfigParser()
config.read("config.ini") # 假设文件名为 config，但没有后缀

MODEL_NAME = config.get("DEFAULT", "model_name", fallback="")
BASE_URL = config.get("DEFAULT", "base_url", fallback="")
GITEE_AI_API_KEY = config.get("DEFAULT", "GITEE_AI_API_KEY", fallback="")

class Doc_agent:
    def __init__(self, path=r"document_data"):
        self.path = path
        self.doc = read_json_file(self.path)
        self.model_name = MODEL_NAME
        self.base_url = BASE_URL
        self.GITEE_AI_API_KEY = GITEE_AI_API_KEY

    def filter_documents(self):
        """Filter documents based on a keyword."""
        # doc_number = self.doc.get("doc_number", 0)
        folder_document_details = self.doc.get("folder_document_details", "")
        filtered_docs = ""
        for doc in folder_document_details:
            filtered_content = doc.get("content", "")

            # filtered_content = filter_content_by_keyword(document_content)
            filtered_content = "".join(filtered_content)
            filtered_docs += f"{filtered_content}"
        
        filtered_docs = filtered_docs.strip()
        if filtered_docs:
            filtered_docs = MarkdownFilter(filtered_docs).filter()['filtered_text']

        return filtered_docs


    def create_summary_prompt(self):
        """Create a prompt for summarizing the document."""

        prompt = f""" 

                你是一个专业的技f术信息抽取专家，擅长从技术文档中提取结构化信息。你的任务是从提供的技术文档中准确提取以下关键信息：接下来你将会收到一系列的开源项目的文档，你的任务是针对目标文档进行功能总结。要求最终输出功能注解的形式,采用一条一条的描述.
                 请注意，你需要提取文档中的关键信息，并以简洁明了的方式呈现。
                 你的处理方式有以下流程组成请提供一个简洁的总结，包含文档的主要观点和关键信息。

                1. **项目相关性描述**：
                - 项目的主要功能和技术定位
                - 解决的问题领域
                - 与其他技术/系统的关联性
                2. **技术栈**：
                - 核心框架和库
                - 基础设施/平台
                - 关键依赖项和基础设施依赖
                3.**应用场景**：
                - 主要应用场景
                - 适用的行业或领域
                4. **关键技术领域特征词汇**：
                -   关键词：提取文档中出现的8-12个关键技术领域特征词汇

                同时有以下要求：
                - 输出的内容需要是中文
                - 输出的内容需要是简洁明了的
                - 输出的内容需要是结构化的
                - 忽略文档中的广告、作者介绍、致谢等非技术内容  
                - 术语标准化：保留技术名词原生大小写（如“Spring Boot”而非“springboot”）
                - 仅提取文档中明确提及的客观信息，禁止主观推测或补充
                """
        return prompt

    def create_summary_schema(self):
        """Create a JSON schema for the summary."""
        scheama = {
            "guided_json": """{

                        "type": "object",

                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "项目的主要功能和技术定位， 解决的问题领域，与其他技术/系统的关联性，用4-5句话来描述"
                            },

                            "technology": {
                                "type": "string",
                                "description": "项目使用的技术栈包括核心框架和库，基础设施/平台，关键依赖项和基础设施依赖，用4-5句话来描述"
                            },

                            "scenarios": {
                                "type": "string",
                                "description": "主要应用场景，适用的行业或领域，相关技术领域，用4-5句话来描述"
                            }
                        },
                        "required": ["description", "technology", "scenarios"]
                }"""
        }


        return scheama


    def summarize_document(self):
        # 初始化
        doc = self.filter_documents()
        doc = chunk_text(doc, max_length=50000)
        prompt = self.create_summary_prompt()
        schema = self.create_summary_schema()
        content = ""    
        save_name_tmp = f"{os.path.dirname(self.path)}//output_tmp.txt"
        save_name = save_name_tmp.replace("_tmp.txt", ".txt")
        if os.path.exists(save_name):
            print(f"{save_name} already exists, skipping...")
            return prompt, schema

        # 遍历文档内容并生成注解
        for item in doc:
            item = item.strip()
            if not item:
                continue
            messages = [{"role": "system", "content": prompt}, {"role": "user", "content": item}]
            client = OpenAI(
                    base_url=self.base_url,
                    api_key=self.GITEE_AI_API_KEY,
            )

            response = client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                stream=True,
                max_tokens=1024,
                temperature=0.5,
                top_p=0.8,
                extra_body={"top_k": 20},
                frequency_penalty=1.1,
            )
            
            
            with open(save_name_tmp, "a+", encoding="utf-8") as f:
                for chunk in response:
                    if not chunk.choices or not chunk.choices[0].delta:
                        continue
                    # 检查是否有内容生成
                    if chunk.choices[0].delta.content:
                        f.write(chunk.choices[0].delta.content)
                        content += chunk.choices[0].delta.content
                    else:

                        continue


        # 生成总结
        content = content.strip()
        if not content:
            print("没有生成内容")
            return prompt, schema
        print(content)

        # 生成总结
        prompt = """
        你是一个专业的技术信息抽取专家，擅长从技术文档中提取结构化信息。请你针对下面的内容进行信息抽取,你的处理流程主要从以下三个方面出发：
        1. 首先从文档中提取下面的关键信息，并以简洁明了的方式呈现。同时另一方面，请你提取其中的可以进行领域判断的特征词汇（8-12个），并进行总结。
                1.**项目相关性描述**：
                - 项目的主要功能和技术定位
                - 解决的问题领域
                - 与其他技术/系统的关联性   
                2. **技术栈**：
                - 核心框架和库
                - 基础设施/平台
                - 关键依赖项和基础设施依赖
                3. **应用场景**：   
                - 主要应用场景
                - 适用的行业或领域
                - 相关技术领域  
        2. 其次，通过针对上面的提取到的信息内容进行整合处理。整合的格式如下：
        例：
        输入：
            1. **项目相关性描述**  
            - 主要功能：提供高性能的3D可视化与交互式        
            探索工具，用于处理大规模语义化三维城市模型及地理空间数据
            - 技术定位：基于Cesium Virtual Globe构建的网页端前端工具
            - 解决问题领域：支持复杂三维场景的数据展示、动态加载与
            多源数据集成分析
            - 关联系统：兼容CityGML标准格式；可集成Google
            Spreadsheets/PostgreSQL/OGC Feature API等外部主题数据源 
            2. **技术栈**  
            - 核心框架库：Cesium Virtual Globe（HTML5 + WebGL实现硬件加速）
            - 数据格式支持：KML/glTF/CZML/GeoJSON/Cesium 3D Tiles/I3S；
            WMS/WMTS影像层；OpenDRIVE/OGC CityGML
            - 基础设施依赖      
            ：PostgreSQL/PostgREST数据库；通过Docker镜像部署
            3. **应用场景**
            - 主要场景：城市三维模型展示（如Munich Buildings, Tokyo Bridges, NYC Solar Streets）及地形地貌叠加分析
            - 行业领域：智慧城市规划；地理信息系统（GIS）开发；建筑与交通仿真模拟
        输出：
        #### **1. 项目相关性描述**
            - **主要功能与定位**：提供高性能Web端3D地理空间可视化工具，支持大规模语义化三维城市模型（如CityGML）及多源地理空间数据（WMS/WMTS影像层）的展示与    分析；集成Cesium引擎实现跨平台高精度渲染与地形处理。
            - **解决的问题领域**：高效处理大体量三维模型动态加载/卸载需求；支持嵌入式主题数据查询及外部数据库联动（PostgreSQL/PostgREST）。
            - **关联系统**：基于WebGL兼容HTML5特性；整合Bing Maps/OpenStreetMap等第三方地图服务进行多视角导航与勘探分析；符合OGC CityGML标准并兼容Cesium 3D Tiles/I3S等格式规范
        #### **2. 技术栈**
            - **核心框架与库**：HTML5 + WebGL + Cesium Virtual Globe（三维可视化引擎） | jQuery | Flatpickr | OpenLayers | PostgREST API | Google Sheets API v4
            - **基础设施/平台**：WebGL硬件加速渲染 | HTTPS安全通信 | Docker容器化部署 | 跨平台运行（Windows/Linux/macOS/iOS/Android）
            - **依赖项**：KML/glTF分块数据集导出自3DCityDB | WMS/WMTS影像层服务接口 | PostgreSQL/PostgREST数据库连接
        #### **3. 应用场景**
            - **主要场景**：三维城市建模分析（建筑分布模拟）、交通仿真可视化（TUM Traffic Spaces    ）、多源地理空间数据融合展示
            - **适用行业或领域**：智慧城市管理｜建筑信息建模(BIM)｜地理信息系统(GIS)开发｜交通规划仿真
            - **关键技术领域**: 语义化GIS数据分析｜大规模三维模型渲染优化｜跨平台Web交互设计  
        ### **4. 技术分类特征词**
            - 关键词：Cesium Virtual Globe, WebGL, CityGML, 3D Tiles, I3S, PostgreSQL, WMS, WMTS, Docker, GIS, BIM, 3DCityDB, Google Sheets API, 3D可视化,  
        
        3. 最后，输出的内容需要是结构化的，忽略文档中的广告、作者介绍、致谢等非技术内容。
        术语标准化：保留技术名词原生大小写（如“Spring Boot”而非“springboot”）
        仅提取文档中明确提及的客观信息，禁止主观推测或补充。
        请注意，输出的内容需要是简洁明了的，且符合以下要求：
        - 术语标准化：保留技术名词原生大小写（如“Spring Boot”而非“springboot”）
        - 仅提取文档中明确提及的客观信息，禁止主观推测或补充
        -严格按照以下格式输出，不要生成总结内容只要和下面格式一样，确保格式正确，否则无法解析：
        例：
        输入：
            1. **项目相关性描述**  
            - 主要功能：提供高性能的3D可视化与交互式探索工具，用于处理大规模语义化三维城市模型及地理空间数据  
            - 技术定位：基于Cesium Virtual Globe构建的网页端前端工具  
            - 解决问题领域：支持复杂三维场景的数据展示、动态加载与多源数据集成分析  
            - 关联系统：兼容CityGML标准格式；可集成Google Spreadsheets/PostgreSQL/OGC Feature API等外部主题数据源  

            2. **技术栈**  
            - 核心框架库：Cesium Virtual Globe（HTML5 + WebGL实现硬件加速）  
            - 数据格式支持：KML/glTF/CZML/GeoJSON/Cesium 3D Tiles/I3S；WMS/WMTS影像层；OpenDRIVE/OGC CityGML  
            - 基础设施依赖：PostgreSQL/PostgREST数据库；通过Docker镜像部署  

            3. **应用场景**  
            - 主要场景：城市三维模型展示（如Munich Buildings, Tokyo Bridges, NYC Solar Streets）及地形地貌叠加分析  
            - 行业领域：智慧城市规划；地理信息系统（GIS）开发；建筑与交通仿真模拟  

        
        输出：
        #### **1. 项目相关性描述**  
            - **主要功能与定位**：提供高性能Web端3D地理空间可视化工具，支持大规模语义化三维城市模型（如CityGML）及多源地理空间数据（WMS/WMTS影像层）的展示与分析；集成Cesium引擎实现跨平台高精度渲染与地形处理。  
            - **解决的问题领域**：高效处理大体量三维模型动态加载/卸载需求；支持嵌入式主题数据查询及外部数据库联动（PostgreSQL/PostgREST）。  
            - **关联系统**：基于WebGL兼容HTML5特性；整合Bing Maps/OpenStreetMap等第三方地图服务进行多视角导航与勘探分析；符合OGC CityGML标准并兼容Cesium 3D Tiles/I3S等格式规范  

            #### **2. 技术栈**  
            - **核心框架与库**：HTML5 + WebGL + Cesium Virtual Globe（三维可视化引擎） | jQuery | Flatpickr | OpenLayers | PostgREST API | Google Sheets API v4  
            - **基础设施/平台**：WebGL硬件加速渲染 | HTTPS安全通信 | Docker容器化部署 | 跨平台运行（Windows/Linux/macOS/iOS/Android）  
            - **依赖项**：KML/glTF分块数据集导出自3DCityDB | WMS/WMTS影像层服务接口 | PostgreSQL/PostgREST数据库连接  

            #### **3. 应用场景**  
            - **主要场景**：三维城市建模分析（建筑分布模拟）、交通仿真可视化（TUM Traffic Spaces）、多源地理空间数据融合展示  
            - **适用行业或领域**：智慧城市管理｜建筑信息建模(BIM)｜地理信息系统(GIS)开发｜交通规划仿真  
            - **关键技术领域**: 语义化GIS数据分析｜大规模三维模型渲染优化｜跨平台Web交互设计

            #### **4. 技术分类特征词**
            - 关键词：Cesium Virtual Globe, WebGL, CityGML, 3D Tiles, I3S, PostgreSQL, WMS, WMTS, Docker, GIS, BIM, 3DCityDB, Google Sheets API, 3D可视化,
        """
        content = content.replace("\n", "")
        messages = [{"role": "system", "content": prompt}, {"role": "user", "content": content}]
        client = OpenAI(
                base_url=self.base_url,
                api_key=self.GITEE_AI_API_KEY,
        )

        response = client.chat.completions.create(
            messages=messages,
            model=self.model_name,
            stream=True,
            max_tokens=1024,
            temperature=0.5,
            top_p=0.8,
            extra_body={"top_k": 20},
            frequency_penalty=1.1,
        )
        
        
        with open(save_name, "a+", encoding="utf-8") as f:
            for chunk in response:
                if not chunk.choices or not chunk.choices[0].delta:
                    continue
                # 检查是否有内容生成
                if chunk.choices[0].delta.content:
                    f.write(chunk.choices[0].delta.content)
                    content += chunk.choices[0].delta.content
                else:

                    continue


        # 使用流式输出

        # llm = ChatOpenAI(
        #     model=self.model_name,
        #     api_key=self.GITEE_AI_API_KEY,
        #     base_url=self.base_url,
        #     streaming=True,
        #     temperature=0.5, 
        #     top_p=0.8,
        #     extra_body=schema,
        #     frequency_penalty=1.1,
        # )
        # content = ""

        # for response in llm.stream(prompt):
        #     if (response.content):
        #         content += response.content
        #         print(response.content, end="")
        # print("\n")
        # 保存结果
        print("生成的总结内容：", content)

        with open(save_name, "w+", encoding="utf-8") as f:
            f.write(content)

        return prompt, schema


def main():
    # Example usage
    # import time
    # start = time.time()
    path = r"/home/zyx/open_insight/Scripts/doc_extract/doc_data"
    # doc_agent = Doc_agent(path)
    # doc_agent.summarize_document()
    # print("总共用时:", time.time() - start)
    params = []
    for dir in os.listdir(path):
        full_path = os.path.join(path, dir)
        if not os.path.isdir(full_path):
            continue
        # params.append(full_path)
        for i in os.listdir(full_path):
            if i.endswith(".json"):
                params.append(os.path.join(full_path, i))

    cpu_count = multiprocessing.cpu_count()//2

    print(f"CPU核心数: {cpu_count}")

    # params = [(doc_agent, path) for path in params]
    # 多进程运行 Doc_agent.summarize_document，参数为 params
    # 需要为每个进程创建独立的 Doc_agent 实例，并传入不同的 path


    # 使用进程池并行处理
    import traceback
    with Pool(processes=cpu_count) as pool:
        try:
            print("开始多进程处理文档...")
            results = []
            for res in tqdm(pool.imap_unordered(run_summarize, params), total=len(params), desc="处理进度"):
                results.append(res)
        except Exception as e:
            print(f"Error occurred during multiprocessing: {e}")
            traceback.print_exc()
            

def run_summarize(path):
    # print(f"Processing document: {path}")
    agent = Doc_agent(path)
    return agent.summarize_document()
    

def qianyi():
    path = r"/home/zyx/open_insight/data2/document_data"
    new_path = r"/home/zyx/open_insight/Scripts/doc_extract/qxy_new.csv"
    data = {}
    import csv
    
    with open(new_path, "r", encoding="utf-8") as f:
       reader = csv.reader(f)
       for row in reader:
           name = row[0].split("_")[-1]
           data[name] = row[0]
    for name in data.keys():
        for dir in os.listdir(path):

            doc_name = "".join(dir.split("-")[:-1])
            if name == doc_name:
                src= os.path.join(path, dir)
                # json_path = os.path.join(full_path, "output.txt")
                dst = os.path.join(r"/home/zyx/open_insight/Scripts/doc_extract/doc_data", data[name])
                if not os.path.exists(dst):
                    os.mkdir(dst)
                shutil.copy(src, dst)


if __name__ == "__main__":
    main()

#    qianyi()
