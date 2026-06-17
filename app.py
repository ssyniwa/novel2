import streamlit as st
import json

# --- 1. 設定・データ読み込み ---
def load_scenario():
    with open("scenario.json", "r", encoding="utf-8") as f:
        return json.load(f)

try:
    SCENARIO_DATA = load_scenario()
except:
    SCENARIO_DATA = {}

# --- 2. ゲーム状態の初期化 ---
def init_game():
    st.session_state.page = 'select_char'
    st.session_state.char = None
    st.session_state.current_scene = "start"
    st.session_state.params = {"勇気": 0, "知識": 0, "体力": 0}
    st.session_state.flags = {}
    st.session_state.skills = []  # スキルリストを初期化

if 'page' not in st.session_state:
    init_game()

# --- 3. メイン画面の構築 ---
st.title("Thunder Witch: Serina's Story")

# キャラクター選択画面
if st.session_state.page == 'select_char':
    st.write("キャラクターを選択してください：")
    cols = st.columns(3)
    if cols[0].button("セリナ"):
        st.session_state.char = "セリナ"
        st.session_state.page = 'game'
        st.session_state.current_scene = "start"
        st.rerun()

# ゲーム進行画面
elif st.session_state.page == 'game':
    char_data = SCENARIO_DATA.get(st.session_state.char, {})
    node = char_data.get(st.session_state.current_scene)

    if node:
        if "image" in node:
            st.image(node["image"], use_container_width=True)
        
        st.write(node["text"])
        
        for opt in node.get("options", []):
            if st.button(opt["label"]):
                # パラメータ加算
                if "effect" in opt:
                    for k, v in opt["effect"].items():
                        st.session_state.params[k] += v
                
                # フラグ更新
                if "flag" in opt:
                    for k, v in opt["flag"].items():
                        st.session_state.flags[k] = v
                
                # スキル習得処理
                if "add_skill" in opt:
                    new_skill = opt["add_skill"]
                    if new_skill not in st.session_state.skills:
                        st.session_state.skills.append(new_skill)
                
                # 次のシーンへ遷移
                st.session_state.current_scene = opt["next"]
                
                if opt["next"].startswith("ending"):
                    st.session_state.page = "result"
                
                st.rerun()
    else:
        st.error("シーンデータが見つかりません。")

# 結果表示画面
elif st.session_state.page == 'result':
    # 簡易的にシーンデータが存在すれば表示
    char_data = SCENARIO_DATA.get(st.session_state.char, {})
    node = char_data.get(st.session_state.current_scene, {})
    
    if "image" in node:
        st.image(node["image"], use_container_width=True)
    st.write(node.get("text", "物語は完結しました。"))
    
    st.subheader("結末")
    st.write(f"最終結果: {st.session_state.current_scene}")
    st.write(f"最終ステータス: {st.session_state.params}")
    st.write(f"習得スキル: {', '.join(st.session_state.skills)}")
    
    if st.button("タイトルへ戻る"):
        init_game()
        st.rerun()

# サイドバーにステータス・フラグ・スキルを表示
st.sidebar.write("### Status")
st.sidebar.json(st.session_state.params)
st.sidebar.write("### Flags")
st.sidebar.json(st.session_state.flags)
st.sidebar.write("### Learned Skills")
if st.session_state.skills:
    for skill in st.session_state.skills:
        st.sidebar.write(f"{skill}")
else:
    st.sidebar.write("まだスキルはありません")
