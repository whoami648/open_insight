# open_insight
本项目主要针对开源项目的技术领域进行划分，构建了多智能体的划分方式，包括特征词范式生成智能体、特征词范式聚类智能体、特征词范式分类智能体等。通过这些智能体，可以实现对开源项目的技术领域进行自动化的划分和分析，从而为开源项目的管理和维护提供支持。
目前主要支持AI领域的技术划分，采用模型为Qwen3-8B 和 后续会增加更多的模型支持。

# 使用说明

```bash
# 克隆项目仓库
git clone https://github.com/yourusername/open_insight.git
cd open_insight
```
## 创建环境
```bash
# 推荐使用conda创建虚拟环境
conda create -n open_insight python=3.12.3
conda activate open_insight
pip install -r requirements.txt
```
## 配置API密钥

在 `src/feature_extract/document_metric/config.ini` 文件中添加您的 API 密钥：

```ini
[apikey]
your_api_key=YOUR_API_KEY_HERE
```

请将 `YOUR_API_KEY_HERE` 替换为实际的 API 密钥。
