
import json
from typing import Any, Dict, List
import json
# from utils import get_Qwen_8b, read_json_file, save_json_file
from langchain_openai import ChatOpenAI
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import re
import os
import pandas as pd
ZILINGYU_ANS = {
    "01-ai_YiDong":"多媒体内容生成\nAI模型服务集成",
    "devzwy_open_nsfw_android":"AI应用开发​\n计算机视觉（CV）\n图像处理",
    "dice2o_BingGPT":"自然语言处理（NLP）\n对话式AI（Conversational AI）",
    "3dcitydb_3dcitydb-web-map":"非AI技术领域",
}
FEATURE_FILE_PATH = r"/home/zyx/open_insight/Qwen-8b-ans1"
FUNCTION_FILE_PATH = r"/home/zyx/open_insight/Scripts/doc_extract/test_data"
base_url = "https://ai.gitee.com/v1"
# https://ai.gitee.com/dashboard/settings/tokens 获取您的访问令牌
GITEE_AI_API_KEY = "LV41QCCDGLTQLUUUBAM8KXZKCQOS4ZTUTQDGH461"

def read_json_file(file_path: str) -> Dict[str, Any]:
    """Read a JSON file and return its content."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_json_file(file_path: str, data: Dict[str, Any]) -> None:
    """Save a dictionary to a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def chunk_text(text, max_length=50000):
    '''Split text into chunks of a specified maximum length, ensuring no chunk exceeds the limit.
    Args:
        text (str): The text to be split into chunks.
        max_length (int): The maximum length of each chunk.
    Returns:
        List[str]: A list of text chunks, each not exceeding the specified maximum length.'''
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


def get_Qwen_8b(messages):
    model_name = "Qwen3-8b"
    DOC_PATH = r"/home/zyx/open_insight/data2/document_data"

    llm = ChatOpenAI(model=model_name, api_key=GITEE_AI_API_KEY, base_url=base_url, streaming=True, temperature=0.1,
                    presence_penalty=1.05, top_p=0.9,
                    extra_body={
                        "guided_json": """{
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "用户的姓名"
                                },
                                "age": {
                                    "type": "integer",
                                    "description": "用户的年龄"
                                },
                                "city": {
                                    "type": "string",
                                    "description": "用户的城市"
                                }
                            },
                            "required": ["name", "city"]
                        }"""
                    })
    response = llm(messages)
    return response

def get_figure():
    from langchain_openai import ChatOpenAI

    model_name = "Qwen2.5-72B-Instruct"

    llm = ChatOpenAI(model=model_name, api_key=GITEE_AI_API_KEY, base_url=base_url, streaming=True, temperature=0.1,
                    presence_penalty=1.05, top_p=0.9,
                    extra_body={
                        "guided_json": """{
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "用户的姓名"
                                },
                                "age": {
                                    "type": "integer",
                                    "description": "用户的年龄"
                                },
                                "city": {
                                    "type": "string",
                                    "description": "用户的城市"
                                }
                            },
                            "required": ["name", "city"]
                        }"""
                    })

    prompt = [{"role": "system", "content": "你是聪明的助手，以 json 格式输出数据，如果无法判断年龄，则 age 为 0"},
            {"role": "user", "content": """
                在一个风和日丽的春日午后，小马走在了北京的街头。时间是 2023年的4月15日，
                正值樱花盛开的季节。作为一位热爱摄影的年轻人，他带着相机，希望能捕捉到这个季节最美的瞬间。
                北京的春天总是短暂而美丽，每一处公园、每一条街道都充满了生机与活力。
            """}]
    
    content = ""
    save_name_tmp = f"{os.path.dirname(__file__)}//output_tmp.json"

    for response in llm.stream(prompt):
        if (response.content):
            content += response.content

            print(response.content, end="")
    with open(save_name_tmp, "w+", encoding="utf-8") as f:
        f.write(content)

