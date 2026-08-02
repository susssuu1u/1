import os
import requests
from openai import OpenAI
import markdown
from datetime import datetime, timedelta
import pytz

# 1. 多源抓取模块 (带容错机制)
def fetch_news():
    print("正在抓取全网最新资讯...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    sources = {
        "罗戈网": "https://www.headscm.com/Fingertip/alerts.html",
        "电商报": "https://www.dsb.cn/news",
        "中国物流与采购网": "http://www.chinawuliu.com.cn/zixun/node_524.shtml",
        "物流指闻": "https://www.wlzww.com/",
        "中华人民共和国国家发展和改革委员会":"https://www.ndrc.gov.cn/",
        "中国消费观察网":"http://www.btschina.cn/zixun/"
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

# 2. 调用大脑进行结构化生成 (全面升级 Prompt)
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
    不要使用任何 Markdown 表格。全部使用具有层级感的无序列表和加粗字体。
    
    # 🌐 行业风向标 ｜ {today_str}
    
    ## 🗞️ 一、 行业最新资讯
    (请严格分为下面三个子模块，跨渠道去重，总数控制在 10 条以内。每条内容必须包含足够的业务细节、数据和逻辑，需要将内容做提炼。商流动态关注零售新零售、电商发展、新模式发展；物流与供应链关注物流。供应链行业的新动态、仓库或运输模式、新库存模式等)
    
    ### 🛒 商流动态
    - **【主题-标题】**
      [详细资讯内容，保留核心数据和业务动作]
      [🔗 原文](提取出的实际URL)
      
    ### 🚚 物流与供应链
    - **【主题-标题】**
      [详细资讯内容，保留核心数据和业务动作]
      [🔗 原文](提取出的实际URL)
      
    ### 📜 宏观风向
    - **【主题-标题】**
      [详细资讯内容，保留核心数据和业务动作]
      [🔗 原文](提取出的实际URL)

    ## 📈 二、 宏观大盘与相关指数
    (请自动抓取或结合知识库输出当前最新的核心大盘数据。有什么重要数据就输出什么，覆盖：仓储指数、物流指数、社零消费、医药冷链/大件指数、运输运价等)
    (格式如下，请严格保持：)
    - **[指数名称，如：7月中国公路物流运价指数]**：**[数值/趋势，如：102.4点，环比回落]**。
      *解读*：[结合实际环境，用一句话点评该数据的意义]
    - (以此类推，输出 4-6 个核心关键指数)

    ## 🧠 三、 今日AI总结与分析
    (结合今日所有信息，站在物流/供应链总监的视角输出)
    
    ### 💡 行业洞察
    (用一段话，深度穿透今天的繁杂信息，提炼出底层商业规律或趋势)
    
    ### 🎯 发力与关注点
    - (列出 2-3 个接下来最值得业务侧关注的机会点或风险点)
    
    ### 🏗️ AI启示
    - (针对仓网布局、降本增效、自动化投入、运力采购等具体的供应链规划环节，给出 2-3 条极具实操性的破局思考或建议)
    """
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"今日原始素材：\n{crawled_text}"}
        ],
        temperature=0.4
    )
    return response.choices[0].message.content

# 3. 生成自适应卡片式网页 (注入高级 CSS)
def generate_html(md_content):
    print("正在生成现代化响应式网页...")
    html_body = markdown.markdown(md_content)
    
    # 全新自适应卡片 UI
    full_html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>战略情报指挥台</title>
        <style>
            :root {{
                --bg: #f4f7f6;
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
            /* 大标题优化 */
            h1 {{ text-align: center; font-size: 1.8rem; color: #111827; margin-bottom: 40px; }}
            
            /* 二级标题 (模块分割) */
            h2 {{
                background: linear-gradient(90deg, #dbeafe 0%, transparent 100%);
                color: #1e40af;
                padding: 10px 15px;
                border-left: 5px solid var(--primary);
                border-radius: 4px;
                margin-top: 50px;
                font-size: 1.3rem;
            }}
            h3 {{ color: #374151; font-size: 1.1rem; border-bottom: 2px solid var(--border); padding-bottom: 8px; margin-top: 30px; }}
            
            /* 魔法卡片化：将所有列表元素转为卡片 */
            ul {{ list-style: none; padding: 0; display: flex; flex-direction: column; gap: 16px; }}
            li {{
                background-color: var(--card-bg);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            li:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            }}
            
            /* 卡片内字体微调 */
            li strong {{ color: #111827; font-size: 1.05rem; display: block; margin-bottom: 8px; }}
            li p {{ margin: 0; color: var(--text-muted); }}
            
            /* 链接样式 */
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
            
            /* 手机端适配 */
            @media (max-width: 600px) {{
                body {{ padding: 10px; }}
                h1 {{ font-size: 1.5rem; }}
                li {{ padding: 15px; }}
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
