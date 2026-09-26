import streamlit as st


def hide_sidebar():
    st.markdown("""
     <style>
            [data-testid='stSidebar'] {display: none;}
            [data-testide='stSidebarNav'] {display: none;}
    </style>
    """, unsafe_allow_html=True
                )