def parse_text_to_json(text):
        # 初始化结果字典
        result = {
            "技术领域分类结果": "",
            "所有特征词汇总": [],
            "分类逻辑说明": {},
            "特别关注点": [],
            "补充说明": ""
        }
        
        # 分割文本为不同部分
        sections = re.split(r'###', text.replace('\n', ''))
        if sections[0].strip() == "":
            sections.pop(0)  # 移除第一个空字符串部分
        
        # 解析第一部分：技术领域分类结果和特征词汇总
        part1 = sections[0].strip()
        match = re.search(r'技术领域分类结果[:：]?\s*(.*?)\s*(?:\n|$)', part1)
        if match:
            result["技术领域分类结果"] = match.group(1).strip()
        else:
            result["技术领域分类结果"] = ""
        
        # 提取特征词汇总
        part1 = sections[1].strip()
        features_section = re.search(r'所有特征词汇总\s*(.*?)\s*(?:\n|$)', part1)
        if features_section:
            features = re.findall(r'\d+\.\s+\*\*(.*?)\*\*', features_section.group(1))
            result["所有特征词汇总"] = features
        else:
            result["所有特征词汇总"] = []

        # 解析第二部分：分类逻辑说明
        part2 = sections[2].strip()
        logic_items = re.search(r'分类逻辑说明：(.*?)(?=\n-|\Z)', part2, re.DOTALL)
        if logic_items:
            result["分类逻辑说明"] = logic_items.group(1).strip().replace('；', '')
        else:
            result["分类逻辑说明"] = ""

        # # 解析第三部分：特别关注点
        # part3 = sections[3].strip()
        # focus_points = re.findall(r'- (.*?)(?=\n-|\Z)', part3, re.DOTALL)
        # result["特别关注点"] = [point.strip().replace('；', '') for point in focus_points]
        
        # # 解析第四部分：补充说明
        # part4 = sections[4].strip()
        # result["补充说明"] = part4.replace('（注：', '注：').replace('）', '')  # 清理括号
        
        return result


def get_decision_feature():
    # 输入文本
    input_text = """
    ### 技术领域分类结果：非AI技术领域  
    #### 所有特征词汇总（去重后）：  
    1. **Android应用开发**  
    2. **Java语言**  
    3. **MainActivity.java**  
    4. **ActionPanelController.java**  
    5. **FreezeController.java**  
    6. **XML布局文件**  
    7. **资源文件**  

    ---

    ### 分类逻辑说明：  
    - **核心框架/平台**：基于 `Android` 开发平台构建应用程序；  
    - **编程语言**：主要使用 `Java` 作为实现语言；  
    - **关键组件/模块**：包含典型 Android 应用结构中的核心类（如 `MainActivity` 作为主界面入口、`ActionPanelController` 和 `FreezeController` 作为功能模块控制器）；  
    - **界面与交互设计**：涉及大量 `XML布局文件` 和 `资源文件` 的设计与优化；  

    ---

    ### 特别关注点：  
    - 典型 Android 应用架构特性：Activity 控制器 + 布局定义 + 资源管理；  
    - 非 AI 相关功能聚焦于相机模式切换与界面交互优化；  

    --- 

    ### 补充说明：
    该领域的核心技术栈围绕 Android SDK 的 API 使用展开（如 Camera API、UI 组件），而非依赖 AI 框架或算法模型。（注：若存在其他潜在关联性需进一步分析）
    """

    # 转换为JSON
    parsed_data = parse_text_to_json(input_text)
    json_output = json.dumps(parsed_data, ensure_ascii=False, indent=2)

    # 打印结果
    print(json_output)

    # 可选：保存到文件
    with open("tech_domain_classification.json", "w", encoding="utf-8") as f:
        f.write(json_output)

