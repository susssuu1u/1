import os
import requests
from openai import OpenAI
import markdown
from datetime import datetime
import pytz

# 1. 抓取网页内容 (使用 Jina Reader 将复杂网页直接转成 LLM 最爱看的干净 Markdown)
def fetch_news():
    print("正在抓取今日资讯...")
    headers = {"User-Agent": "Mozilla/5.0"}
    # 抓取罗戈网
    headscm_url = "https://r.jina.ai/https://www.headscm.com/Fingertip/alerts.html"
    headscm_text = requests.get(headscm_url, headers=headers).text[:5000] # 截取前5000字防超载
    
    # 抓取派代网
    pai_url = "https://r.jina.ai/https://www.pai.com.cn/news"
    pai_text = requests.get(pai_url, headers=headers).text[:5000]
    
    return headscm_text, pai_text

# 2. 调用大模型进行深度分析
def analyze_and_generate(headscm_text, pai_text):
    print("正在调用 AI 大脑进行分析...")
    # 这里以 DeepSeek 为例，如果你用其他模型，修改 base_url 即可
    client = OpenAI(
        api_key=os.environ.get("LLM_API_KEY"),
        base_url="https://api.deepseek.com" 
    )
    
    today_str = datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d')
    
    system_prompt = f"""
    你是首席零售与物流战略分析师。今天是 {today_str}。
    请根据我提供的【罗戈网】和【派代网】今日最新资讯文本，提取出最具战略价值的 5-8 条动态。
    结合当前宏观指数（如社零增速、公路运价指数、快递业务量，请利用你的知识库给出最新概数），进行深度点评。
    请严格按照 Markdown 格式输出，包含：
    1. 大标题：🌐 零售与物流战略风向标 ｜ {today_str}
    2. 📈 宏观环境与行业指数（表格形式，包含数据和一句话简评）
    3. 🗞️ 核心阵地动态监测（提炼核心事件、分析物流打法，并附上你认为的重要度评级）
    4. 🧠 首席分析师今日总结（行业主线总结与行动建议）
    注意：不要输出任何多余的开场白，直接输出 Markdown 正文。
    """
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"罗戈网内容:\n{headscm_text}\n\n派代网内容:\n{pai_text}"}
        ],
        temperature=0.5
    )
    return response.choices[0].message.content

# 3. 将 Markdown 渲染为精美的 HTML 网页
def generate_html(md_content):
    print("正在生成网页看板...")
    html_body = markdown.markdown(md_content, extensions=['tables'])
    
    # 加上一点 CSS 让网页看起来像个高端看板
    full_html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>零售与物流战略看板</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 900px; margin: 0 auto; padding: 30px; background-color: #f8f9fa; color: #333; }}
            .container {{ background-color: #fff; padding: 40px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
            h1 {{ color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 10px; }}
            h2 {{ color: #202124; margin-top: 30px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #e0e0e0; padding: 12px; text-align: left; }}
            th {{ background-color: #f1f3f4; font-weight: bold; }}
            ul {{ line-height: 1.8; }}
        </style>
    </head>
    <body>
        <div class="container">
            {html_body}
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    print("生成完毕！")

if __name__ == "__main__":
    t1, t2 = fetch_news()
    md_result = analyze_and_generate(t1, t2)
    generate_html(md_result)
