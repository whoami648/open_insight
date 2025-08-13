import gradio as gr
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
import plotly.express as px
import re
import os
import json
from utils import parse_text_to_json,ZILINGYU_ANS
import random
FEATURE_FILE_PATH = r"/home/zyx/open_insight/Qwen-8b-ans1"
FUNCTION_FILE_PATH = r"/home/zyx/open_insight/Scripts/doc_extract/test_data"
class TextAnalysisApp:
    def __init__(self):
        self.demo = self.build_interface()
        

    def text_analysis(self, input_text):
        """ 文本分析处理函数 """

        # 生成词云
        feature_file_path = input_text.replace('https://github.com/', '').replace('/', '_')
        feature_file_path = os.path.join(FEATURE_FILE_PATH, feature_file_path)
        feature_file_name = os.path.join(feature_file_path, "output.txt")

        with open(feature_file_name, "r", encoding="utf-8") as f:
            feature_content = f.read()


        parsed_data = parse_text_to_json(feature_content)

        feature_words = parsed_data.get("所有特征词汇总", [])
        domain_output = parsed_data.get("技术领域分类结果", "")

        # vectorizer = CountVectorizer(stop_words="english", max_features=50)
        # word_counts = vectorizer.fit_transform([input_text])
        keywords = feature_words
        freqs = [1] * len(feature_words)

        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color="white",
            font_path="/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # 设置中文字体路径
        ).generate_from_frequencies(dict(zip(feature_words, freqs)))
        wordcloud_path = "wordcloud.png"
        wordcloud.to_file(wordcloud_path)




        top_keywords = "\n".join(keywords)

        # top_keywords = "\n".join(keywords)


        function_path = input_text.replace('https://github.com/', '').replace('/', '_')
        function_path = os.path.join(FUNCTION_FILE_PATH, function_path)
        function_path = os.path.join(function_path, "output.txt")
        with open(function_path, "r", encoding="utf-8") as f:
            # f.write(json.dumps(parsed_data, ensure_ascii=False, indent=4))
            summary = f.read().strip()
            if not summary:
                summary = "未能生成有效的功能注解，请检查输入文本或模型配置。"

        xiaofeidu_output = ZILINGYU_ANS.get(input_text.replace('https://github.com/', '').replace('/', '_'), "未知细分领域分类结果")

        return domain_output, xiaofeidu_output, wordcloud_path, top_keywords, summary

    def build_interface(self):
        with gr.Blocks(title="技术领域分类工具", css=".gradio-container .prose h1, .gradio-container .prose h2, .gradio-container .prose h3 {text-align: center;}", theme=gr.themes.Soft()) as demo:
            gr.Markdown("## 🚀 技术领域分类工具")
            gr.Markdown("输入开源项目链接，进行技术领域分类、特征词提取、词云图生成等分析。")

            with gr.Row():
                self.text_input = gr.Textbox(
                    label="输入开源项目链接",
                    placeholder="粘贴或输入开源项目链接...",
                    lines=8,
                    max_lines=20,
                    interactive=True
                )

            self.submit_btn = gr.Button("start", variant="primary")
            self.clear_btn = gr.Button("clear")


            with gr.Tab("技术领域分类"):
                self.domain_output = gr.Textbox(label="宏领域分类结果")
                self.xiaofeidu_output = gr.Textbox(label="细分领域分类结果")
            with gr.Tab("词云图"):
                self.wordcloud_output = gr.Image(label="特征词词云", type="filepath")
            # with gr.Tab("气泡图"):
            #     self.plot_output = gr.Plot(label="词频分布气泡图")
            with gr.Tab("特征词列表"):
                self.keywords_output = gr.Textbox(label="特征词摘要")
            with gr.Tab("文本功能注解"):
                self.summary_output = gr.Textbox(label="功能注解", lines=4)
            

            self.submit_btn.click(
                fn=self.text_analysis,
                inputs=self.text_input,
                outputs=[self.domain_output, self.xiaofeidu_output, self.wordcloud_output, self.keywords_output, self.summary_output]
            )
            self.clear_btn.click(
                lambda: [None,None, None, "", ""],
                inputs=None,
                outputs=[self.domain_output,self.xiaofeidu_output, self.wordcloud_output, self.keywords_output, self.summary_output]
            )
        return demo

    def launch(self, server_port=8000, share=False):
        self.demo.launch(server_port=server_port, share=share)

if __name__ == "__main__":
    app = TextAnalysisApp()
    app.launch(server_port=8000, share=False)
