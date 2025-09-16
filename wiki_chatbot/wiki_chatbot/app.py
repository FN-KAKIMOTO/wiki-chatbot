"""Wiki ChatbotのメインStreamlitアプリケーションエントリーポイント。

このモジュールはWiki Chatbotアプリケーションのメインウェブインターフェースを提供し、
認証、ナビゲーション、コアチャット機能を含みます。
"""

import os
import sys

# パスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

from config.web_settings import WebConfig, initialize_web_config
from utils.chatbot import WikiChatbot
from utils.session_manager import SessionManager


def main() -> None:
    """メインStreamlitアプリケーションを初期化・実行する。

    この関数は以下を処理します：
    - Web設定の初期化と検証
    - ページ設定のセットアップ
    - 認証フロー
    - 異なるページ間のナビゲーション（チャット、管理画面、設定）
    - セッション管理とステータス表示

    Returns:
        None
    """
    # Web設定の初期化
    is_valid, errors = initialize_web_config()

    # アプリ設定取得
    app_config = WebConfig.get_app_config()

    st.set_page_config(page_title=app_config["app_title"], page_icon="💬", layout="wide")

    # 設定エラーがある場合の警告表示
    if not is_valid:
        st.error("⚠️ 設定エラー:")
        for error in errors:
            st.error(f"• {error}")
        st.stop()

    # セッション管理初期化
    SessionManager.initialize_session()

    # 認証チェック
    if not SessionManager.check_authentication():
        if not SessionManager.authenticate_user():
            return

    # サイドバーナビゲーション
    st.sidebar.title("📚 Wiki Chatbot")
    st.sidebar.markdown("---")

    page = st.sidebar.selectbox("ページを選択", ["💬 チャット", "🛠️ 管理画面", "⚙️ 設定"])

    if page == "🛠️ 管理画面":
        # 管理画面をインポートして実行
        from pages.admin import main as admin_main

        admin_main()
    elif page == "⚙️ 設定":
        # 設定画面をインポートして実行
        from pages.settings import main as settings_main

        settings_main()
    else:
        # チャット機能
        chatbot = WikiChatbot()

        # 商材が選択されている場合はチャット画面を表示
        if "selected_product" in st.session_state and st.session_state["selected_product"]:
            product_name = st.session_state["selected_product"]

            # 戻るボタン
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("← 商材選択に戻る"):
                    if "selected_product" in st.session_state:
                        del st.session_state["selected_product"]
                    st.rerun()

            with col2:
                st.write(f"**現在の商材:** {product_name}")

            st.divider()

            # 現在の設定表示
            chatbot.show_current_settings()

            # チャット履歴クリアボタン（サイドバー）
            st.sidebar.markdown("---")
            st.sidebar.subheader("🗑️ チャット管理")
            chatbot.clear_chat_history(product_name)

            # クエリ制限チェック
            if not SessionManager.check_query_limit():
                st.stop()

            # チャット画面
            chatbot.chat_interface(product_name)

        else:
            # 商材選択画面
            chatbot.product_selection_interface()

    # セッション状態表示
    SessionManager.display_session_status()

    # サイドバーの説明
    st.sidebar.markdown("---")
    st.sidebar.subheader("📖 このアプリについて")
    st.sidebar.write(
        """
    **社内Wiki検索チャットボット** は、RAG（Retrieval-Augmented Generation）技術を使用して、社内文書から適切な情報を検索し、質問に回答するシステムです。

    **主な機能:**
    - 商材ごとのRAGデータベース管理
    - 文書のアップロード・削除
    - 自然言語での質問応答
    - 情報源の表示
    """
    )

    # API Key設定のガイド
    if page == "💬 チャット":
        st.sidebar.markdown("---")
        st.sidebar.subheader("⚙️ 設定")
        st.sidebar.write(
            """
        **OpenAI API Key** が必要です。

        取得方法:
        1. [OpenAI Platform](https://platform.openai.com/) にアクセス
        2. API Keyを取得
        3. 下記に入力
        """
        )


if __name__ == "__main__":
    main()
