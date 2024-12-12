import collections, sys
import streamlit as st; ss = st.session_state
from .util_uid import get_identity

def init_resource():
    st.set_page_config(
        page_title="PDL Agent",
        page_icon="🍊",
        initial_sidebar_state="auto",
        menu_items={
            # 'Get Help': 'https://www.extremelycoolapp.com/help',
            'Report a bug': "mailto:easonsshi@tencent.com",
            # 'About': "# This is a header. This is an *extremely* cool app!"
        }
    )
    st.title('️🍊 PDL Agent')
    # 设置sidebar默认width
    setting_stype = """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"]{
        min-width: 300px;
        max-width: 1000px;
        width: 500px;
    }
    """
    st.markdown(setting_stype, unsafe_allow_html=True)

    # bot_icon = Image.open('resource/icon.png')
    if 'avatars' not in ss:
        ss['avatars'] = collections.defaultdict(lambda: "🤖")
        ss['avatars'] |= {
            # 'ian': bot_icon,
            'system': '⚙️', # 🖥️
            'user': '💬',   # 🧑‍💻 👤 🙂 🙋‍♂️ / 🙋‍♀️
            'assistant': '🤖',
            'bot': '🤖',
        }
    if 'tool_emoji' not in ss:
        ss['tool_emoji'] = collections.defaultdict(lambda: "⚙️")
        ss['tool_emoji'] |= {
            "search": "🔍",
            "web_search": "🔍",
            "search_news": "🔍",
            "search_images": "🔍",
            "think": "🤔",
            "web_logo": "🌐",
            "warning": "⚠️",
            "analysis": "💡",
            "success": "✅",
            "doc_logo": "📄",
            "calc_logo": "🧮",
            "code_logo": "💻",
            "code_logo": "python_executor",
            'default_tool': "⚙️"
        }

    if "headers" not in ss:
        headers = st.context.headers
        user_identity = get_identity(headers, app_id="MAWYUI3UXKRDVJBLWMQNGUBDRE5SZOBL")
        # print(f"user_identity: {user_identity}")
        ss.headers = headers
        ss.user_identity = user_identity

def set_global_exception_handler():
    """ Set global exception handler for Streamlit. 
    NOTE: only work for streamlit of low version.
    from: /apdcephfs_cq8/share_2992827/shennong_5/ianxxu/chatchat/_TaskPlan/UI/v2.1/IanAGI.py
    """
    def exception_handler(e):
        import traceback
        # Custom error handling
        st.image("https://media1.tenor.com/m/t7_iTN0iYekAAAAd/sad-sad-cat.gif")
        st.error(f"Oops, something funny happened with a {type(e).__name__}", icon="😿")
        print(traceback.format_exc())
        st.warning(traceback.format_exc())

    from streamlit.runtime.scriptrunner.script_runner import handle_uncaught_app_exception
    handle_uncaught_app_exception.__code__ = exception_handler.__code__


def set_streamlit():
    # set_global_exception_handler()
    pass
