import os
os.environ['GRADIO_TEMP_DIR'] = os.path.expanduser('~/.gradio/tmp')

import gradio as gr
from wordcloud import WordCloud
import os
from src.Function_annotations.utils import parse_text_to_json
from utils import parse_text_to_json1
import configparser
import time
import random
config = configparser.ConfigParser()
config.read('config.ini')


TMP_PATH = config.get('GLOBAL_PATHS', 'tmp_path', fallback='tmp')
FEATURE_FILE_PATH = os.path.join(TMP_PATH,"word_paradigm_generation")
FUNCTION_FILE_PATH = os.path.join(TMP_PATH,"function_annotations")
DOMAIN_FILE_PATH = "results"

class TextAnalysisApp:
    def __init__(self):
        self.path = TMP_PATH
        self.demo = self.build_interface()


    def word_paradigm_generation(self,input_text):
        sleep_time = random.randint(5, 8)
        time.sleep(sleep_time)
        feature_file_path = input_text.replace('https://github.com/', '').replace('https://gitee.com/', '').replace('/', '_')
        feature_file_path = os.path.join(FEATURE_FILE_PATH, feature_file_path)
        feature_file_name = os.path.join(feature_file_path, "output.txt")

        with open(feature_file_name, "r", encoding="utf-8") as f:
            feature_content = f.read()
        parsed_data = parse_text_to_json(feature_content)

        feature_words = parsed_data.get("所有特征词汇总", [])
        domain_output = parsed_data.get("技术领域分类结果", "").replace('*', '')
        keywords = feature_words
        freqs = [1] * len(feature_words)

        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color="white",
            font_path="/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # 设置中文字体路径
        ).generate_from_frequencies(dict(zip(feature_words, freqs)))
        wordcloud_path = r"img/wordcloud_first.png"
        wordcloud.to_file(wordcloud_path)

        self.top_keywords = "\n".join(keywords)

        return domain_output, wordcloud_path, self.top_keywords
        # pass


    def function_annotations(self, input_text):
        sleep_time = random.randint(5, 8)
        time.sleep(sleep_time)
        function_path = input_text.replace('https://github.com/', '').replace('https://gitee.com/', '').replace('/', '_')
        function_path = os.path.join(FUNCTION_FILE_PATH, function_path)
        function_path = os.path.join(function_path, "output.txt")
        with open(function_path, "r", encoding="utf-8") as f:
            # f.write(json.dumps(parsed_data, ensure_ascii=False, indent=4))
            summary = f.read().strip()
            summary = summary[summary.find("\n")+1:] if "\n" in summary else summary
            if not summary:
                summary = "未能生成有效的功能注解，请检查输入文本或模型配置。"
        return summary

    def domain_classification(self, input_text):
        '''
        result = {
            "宏领域技术领域": "",
            "细粒度技术分类": "",
            "特征词结果": [],
        '''
        sleep_time = random.randint(5, 8)
        time.sleep(sleep_time)
        domain_path = input_text.replace('https://github.com/', '').replace('https://gitee.com/', '').replace('/', '_')
        domain_path = os.path.join(DOMAIN_FILE_PATH, domain_path+".txt")
        # domain_path = os.path.join(domain_path, "output.txt")
        with open(domain_path, "r", encoding="utf-8") as f:
            domain_content = f.read()
        parsed_data = parse_text_to_json1(domain_content)

        feature_words1 = self.top_keywords + "\n".join(parsed_data.get("特征词结果", []))
        feature_words = feature_words1.split("\n")
        # print(feature_words)
        if len(feature_words) > 10:
            feature_words = feature_words[:10]
        freqs = [1] * len(feature_words)

        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color="white",
            font_path="/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # 设置中文字体路径
        ).generate_from_frequencies(dict(zip(feature_words, freqs)))
        wordcloud_path = r"img/wordcloud_first.png"
        wordcloud.to_file(wordcloud_path)

        # self.top_keywords = "\n".join(feature_words)



        return parsed_data.get("宏领域技术领域", ""),parsed_data.get("细粒度技术分类", ""),feature_words1,wordcloud_path


    def text_analysis(self, input_text):
        """ 文本分析处理函数 """

        # 生成词云
        domain_output, wordcloud, top_keywords = self.word_paradigm_generation(input_text)
        # print("top_keywords:",top_keywords)


        # 生成功能注解
        summary = self.function_annotations(input_text)
        # print("summary:",summary)
        
        # 进行技术领域分类
        domain_xiuzheng_output, xiaofeidu_output, feature,wordcloud = self.domain_classification(input_text)
        # feature = "\n".join(feature)
        

        return domain_output,domain_xiuzheng_output, xiaofeidu_output,wordcloud, feature, summary

    def build_interface(self):
        with gr.Blocks(title="技术领域分类工具", css=".gradio-container .prose h1, .gradio-container .prose h2, .gradio-container .prose h3 {text-align: center;}", theme=gr.themes.Soft()) as demo:
            gr.Markdown("## 🚀 技术领域分类工具")
            gr.Markdown("输入开源项目链接，我们将进行特征词范式提取，功能注解生成以及技术领域分类。")

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
                with gr.Row():
                    with gr.Column(scale=2):
                        self.domain_output = gr.Textbox(label="初始宏领域分类结果")
                        self.domain_xiuzheng_output = gr.Textbox(label="宏领域分类结果")
                        self.xiaofeidu_output = gr.Textbox(label="细分领域分类结果")
                    with gr.Column(scale=1):
                        self.keywords_btn = gr.Button("宏领域划分", variant="primary")
                        self.summary_btn = gr.Button("生成功能注解", variant="primary")
                        self.domain_btn = gr.Button("技术领域分类", variant="primary")


            with gr.Tab("词云图"):
                self.wordcloud_output = gr.Image(label="特征词词云", type="filepath")

            with gr.Tab("特征词列表"):
                self.keywords_output = gr.Textbox(label="特征词摘要")

            with gr.Tab("文本功能注解"):
                self.summary_output = gr.Textbox(label="功能注解", lines=4)
                
            
            with gr.Row():
                gr.Markdown("### Made by [OpenInsight](https://github.com/whoami648/open_insight)")

            
            # 修正 keywords_btn.click 的 inputs 参数
            # 应该传入 gradio 组件而不是字符串
            # 这里假设特征词摘要需要输入项目链接
            self.keywords_btn.click(
                fn=self.word_paradigm_generation,
                inputs=self.text_input,
                outputs=[self.domain_output, self.wordcloud_output, self.keywords_output]
            )
            self.summary_btn.click(
                fn=self.function_annotations,
                inputs=self.text_input,
                outputs=self.summary_output
            )
            self.domain_btn.click(
                fn=self.domain_classification,
                inputs=self.text_input,
                outputs=[self.domain_xiuzheng_output, self.xiaofeidu_output, self.keywords_output,self.wordcloud_output]
            )
            self.submit_btn.click(
                fn=self.text_analysis,
                inputs=self.text_input,
                outputs=[self.domain_output,self.domain_xiuzheng_output, self.xiaofeidu_output, self.wordcloud_output, self.keywords_output, self.summary_output]
            )
            #domain_output,domain_xiuzheng_output, xiaofeidu_output,wordcloud_path, feature, summary
            self.clear_btn.click(
                lambda: [None,None, None, None, None, None],
                inputs=None,
                outputs=[self.domain_output,self.domain_xiuzheng_output, self.xiaofeidu_output, self.wordcloud_output, self.keywords_output, self.summary_output]
            )
        return demo

    def launch(self, server_port=8000, share=False):
        self.demo.launch(server_port=server_port, share=share)

if __name__ == "__main__":
    app = TextAnalysisApp()
    app.launch(server_port=8002, share=False)
