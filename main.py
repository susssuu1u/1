import os
import requests
from openai import OpenAI
import markdown
from datetime import datetime
import pytz

# 1. 多源抓取模块 (保持不变)
def fetch_news():
    print("正在抓取全网最新资讯...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    sources = {
        "罗戈网": "https://www.headscm.com/Fingertip/alerts.html",
        "电商报": "https://www.dsb.cn/news",
        "中国物流与采购网": "http://www.chinawuliu.com.cn/zixun/node_524.shtml",
        "亿邦动力(电商)": "https://www.ebrun.com/",
        "物流指闻": "https://www.wlzww.com/",
        "中国消费观察网":"http://www.btschina.cn/zixun/",
        "赢商网(华南)": "http://news.winshang.com/list-11.html"
    }
    
    combined_text = ""
    for name, url in sources.items():
        print(f"正在抓取: {name}")
        try:
            jina_url = f"https://r.jina.ai/{url}"
            response = requests.get(jina_url, headers=headers, timeout=15)
            if response.status_code == 200:
                text_snippet = response.text[:4000] 
                combined_text += f"\n\n### 【{name}】抓取内容 ###\n{text_snippet}"
        except Exception as e:
            print(f"⚠️ {name} 抓取超时或异常: {e}")
            
    return combined_text

# 2. 调用大脑进行结构化生成 (注入导读与前瞻评价指令)
def analyze_and_generate(crawled_text):
    print("正在进行深度分析与排版...")
    client = OpenAI(
        api_key=os.environ.get("LLM_API_KEY"),
        base_url="https://api.deepseek.com" 
    )
    
    tz = pytz.timezone('Asia/Shanghai')
    today_str = datetime.now(tz).strftime('%Y-%m-%d')
    
    system_prompt = f"""
    你是首席零售与供应链战略规划专家。今天是 {today_str}。
    请根据抓取到的全网素材，结合你的知识库，输出今日的情报内参。

    【排版与内容强制要求】
    不要使用表格。严格使用 Markdown 的引用语法 (>) 来呈现 AI 导读，使用无序列表呈现新闻。
    
    # 🌐 行业风向标 ｜ {today_str}
    
    > **🌟 今日insight**：[请用 1-2 句话，高度浓缩今天全网资讯中最震撼、最需要关注的战略级异动、趋势或宏观拐点。必须犀利、直击要害。]

    ## 🗞️ 一、 行业最新资讯
    
    ### 🛒 1. 商流动态
    > **🤖 AI 导读**：[一句话提炼今日商流板块的核心逻辑，例如：前端价格战加剧，品牌方加速寻找下沉增量]
    - **【主题-标题】**
      [详细资讯内容，保留核心数据和业务动作]
      [🔗原文](提取出的实际URL)
      
    ### 🚚 2. 物流与供应链
    > **🤖 AI 导读**：[一句话提炼今日物流板块的核心博弈点或打法，例如：头部企业通过数字化手段强压干线成本]
    - **【主题-标题】**
      [详细资讯内容，保留核心数据和业务动作]
      [🔗原文](提取出的实际URL)

    ### 🌴 3. 华南专属
    > **🤖 AI 导读**：[一句话提炼今日大湾区或本地商业的焦点]
    - **【主题-标题】**
      [详细资讯内容]
      [🔗原文](提取出的实际URL)
      
    ### 📜 4. 政策与宏观风向
    > **🤖 AI 导读**：[一句话提炼政策释放的红利或监管信号]
    - **【主题-标题】**
      [详细资讯内容]
      [🔗原文](提取出的实际URL)

    ## 📈 二、 宏观大盘与相关指数
    (输出当前最新的核心大盘数据。覆盖：仓储指数、物流指数、社零消费、医药冷链/大件指数、运价等)
    - **[指数名称]**：**[数值/趋势]**。*战略解读*：[一句话点评该数据的意义]
    - (输出 4-6 个核心关键指数)

    ## 🧠 三、 AI总结与思考
    ### 💡 今日行业洞察
    (用一段话深度穿透底层商业规律)
    ### 🎯 重点发力与关注点
    - (列出 2-3 个最值得业务侧关注的机会点或风险点)
    ### 🏗️ 一点思考
    - (针对仓网布局、降本增效等，给出 2-3 条实操性建议)
    """
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"今日原始素材：\n{crawled_text}"}
        ],
        temperature=0.6 # 适度调高一点温度，让 AI 的“评价”和“思考”更加锐利有深度
    )
    return response.choices[0].message.content

# 3. 生成自适应网页 (重写引用块样式，打造高亮 UI)
def generate_html(md_content):
    print("正在生成现代化响应式网页...")
    html_body = markdown.markdown(md_content)
    
    full_html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>战略情报指挥台</title>
        <style>
            :root {{
                --bg: #f3f4f6;
                --card-bg: #ffffff;
                --primary: #2563eb;
                --text-main: #1f2937;
                --text-muted: #4b5563;
                --border: #e5e7eb;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
                background-color: var(--bg);
                color: var(--text-main);
                line-height: 1.7;
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1 {{ text-align: center; font-size: 1.8rem; color: #111827; margin-bottom: 30px; }}
            
            /* 【重点优化】AI 导读与思考的高亮样式 (Blockquote) */
            blockquote {{
                background-color: #f0fdf4; /* 浅清新的绿色背景 */
                border-left: 5px solid #16a34a; /* 醒目的左侧粗边框 */
                margin: 20px 0;
                padding: 15px 20px;
                border-radius: 0 8px 8px 0;
                color: #166534;
                font-size: 1.05rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }}
            blockquote strong {{
                color: #15803d;
                font-size: 1.1rem;
            }}

            h2 {{
                background: linear-gradient(90deg, #dbeafe 0%, transparent 100%);
                color: #1e40af;
                padding: 10px 15px;
                border-left: 5px solid var(--primary);
                border-radius: 4px;
                margin-top: 40px;
                font-size: 1.3rem;
            }}
            h3 {{ color: #374151; font-size: 1.1rem; border-bottom: 2px solid var(--border); padding-bottom: 8px; margin-top: 30px; }}
            
            /* 新闻卡片样式 */
            ul {{ list-style: none; padding: 0; display: flex; flex-direction: column; gap: 16px; }}
            li {{
                background-color: var(--card-bg);
                border: 1px solid var(--border);
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.04);
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            li:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 12px rgba(0, 0, 0, 0.08);
            }}
            li strong {{ color: #111827; font-size: 1.05rem; display: block; margin-bottom: 8px; }}
            li p {{ margin: 0; color: var(--text-muted); }}
            a {{
                color: var(--primary);
                text-decoration: none;
                font-weight: 600;
                display: inline-block;
                margin-top: 10px;
                background-color: #eff6ff;
                padding: 4px 10px;
                border-radius: 6px;
                font-size: 0.9rem;
            }}
            a:hover {{ background-color: #dbeafe; }}
            @media (max-width: 600px) {{
                body {{ padding: 12px; }}
                h1 {{ font-size: 1.5rem; }}
                li {{ padding: 15px; }}
                blockquote {{ font-size: 1rem; padding: 12px 15px; }}
            }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    print("看板生成完毕！")

if __name__ == "__main__":
    text_data = fetch_news()
    md_result = analyze_and_generate(text_data)
    generate_html(md_result)