def hong_division_precision_recall():
    """根据关键词过滤内容"""
    src_path = r"/home/zyx/open_insight/Qwen-8b-ans1"
    ground_truth = {}
    test = {}
    keywords = ["ai", "langraph", "gpt", "llm", "chat", "openai","agent","qwen","bert","transformer","tensorflow","mindspore-lab","paddlepaddle_","llama","gemini","nlp","textclassifier","torch"]
    for i in os.listdir(src_path):

        try:
            # if "PaddlePaddle" in i:
            #     ground_truth[i] = "yes"

            # ground_truth[i] = "no"

            # for keyword in keywords:
            #     if keyword in i.lower():
            #         ground_truth[i] = "yes"


            file_path = os.path.join(src_path, i)
            file_path = os.path.join(file_path, "output.txt")
            with open(file_path, "r", encoding="utf-8") as f:
                feature_content = f.read()
                parsed_data = parse_text_to_json(feature_content)
                domain_output = parsed_data.get("技术领域分类结果", "")
                if "AI" in domain_output and "非 AI" not in domain_output and "非AI" not in domain_output:
                    test[i] = "yes"
                else:
                    test[i] = "no"
        except Exception as e:
            print(f"Error processing {i}: {e}")
            continue


    # ground_truth1 = {}
    df1 = pd.read_csv(r"qxy_zyx.csv",header=None)
    for index, row in df1.iterrows():
        # print(row)
        if "用户" in row[0]:
            continue
        ground_truth[row[0]] = row[1]



    ground_truth["FlagOpen_FlagPerf"] = "yes"
    ground_truth["EdisonLeeeee_GraphGallery"] = "yes"
    ground_truth["TideDra_lmm-r1"] = "yes"
    ground_truth["amazon-science_fmcore"] = "yes"
    ground_truth["jeffffffli_HybrIK"] = "yes"
    ground_truth["APIJSON_apijson-milvus"] = "yes"
    ground_truth["scikit-learn-contrib_imbalanced-learn"]  = "yes"
    ground_truth["fake-useragent_fake-useragent"] = "no"
    # ground_truth["aleju_imgaug"] = "no"
    ground_truth["langchain-ai_langchain"] = "yes"
    ground_truth["facebook_rebound"] = "no"
    ground_truth["oddfar_campus-imaotai"] = "no"
    # print(ground_truth["aleju_imgaug"])

    #ground_truth的value和test的value进行比较，不同存储到csv，只存储分类不一致的
    # 创建DataFrame
    # 只保留分类不一致的行
    test1 = {key: value for key, value in test.items() if key in ground_truth}
    ground_truth1 = {key: value for key, value in ground_truth.items() if key in test}
    # df = pd.DataFrame(list(test1.items()), columns=['项目名称', '预测分类'])
    # df['实际分类'] = df['项目名称'].map(ground_truth)
    # df = df[df['预测分类'] != df['实际分类']]  # 只保留分类不一致的行
    # # 保存到CSV文件
    # df.to_csv("分类结果1.csv", index=False)

    precision = sum(1 for key in test1 if test1[key] == ground_truth1[key]) / len(test1) if test1 else 0
    recall = sum(1 for key in test1 if test1[key] == ground_truth1[key]) / len(ground_truth1) if ground_truth1 else 0
    print(f"Precision: {precision:.2f}, Recall: {recall:.2f}")
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    print(f"F1 Score: {f1:.2f}")
    df = pd.DataFrame(list(test1.items()), columns=['项目名称', '预测分类'])
    df['实际分类'] = df['项目名称'].map(ground_truth1)
    df = df[df['预测分类'] != df['实际分类']]  # 只保留分类不一致的行
    # 保存到CSV文件
    df.to_csv("分类结果123.csv", index=False)




    

    




    df = pd.DataFrame(list(ground_truth.items()), columns=['项目名称', '实际分类'])
    df['预测分类'] = df['项目名称'].map(test)
    df.to_csv("分类结果.csv", index=False)

    
   

           


        

    return ground_truth


if __name__ == "__main__":
    # get_decision_feature()
    # # Example usage
    # content = ""
    # #  filter_content_by_keyword(content: str)
    # a,b = filter_content_by_keyword(content)
    # with open("sample_content.txt", "w+") as file:
    #     file.write(str(a)+"\n\n" + str(b))
    # print()  # Print the response from the model
    # get_figure()
    # with open("output_tmp.json", "r", encoding="utf-8") as f:
    #     content = json.load(f)
    # # print(content)
    # import matplotlib.font_manager as fm
    # # 搜索所有支持中文的字体
    # for font in fm.findSystemFonts():
    #     if "wqy" in font or "Noto" in font:  # 文泉驿/Noto字体
    #         print(font)  # 输出可用路径

    hong_division_precision_recall()