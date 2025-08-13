
'''
# nohup python /home/zyx/open_insight/Scripts/llm_extract/test.py > /home/zyx/open_insight/Scripts/llm_extract/feature.log 2>&1 &
[1] 831535

'''
from openai import OpenAI
import pandas as pd
import os
from tqdm import tqdm
import sys
from multiprocessing import Pool
import multiprocessing

SAVE_PATH = r"/home/zyx/open_insight/Qwen-8b-ans1"
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

def chunk_text(text, max_length=100000):
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


def load_data():
    """
    Load the data from CSV files.
    
    Returns:
        pd.DataFrame: DataFrame containing the loaded data.
    """


    filter_data = pd.read_csv(r"/home/zyx/open_insight/data/file_data_after_filter.csv")
    github_meadata = pd.read_csv(r"/home/zyx/open_insight/data/github_metadata.csv")
    filter_dict = dict(zip(filter_data.iloc[:, 0], filter_data.iloc[:, 1]))
    def df_to_dict(df):
        result = {}
        for _, row in df.iterrows():
            key = row.iloc[0]
            value = []
            for col, val in zip(df.columns[1:], row.iloc[1:]):
                value.append(f"{col}:{val}")
            result[key] = ", ".join(value)
        return result

    github_meadata_dict = df_to_dict(github_meadata)
    # list(github_meadata_dict.items())[:10]
    topics = pd.read_csv(r"/home/zyx/open_insight/data/topics.csv")
    topics_dict = dict(zip(topics.iloc[:, 0], topics.iloc[:, 1]))
    # # 测试
    # repo_name = 'https://github.com/Arthur151/ROMP'
    # item = f"请你判断提取一下这个输入，repo_name:{repo_name}"+f"{github_meadata_dict.get(repo_name, '')}"+f",topics:{topics_dict.get(repo_name, '')}"+f",files:{filter_dict.get(os.path.basename(repo_name), '')}"
    # item_chunks = chunk_text(item)
    # # item_list.append(item_chunks)
    # save_name = f"/home/zyx/open_insight/Qwen-8b-ans1/{repo_name.replace('https://github.com/', '').replace('/', '_')}"
    # process_LLM_feature_extract(item_chunks,save_path=save_name)

    
    item_list = []
    save_name_list = []
   

    # save_name_list.append(save_name)
    

    for repo_name in tqdm(github_meadata_dict.keys()):
       
        item = f"请你判断提取一下这个输入，repo_name:{repo_name}"+f"{github_meadata_dict.get(repo_name, '')}"+f",topics:{topics_dict.get(repo_name, '')}"+f",files:{filter_dict.get(os.path.basename(repo_name), '')}"
        item_chunks = chunk_text(item)
        item_list.append(item_chunks)
        save_name = f"/home/zyx/open_insight/Qwen-8b-ans1/{repo_name.replace('https://github.com/', '').replace('/', '_')}"

        save_name_list.append(save_name)



    params = list(zip(item_list, save_name_list))

    # 获取 CPU 核心数（自动适配）
    cpu_count = multiprocessing.cpu_count()//2

    # 创建进程池
    with multiprocessing.Pool(processes=cpu_count) as pool:
        # 使用 starmap 传递多个参数[1,6](@ref)
        try:
            results = pool.starmap(process_LLM_feature_extract, params)
            with open(os.path.join(SAVE_PATH, "/home/zyx/open_insight/result.txt"), "w", encoding="utf-8") as f:
                for result in results:
                    f.write("\n".join(result) + "\n")
        except Exception as e:
            print(f"Error occurred during multiprocessing: {e}")
            results = []
            # pass

    return item_chunks



