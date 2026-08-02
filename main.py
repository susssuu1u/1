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
    
    # 你指定的扩充信息源库
    sources = {
        "罗戈网": "https://www.headscm.com/Fingertip/alerts.html",
        "电商报": "https://www.dsb.cn/news",
        "中国物流与采购网": "http://www.chinawuliu.com.cn/zixun/node_524.shtml",
        "物流指闻": "https://www.wlzww.com/",
        "邮政网": "https://www.spb.gov.cn/gjyzj/c100015/list_a.shtml",
        "中国消费观察网":"http://www.btschina.cn/zixun/"
        # 每日财经、南方日报因反爬较严，由大模型在后台进行联网检索补充
    }
    
    combined_text = ""
    
    for name, url in sources.items():
        print(f"正在抓取: {name}")
        try:
            # 加上超时控制，防止某个网站卡死整个流程
            jina_url = f"https://r.jina.ai/{url}"
            response = requests.get(jina_url, headers=headers, timeout=15)
            if response.status_code == 200:
                # 每个网站截取前3500字，防止大模型上下文超载
                text_snippet = response.text[:3500] 
                combined_text += f"\n\n### 【{name}】抓取内容 ###\n{text_snippet}"
            else:
                print(f"⚠️ {name} 抓取失败，状态码: {response.status_code}")
        except Exception as e:
            print(f"⚠️ {name} 抓取超时或异常: {e}")
            
    return combined_text

# 2. 调用大模型进行深度分析 (加入T-1和外单逻辑)
def analyze_and_generate(crawled_text):
    print("正在调用 AI 大脑进行深度合并与分析...")
    client = OpenAI(
        api_key=os.environ.get("LLM_API_KEY"),
        base_url="https://api.deepseek.com" 
    )
    
    # 动态计算日期
    tz = pytz.timezone('Asia/Shanghai')
    today = datetime.now(tz)
    yesterday = today - timedelta(days=1)
    
    today_str = today.strftime('%Y-%m-%d')
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    
    system_prompt = f"""
    你是首席零售与国内物流/供应链战略分析师。今天是 {today_str}，昨天是 {yesterday_str} (T-1)。
    
    请根据我提供的多个信息源抓取文本，并结合你自身的知识库，生成今日的情报看板。
    
    【核心执行规则】
    1. 资讯筛选：重点关注 T-1 ({yesterday_str}) 发生的重大行业事件，时间线最多溯源近 5 天。必须跨渠道去重，合并相似事件。
    2. 链接溯源：输出具体新闻时，必须从抓取文本中找出该新闻的原文链接，并严格按照 Markdown 格式附在末尾，如：[原文链接](https://...)。
    3. 外单指数：必须重点呈现国内/跨境/出海/外贸物流相关指数，如 SCFI（上海出口集装箱运价指数）、CCFI、或核心航空货运价格趋势。
    
    【强制输出格式】(请严格输出 Markdown，切勿添加废话)
    
    # 🌐 零售与物流全景战略看板 ｜ {today_str}
    
    ## 📈 第一部分：宏观大盘与指数 (以表格呈现)
    | 指数板块 | 核心指标名称 (如: SCFI/社零增速/物流成本占比/仓库价格) | 最新动态/数据估值 | 战略简评 |
    | :--- | :--- | :--- | :--- |
    | **跨境与外单** | ... | ... | ... |
    | **国内零售** | ... | ... | ... |
    | **干线与末端** | ... | ... | ... |
    
    ## 🗞️ 第二部分：资讯信息 (T-1 重点聚焦)
    *(提炼 8-10 条最具战略价值的去重资讯)*
    * **[标签，如: 仓配一体/新零售业态 等行业关键词]**：**事件核心摘要** 
      * *AI洞察*：[结合物流打法分析其战略意图]
      * *来源*：[原文链接](提取出的实际URL)
    * *(以此类推)*
    
    ## 🧠 第三部分：分析AI今日总结
    - **行业主线**：[一句话总结近3天的行业主旋律]
    - **行动建议**：[针对国内零售商或供应链企业的物流打法建议或侧重关注点]
    """
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"以下是今日抓取到的各平台原始素材：\n{crawled_text}"}
        ],
        temperature=0.3 # 调低发散性，确保链接和去重逻辑严格执行
    )
    return response.choices[0].message.content

# 3. 将 Markdown 渲染为包含可点击链接的网页
def generate_html(md_content):
    print("正在生成新版网页看板...")
    # 引入 extra 扩展以支持更丰富的 Markdown 语法（包括链接和表格）
    html_body = markdown.markdown(md_content, extensions=['tables', 'extra'])
    
    full_html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>零售与物流情报全景看板</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; max-width: 960px; margin: 0 auto; padding: 20px; background-color: #f3f4f6; color: #1f2937; line-height: 1.6; }}
            .container {{ background-color: #ffffff; padding: 40px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }}
            h1 {{ color: #111827; border-bottom: 3px solid #3b82f6; padding-bottom: 12px; font-size: 1.8rem; }}
            h2 {{ color: #2563eb; margin-top: 35px; font-size: 1.4rem; }}
            table {{ width: 100%; border-collapse: collapse; margin: 25px 0; font-size: 0.95rem; }}
            th, td {{ border: 1px solid #e5e7eb; padding: 14px; text-align: left; }}
            th {{ background-color: #f9fafb; font-weight: 600; color: #374151; }}
            tr:nth-child(even) {{ background-color: #f9fafb; }}
            a {{ color: #2563eb; text-decoration: none; font-weight: 500; }}
            a:hover {{ text-decoration: underline; color: #1d4ed8; }}
            ul {{ margin-left: -20px; }}
            li {{ margin-bottom: 12px; }}
            .insight {{ color: #4b5563; font-size: 0.95rem; margin-top: 4px; }}
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
    print("看板生成完毕！")

if __name__ == "__main__":
    text_data = fetch_news()
    md_result = analyze_and_generate(text_data)
    generate_html(md_result)
