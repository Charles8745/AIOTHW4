"""
古代思想家風格的 AI 思考生成器 (升級版)
==========================================
使用 Two-Stage Chain-of-Thought (CoT) 技術
讓 AI 模擬老子、孔子、管仲三位思想家的思考方式

✨ 升級功能：
- 一鍵比較三位思想家
- 經典名言引用
- 串流輸出 (Streaming)
- 範例問題一鍵填入

作者：Charles
日期：2025/12/04
"""

import streamlit as st
from groq import Groq
import os
import random

# ==================== 頁面設定 ====================
st.set_page_config(
    page_title="古代思想家 AI 思考生成器",
    page_icon="🏛️",
    layout="wide"
)

# ==================== 自訂 CSS ====================
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
    .quote-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        font-style: italic;
        margin: 10px 0;
        text-align: center;
    }
    .thinker-card {
        border-radius: 10px;
        padding: 15px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== API 設定 ====================
def get_api_key():
    try:
        return st.secrets["GROQ_API_KEY"]
    except:
        return os.environ.get("GROQ_API_KEY", "")

# ==================== 經典名言庫 ====================
QUOTES = {
    "老子式（道家）": [
        "道可道，非常道；名可名，非常名。",
        "上善若水，水善利萬物而不爭。",
        "天下之至柔，馳騁天下之至堅。",
        "知人者智，自知者明。",
        "千里之行，始於足下。",
        "禍兮福之所倚，福兮禍之所伏。",
        "大巧若拙，大辯若訥。",
        "無為而無不為。"
    ],
    "孔子式（儒家）": [
        "己所不欲，勿施於人。",
        "學而不思則罔，思而不學則殆。",
        "三人行，必有我師焉。",
        "君子和而不同，小人同而不和。",
        "知之為知之，不知為不知，是知也。",
        "溫故而知新，可以為師矣。",
        "德不孤，必有鄰。",
        "見賢思齊焉，見不賢而內自省也。"
    ],
    "管仲式（法家/務實）": [
        "倉廩實則知禮節，衣食足則知榮辱。",
        "政之所興，在順民心；政之所廢，在逆民心。",
        "一年之計，莫如樹穀；十年之計，莫如樹木；終身之計，莫如樹人。",
        "禮義廉恥，國之四維；四維不張，國乃滅亡。",
        "善人者，人亦善之。",
        "令則行，禁則止。",
        "士農工商四民者，國之石民也。"
    ]
}

# ==================== 範例問題 ====================
EXAMPLE_QUESTIONS = [
    "我要如何讓新團隊快速運作起來？",
    "面對團隊內部衝突，我應該怎麼處理？",
    "在有限預算下，如何提升產品上線速度？",
    "我該如何在公司中獲得升遷機會？",
    "面對兩個都不錯的選擇，我該如何決定？",
    "如何有效率地完成一個大型專案？",
    "如何平衡工作與生活？",
    "如何激勵團隊成員更積極投入？"
]

# ==================== 思想家風格定義 ====================
THINKERS = {
    "老子式（道家）": {
        "icon": "☯️",
        "color": "#6B5B95",
        "bg_color": "#f0ebf8",
        "core_concepts": "無為、順勢、柔弱勝剛強、反者道之動、道法自然、去欲去控制",
        "short_desc": "以退為進，順應自然",
        "stage1_system": """你是「老子」本人穿越到現代，是一位說話很有禪意但又接地氣的智慧老朋友。

你的個性：
- 🍵 說話慢悠悠的，喜歡用生活中的比喻（水、風、樹、茶...）
- 😌 常常反問對方，讓人自己想通
- 🌊 喜歡用「你有沒有想過...」「其實啊...」「我跟你說個故事」開頭
- 😏 偶爾會幽默吐槽現代人太急躁

核心觀念（用聊天的方式帶出來）：
- 無為：「有時候不動，比亂動好」
- 順勢：「水往低處流，不是因為它傻，是因為它聰明」
- 反向思維：「你越想抓住，它越溜走」

請用台灣年輕人的口語 + 一點文言點綴。像朋友聊天一樣，產生 4-5 個思考角度。
每個角度用「🌀」開頭，不要用 Step 1、Step 2 這種死板格式。
可以加入一些「欸」「啊」「嘛」「齁」等語氣詞。""",
        
        "stage2_system": """你是老子本人，剛剛已經幫朋友分析過問題了，現在要給他一些暖心又實用的建議。

說話風格：
- 像個喝茶聊天的長輩，但不說教
- 會用「我建議你啊...」「不然你試試看...」「我以前也遇過類似的」
- 適時引用一句道德經的話，但要翻譯成白話
- 最後給一個很有畫面感的總結，像是「就像水一樣...」

請根據剛剛的思考角度，給出 3-4 個具體建議。
結尾用一段溫暖的話收尾，像朋友互相打氣那樣。
可以用 emoji 點綴，但不要太多。"""
    },
    
    "孔子式（儒家）": {
        "icon": "📚",
        "color": "#DD4124",
        "bg_color": "#fdf0ef",
        "core_concepts": "仁義禮智信、以德服人、修身齊家治國、名正言順、中庸之道",
        "short_desc": "以德服人，修身齊家",
        "stage1_system": """你是「孔子」本人穿越到現代，是一位溫暖又有點囉嗦的老師型朋友。

你的個性：
- 📖 很在乎人跟人之間的關係，常說「做人最重要的是...」
- 🤝 會從對方的角度想問題，常問「那對方會怎麼想？」
- 😊 講話溫溫的，但很有說服力
- 🎯 相信「把自己做好，事情就會變好」

核心觀念（用聊天的方式帶出來）：
- 仁：「你對別人好，別人也會對你好」
- 修身：「先管好自己，再談改變別人」
- 中庸：「太過或不及都不好，要找到平衡點」

請用台灣習慣的溫暖口語。像個會關心你的學長姐在跟你聊天。
產生 4-5 個思考角度，每個用「💭」開頭。
會說「我覺得啦」「你想想看」「換個角度來說」這種話。""",
        
        "stage2_system": """你是孔子本人，剛剛分析完了，現在要給朋友溫暖又實際的建議。

說話風格：
- 像個很會照顧人的學長姐
- 會說「我建議你可以...」「第一步先...」「記得要...」
- 偶爾引用論語但會加上白話解釋，像是「子曰：...（意思就是...）」
- 會提醒對方照顧好自己、也照顧好身邊的人

請根據剛剛的思考，給出 3-4 個溫暖又可執行的建議。
結尾要像朋友一樣鼓勵對方，讓人覺得被支持。
可以用 emoji 但要溫馨風格。"""
    },
    
    "管仲式（法家/務實）": {
        "icon": "⚖️",
        "color": "#009B77",
        "bg_color": "#e8f5f1",
        "core_concepts": "制度、分工、效率、獎懲分明、富國強兵、務實治國",
        "short_desc": "制度為本，效率至上",
        "stage1_system": """你是「管仲」本人穿越到現代，是一位超級務實、講話直接的創業導師型朋友。

你的個性：
- 💼 講話很直接，不廢話，直接切重點
- 📊 喜歡分析利弊、算成本效益
- 🎯 常說「重點是...」「關鍵在於...」「你要先搞清楚...」
- 😎 有點霸氣，但是是為對方好

核心觀念（用聊天的方式帶出來）：
- 制度：「沒有規矩不成方圓，先把規則訂好」
- 效率：「時間就是錢，不要浪費在沒用的事上」
- 獎懲：「做得好要獎，做不好要罰，很公平」

請用台灣職場常見的直接口語。像個很 carry 的主管在幫你分析。
產生 4-5 個思考角度，每個用「⚡」開頭。
會說「老實說」「講白了」「重點來了」這種話。""",
        
        "stage2_system": """你是管仲本人，分析完了，現在要給出超級實用的行動方案。

說話風格：
- 像個很罩的創業前輩，講話直接有力
- 會說「第一，你要...」「再來...」「最重要的是...」
- 會幫對方算利弊、預測風險
- 最後給一個很有執行力的總結

請根據剛剛的分析，給出 3-4 個可以馬上執行的建議。
每個建議都要具體、可量化、有時間表更好。
結尾要很有力量，像在幫對方打一劑強心針。
可以用 emoji 但要專業風格。"""
    }
}

# ==================== Groq API 呼叫函式（串流版）====================
def call_groq_stream(system_prompt: str, user_prompt: str, api_key: str):
    """呼叫 Groq API 進行串流推理"""
    try:
        client = Groq(api_key=api_key)
        
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1024,
            temperature=0.7,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
                
    except Exception as e:
        yield f"❌ API 呼叫錯誤：{str(e)}"

def call_groq(system_prompt: str, user_prompt: str, api_key: str) -> str:
    """呼叫 Groq API 進行推理（非串流版，用於比較模式）"""
    try:
        client = Groq(api_key=api_key)
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1024,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return f"❌ API 呼叫錯誤：{str(e)}"

# ==================== Two-Stage CoT 主函式 ====================
def ancient_thinker_generate_stream(question: str, thinker_style: str, api_key: str, stage1_placeholder, stage2_placeholder):
    """
    Two-Stage Chain-of-Thought 生成（串流版）
    """
    thinker = THINKERS[thinker_style]
    
    # Stage 1: 生成推理鏈
    stage1_prompt = f"""使用者的問題是：「{question}」

請以這位思想家的核心觀念進行深度思考：
{thinker['core_concepts']}

產生 4-6 條推理步驟，每條標明 Step 編號。"""

    reasoning_chain = ""
    for chunk in call_groq_stream(thinker["stage1_system"], stage1_prompt, api_key):
        reasoning_chain += chunk
        stage1_placeholder.markdown(reasoning_chain + "▌")
    stage1_placeholder.markdown(reasoning_chain)
    
    # Stage 2: 根據推理鏈生成建議
    stage2_prompt = f"""使用者的原始問題：「{question}」

以下是 Stage1 產生的推理鏈：
{reasoning_chain}

請根據上述每一條推理步驟，提供對應的具體建議，最後給出總結。"""

    final_advice = ""
    for chunk in call_groq_stream(thinker["stage2_system"], stage2_prompt, api_key):
        final_advice += chunk
        stage2_placeholder.markdown(final_advice + "▌")
    stage2_placeholder.markdown(final_advice)
    
    return reasoning_chain, final_advice

def ancient_thinker_generate(question: str, thinker_style: str, api_key: str):
    """
    Two-Stage Chain-of-Thought 生成（非串流版，用於比較模式）
    """
    thinker = THINKERS[thinker_style]
    
    stage1_prompt = f"""使用者的問題是：「{question}」

請以這位思想家的核心觀念進行深度思考：
{thinker['core_concepts']}

產生 4-6 條推理步驟，每條標明 Step 編號。"""

    reasoning_chain = call_groq(thinker["stage1_system"], stage1_prompt, api_key)
    
    stage2_prompt = f"""使用者的原始問題：「{question}」

以下是 Stage1 產生的推理鏈：
{reasoning_chain}

請根據上述每一條推理步驟，提供對應的具體建議，最後給出總結。"""

    final_advice = call_groq(thinker["stage2_system"], stage2_prompt, api_key)
    
    return reasoning_chain, final_advice

# ==================== Streamlit UI ====================
def main():
    # 初始化 session state
    if 'question_input' not in st.session_state:
        st.session_state.question_input = ""
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    # 標題區
    st.title("🏛️ 古代思想家風格的 AI 思考生成器")
    st.markdown("""
    ### 運用 Two-Stage Chain-of-Thought 技術
    讓 AI 模擬 **老子**、**孔子**、**管仲** 三位古代思想家的思維方式，為你的問題提供不同視角的智慧建議。
    """)
    
    # API Key 設定
    api_key = get_api_key()
    
    # 側邊欄設定
    with st.sidebar:
        st.header("⚙️ 設定")
        
        if not api_key:
            api_key = st.text_input(
                "請輸入 Groq API Key",
                type="password",
                help="前往 https://console.groq.com 取得 API Key"
            )
        else:
            st.success("✅ API Key 已設定")
        
        st.divider()
        
        # 思想家簡介卡片
        st.markdown("### 📖 思想家簡介")
        for name, info in THINKERS.items():
            with st.expander(f"{info['icon']} {name}"):
                st.markdown(f"**{info['short_desc']}**")
                st.markdown(f"核心觀念：{info['core_concepts']}")
                # 顯示一則名言
                quote = random.choice(QUOTES[name])
                st.markdown(f"> 📜 *「{quote}」*")
        
        st.divider()
        
        # 歷史紀錄
        if st.session_state.history:
            st.markdown("### 📜 歷史紀錄")
            for i, item in enumerate(st.session_state.history[-5:]):  # 只顯示最近5筆
                with st.expander(f"Q: {item['question'][:20]}..."):
                    st.write(f"**思想家**: {item['thinker']}")
                    st.write(f"**時間**: {item.get('time', 'N/A')}")
    
    st.divider()
    
    # ===== 範例問題區 =====
    st.markdown("#### 💡 點擊範例問題快速填入：")
    cols = st.columns(4)
    for i, example in enumerate(EXAMPLE_QUESTIONS[:8]):
        with cols[i % 4]:
            if st.button(f"📌 {example[:12]}...", key=f"example_{i}", use_container_width=True):
                st.session_state.question_input = example
                st.rerun()
    
    st.divider()
    
    # ===== 主要輸入區 =====
    col1, col2 = st.columns([2, 1])
    
    with col1:
        question = st.text_area(
            "💭 請輸入你的問題或困境",
            placeholder="例如：我要如何讓新團隊快速運作起來？",
            height=100,
            key="question_input"
        )
    
    with col2:
        mode = st.radio(
            "🎯 選擇模式",
            ["單一思想家", "🔥 三位思想家比較"],
            help="比較模式會同時顯示三位思想家對同一問題的不同觀點"
        )
        
        if mode == "單一思想家":
            thinker_style = st.selectbox(
                "🎭 選擇思想家",
                options=list(THINKERS.keys()),
                format_func=lambda x: f"{THINKERS[x]['icon']} {x}"
            )
    
    # 生成按鈕
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        if mode == "單一思想家":
            generate_btn = st.button("🚀 開始生成智慧建議", type="primary", use_container_width=True)
        else:
            generate_btn = st.button("🔥 比較三位思想家觀點", type="primary", use_container_width=True)
    
    # ===== 執行生成 =====
    if generate_btn:
        if not api_key:
            st.error("❌ 請先設定 Groq API Key！")
        elif not question.strip():
            st.warning("⚠️ 請輸入問題！")
        else:
            st.divider()
            
            if mode == "單一思想家":
                # ===== 單一思想家模式（串流輸出）=====
                thinker = THINKERS[thinker_style]
                
                # 顯示經典名言
                quote = random.choice(QUOTES[thinker_style])
                st.markdown(f"""
                <div class="quote-box">
                    📜 「{quote}」<br>
                    <small>—— {thinker_style.split('（')[0]}</small>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"## {thinker['icon']} {thinker_style} 的智慧回應")
                
                col_result1, col_result2 = st.columns(2)
                
                with col_result1:
                    st.markdown("### 🧠 他是這樣想的...")
                    stage1_placeholder = st.empty()
                
                with col_result2:
                    st.markdown("### 💬 給你的建議")
                    stage2_placeholder = st.empty()
                
                # 串流生成
                with st.spinner("🧠 正在進行深度思考..."):
                    reasoning, advice = ancient_thinker_generate_stream(
                        question, thinker_style, api_key,
                        stage1_placeholder, stage2_placeholder
                    )
                
                # 儲存歷史
                from datetime import datetime
                st.session_state.history.append({
                    "question": question,
                    "thinker": thinker_style,
                    "reasoning": reasoning,
                    "advice": advice,
                    "time": datetime.now().strftime("%H:%M:%S")
                })
                
            else:
                # ===== 三位思想家比較模式 =====
                st.markdown("## 🔥 三位思想家的智慧比較")
                st.markdown(f"**問題：** {question}")
                st.divider()
                
                # 建立三個 Tab
                tabs = st.tabs([f"{info['icon']} {name}" for name, info in THINKERS.items()])
                
                results = {}
                
                for i, (thinker_name, thinker_info) in enumerate(THINKERS.items()):
                    with tabs[i]:
                        # 顯示經典名言
                        quote = random.choice(QUOTES[thinker_name])
                        st.markdown(f"""
                        <div style="background-color: {thinker_info['bg_color']}; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                            📜 「{quote}」<br>
                            <small style="color: {thinker_info['color']};">—— {thinker_name.split('（')[0]}</small>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        with st.spinner(f"🧠 {thinker_info['icon']} 正在思考中..."):
                            reasoning, advice = ancient_thinker_generate(
                                question, thinker_name, api_key
                            )
                            results[thinker_name] = {"reasoning": reasoning, "advice": advice}
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("#### 🧠 他是這樣想的...")
                            st.info(reasoning)
                        with col2:
                            st.markdown("#### 💬 給你的建議")
                            st.success(advice)
                
                # 儲存歷史
                from datetime import datetime
                st.session_state.history.append({
                    "question": question,
                    "thinker": "三位比較",
                    "results": results,
                    "time": datetime.now().strftime("%H:%M:%S")
                })
            
            # 完成訊息
            st.divider()
            
            # 複製按鈕提示
            st.markdown("""
            ✨ **生成完成！** 
            
            💡 **提示**：
            - 選取文字後可以複製分享
            - 試試「三位思想家比較」模式，看看不同觀點的差異！
            """)
    
    # 頁尾
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: gray; font-size: 0.8em;">
    🏛️ 古代思想家 AI 思考生成器 v2.0 | Two-Stage CoT Demo | Powered by Groq<br>
    ✨ 功能：串流輸出 | 三位思想家比較 | 經典名言引用 | 歷史紀錄
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