def process_LLM_feature_extract(item_chunks,save_path=r"/home/zyx/open_insight/output_pytorch_50.txt"):
    # if not os.path.exists(save_path):
    #     pass
    # else:
    #     return
    prompts = f"""假如你是一位开源项目技术领域的专家，接下来会有一个任务，任务的目标是针对一个开源项目的提交记录进行与技术领域分类有关的内容，提取成特征词范式的形式.同时判断是否为Ai项目。
                    注意：请不要输出问题，只给出问题的答案！！！！

                    同时请你进行提取的步骤如下：
                    1. 你需要分析开源项目的提交记录内容，提取出与技术领域相关的特征词。
                    2. 输入主要包括八大类，分别是：release_data中的版本信息提取为特征2，将commit_data中的提交信息提取为特征3，将PR_data中的pull request信息提取为特征4，将topics中的项目主题信息提取为特征5，
                       将language中的主语言信息提取为特征6，将仓库名提取为特征7，将仓库中的所有文件名称提取为特征8。对于
                    3. 因为输入可能超长，所以需要将输入分块处理，每个块的长度不超过100000个字符。
                    4. 特征词应该是与开源项目的技术领域相关的关键词或短语，尽量简洁明了。
                    5. 输出的特征词应该是一个列表，每个特征词占一行。

                    例如：


                    例子1：
                    
                    输入：repo_list:https://github.com/minoca/os，repo_name:minoca,repo_version:1.0.0, release_data:[下一代操作系统], PR_data:[], commit_data:[提交了C代码], language:C, files:['kernel.c', 'fs.c']
                    输出：### 输入分析
                        **1. 仓库链接和名称**：
                        - `repo_list: https://github.com/3dcitydb/3dcitydb-web-map`
                        - `repo_name: 3dcitydb-web-map`
                        - `version: v2.0.0`

                        这表明这是一个名为 `3dcitydb-web-map` 的项目，托管在 GitHub 上，当前版本为 v2.0.0。

                        **2. 版本信息（release_data）**：
                        - 包含了新功能的介绍，如支持 i3s 和 GeoJSON 图层，支持 OGC Feature API，支持 WMTS 作为影像或底图层等。
                        - 提到支持多种 3D 图层类型（KML/COLLADA/glTF、Cesium 3D Tiles）以及从 PostgreSQL/PostgREST 和 Google Spreadsheets 提取主题数据。
                        - 说明该项目是一个 Web 地图工具，用于处理和展示城市三维模型和地理数据。

                        **3. 提交信息（commit_data）**：
                        - 提交信息为空，没有具体的提交记录。

                        **4. PR 数据（PR_data）**：
                        - 提到了一些 PR 的标题，如“Layers don't follow when export view”、“Replaced removed loading functions with Cesium.Resource (Required for Cesium1.44)”等。
                        - 这些 PR 涉及功能改进和依赖库（如 Cesium）的更新。

                        **5. 项目主题（topics）**：
                        - 包括：`3d-city-model`, `cesiumjs`, `citygml`, `database`, `web-based-visualization`
                        - 项目主题明确指向三维城市模型、CesiumJS（一个用于 3D 地图的 JavaScript 库）、CityGML（城市地理标记语言）、数据库和基于 Web 的可视化。

                        **6. 语言（language）**：
                        - 主要语言为 JavaScript，这表明这是一个 Web 应用程序，可能与前端交互和地图可视化相关。

                        **7. 文件列表（files）**：
                        - 包含许多 `.kmz`、`.json`、`.js`、`.css` 等文件，如 `NYC_Manhattan_Lots_Tile_..._footprint.kmz`、`GMLID_..._gltf`、`createVectorTileGeometries.js`、`Cesium3DTilesInspector.js`、`viewerCesiumNavigationMixin.min.js` 等。
                        - 这些文件涉及地图瓦片、三维模型、CesiumJS 库的使用、以及数据库查询和地理数据可视化。

                        ### 特征分析

                        从以上信息中可以提取出以下特征：

                        - **项目主题**：3D 城市模型、CesiumJS、CityGML、数据库、Web 可视化。
                        - **版本信息**：新增了多种地图图层支持（如 i3s、GeoJSON、WMTS），以及对 OGC Feature API 的支持。
                        - **文件内容**：包含大量的三维地图文件（KML、GeoJSON、glTF）、CesiumJS 相关的 JS 文件、数据库查询和处理文件（PostgreSQL/PostgREST）、地图瓦片处理文件等。
                        - **语言**：JavaScript，用于 Web 地图工具开发。

                        ### 领域判断

                        从这些特征来看，这个项目主要围绕 **地理信息系统（GIS）** 展开，尤其是基于 Web 的三维地理数据可视化。它支持多种地图图层、三维模型格式（如 Cesium 3D Tiles、glTF、CityGML）、数据库（PostgreSQL、PostgREST、Google Spreadsheets）集成、以及 Web 可视化。

                        因此，该项目属于 **地理信息系统（GIS）领域**。

                        ---

                        ### 最终结论

                        **输出**:非AI技术领域。地理信息系统（GIS）领域。
                        **原因**：该项目是一个基于 Web 的地理信息系统（GIS）工具，主要用于处理和可视化城市三维模型和地理数据。该项目的代码主要使用 JavaScript 编写，并且包含多个与地图、地理数据、三维可视化相关的文件，如 KML、GeoJSON、Cesium 3D Tiles 等



                    例子2：
                    输入：repo_list:https://github.com/pytorch/pytorch,repo_name:pytorch,repo_version:1.0.0, release_data:\'This release is meant to fix the following issues (regressions / silent correctness):\\r\\n- RuntimeError by torch.nn.modules.activation.MultiheadAttention with bias=False and batch_first=True #88669\\r\\n- Installation via pip  on Amazon Linux 2, regression #88869\\r\\n- Installation using poetry on Mac M1, failure #88049\\r\\n- Missing masked tensor documentation #89734\\r\\n- torch.jit.annotations.parse_type_line is not safe (command injection) #88868\\r\\n- Use the Python frame safely in _pythonCallstack #88993\\r\\n- Double-backward with full_backward_hook causes RuntimeError #88312\\r\\n- Fix logical error in get_default_qat_qconfig #88876\\r\\n- Fix cuda/cpu check on NoneType and unit test #88854 and #88970\\r\\n- Onnx ATen Fallback for BUILD_CAFFE2=0 for ONNX-only ops #88504\\r\\n- Onnx operator_export_type on the new registry #87735\\r\\n- torchrun AttributeError caused by file_based_local_timer on Windows #85427\\r\\n\\r\\nThe [release tracker](https://github.com/pytorch/pytorch/issues/89855) should contain all relevant pull requests related to this release as well as links to related issues\\r\\n\', \'This release is meant to fix the following issues (regressions / silent correctness):\\r\\n- RuntimeError by torch.nn.modules.activation.MultiheadAttention with bias=False and batch_first=True #88669\\r\\n- Installation via pip  on Amazon Linux 2, regression #88869\\r\\n- Installation using poetry on Mac M1, failure #88049\\r\\n- Missing masked tensor documentation #89734\\r\\n- torch.jit.annotations.parse_type_line is not safe (command injection) #88868\\r\\n- Use the Python frame safely in _pythonCallstack #88993\\r\\n- Double-backward with full_backward_hook causes RuntimeError #88312\\r\\n- Fix logical error in get_default_qat_qconfig #88876\\r\\n- Fix cuda/cpu check on NoneType and unit test #88854 and #88970\\r\\n- Onnx ATen Fallback for BUILD_CAFFE2=0 for ONNX-only ops #88504\\r\\n- Onnx operator_export_type on the new registry #87735\\r\\n- torchrun AttributeError caused by file_based_local_timer on Windows #85427\\r\\n\\r\\nThe [release tracker], PR_data:[], commit_data:[], language:Python, files:[\'TestProxyTensorOpInfoCPU.test_make_fx_symbolic_exhaustive_inplace_any_cpu_float32\', \'Transpose.cpp\', \'Clone.cpp\', \'TestNestedTensorSubclassCUDA.test_autograd_function_with_None_grad_cuda_float32\', \'CPython313-test_set-TestOnlySetsString.test_sym_difference\', \'TestUnique.test_unique_axis_errors\', \'aot_autograd.py\', \'PrefixStore.cpp\', \'FusedAdagrad.h\', \'CPython313-test_userlist-UserListTest.test_init\', \'TestNestedTensorSubclassCPU.test_unbind_transpose_ragged_idx_3_cpu\', \'CPython313-test_iter-TestCase.test_builtin_list\', \'distribution.py\', \'Repeat.h\', \'filter_test_configs.py\', \'Type_demangle.cpp\', \'TestProxyTensorOpInfoCPU.test_make_fx_symbolic_exhaustive_inplace_amax_cpu_float32\', \'lennard_jones\', \'TestProxyTensorOpInfoCPU.test_make_fx_fake_exhaustive_nanmedian_cpu_float32\']\'
                    输出： AI技术领域。原因是该项目使用了PyTorch框架，主要用于深度学习和计算机视觉任务。同时，该项目的代码主要使用Python编写，包含多个重要的Python文件。


                    
                    """

    client = OpenAI(
                base_url="https://ai.gitee.com/v1",
                api_key="LV41QCCDGLTQLUUUBAM8KXZKCQOS4ZTUTQDGH461",
    )
    content = ""
    save_name_tmp = os.path.join(save_path, "output_tmp.txt")
    save_name = os.path.join(save_path, "output.txt")

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

    with open(save_name, "a+", encoding="utf-8") as f:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"""请你针对下面的这些已经判定的技术领域和特征词进行总结，输出总结之后的技术领域的分类结果所有特征词，还有分类的原因，如果是AI领域输出结果必须包含AI技术领域这四个字.
                    
                    例如：
                     
                     输入：AI技术领域。原因是该项目使用了PyTorch框架，主要用于深度学习和计算机视觉任务。同时，该项目的代码主要使用Python编写，包含多个重要的Python文件。特征词：（PyTorch, 深度学习, 计算机视觉, Python）
                     
                     输出：### 技术领域分类结果：AI技术领域  
                            #### 所有特征词汇总（去重后）：  
                            1. **PyTorch**  
                            2. **深度学习**  
                            3. **计算机视觉**  
                            4. **Python**  
                            5. **张量运算**  
                            6. **自动微分**  
                            7. **卷积操作**（含 `ConvTranspose1d` / `Conv2d` / `conv1d` / `convolution`）  
                            8. **激活函数**（如 `nn.functional` 相关）  
                            9. **神经网络框架** / **神经网络操作** / **神经网络层实现**  
                            10. **优化器实现** / **计算优化算法**
                            11. **GPU加速/CUDA加速**
                            12. **ONNX支持/优化**
                            13. **多头注意力机制 (MHA)** 
                            14. **大语言模型模块 (LLM)** 
                            15. **C++头文件/实现代码**
                            16. **分布式训练**
                            17. **Tensor Op Info 测试用例**
                            18. **层归一化 (LayerNorm)**
                            19. **嵌入袋 (Embedding Bag)**
                            20. **稀疏计算 (Sparse)**
                            21. **Softmax 函数**

                            ---

                            ### 分类逻辑说明：
                            - 核心框架：`PyTorch` 作为核心工具链贯穿所有场景。
                            - 技术方向：以 `深度学习` 和 `计算机视觉` 为主战场。
                            - 编程语言：主要使用 `Python` 实现逻辑层及接口。
                            - 核心功能模块：
                            - 张量运算 (`Tensor`) + 自动微分 (`autograd`) + GPU 加速 (`CUDA`)
                            - 神经网络构建：卷积层 (`Convolution`) + 激活函数 + 层归一化
                            - 模型优化：优化器设计 + 大语言模型模块 (`LLM`)
                            - 高级特性：
                            - ONNX 支持与转换
                            - 多头注意力机制 (Transformer 架构)
                            - 分布式训练与性能调优
                            - 测试与验证：
                            - 张量操作测试用例 (`Test Proxy Tensor Op Info`)
                            - C++ 实现代码与混合编程

                            ---

                            ### 特别关注点：
                            - 跨语言开发：Python 主体 + C++ 性能组件（如 MHA 实现）
                            - 工具链覆盖范围广：从基础框架到高级算法优化均有涉及
                            - 应用场景明确：聚焦 AI 领域的核心任务"""
                },
                {
                    "role": "user",
                    "content": content
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



        for chunk in response:
            if chunk.choices[0].delta.content:
                # print(chunk.choices[0].delta.content, end="", flush=True)
                with open(save_name, "a+", encoding="utf-8") as f:
                    f.write(chunk.choices[0].delta.content)
            else:
                continue
        

if __name__ == "__main__":
    item_chunks = load_data()
    # main(item_chunks)
    print("Processing complete.")