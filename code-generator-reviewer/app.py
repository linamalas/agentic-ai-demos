import streamlit as st
from workflow import app
from graphviz import Digraph
st.title("Code Generator +Reviewer")

if "review_state" not in st.session_state:
    st.session_state.review_state={
        "task":None,
        "code":None,
        "style_guide":None,
        "focus":None,
        "initial_review":None,
        "reflection":None,
        "final_review":None,
        "improved_code":None,
        "history":[],
        "needs_refinement":False,
    }

mode=st.radio("Choose mode:",["Generate from Task","Review Existing Code"])

if mode=="Generate from Task":
    task=st.text_area("Enter the programming task:",height=120)
    st.session_state.review_state["task"]=task
    st.session_state.review_state["code"]=None
else:
    code=st.text_area("Paste your code here:",height=200)
    st.session_state.review_state["code"]=code
    st.session_state.review_state["task"]=None
    
style_guide=st.text_input("Style Guide (e.g, PEP8,Airbnb JS)")
focus=st.text_input("Focus (e.g.,performance,readability,security)")

st.session_state.review_state['style_guide']=style_guide
st.session_state.review_state['focus']=focus


if st.button("Run Review"):
    result=app.invoke(st.session_state.review_state)
    st.session_state.review_state.update(result)
    if st.session_state.review_state["final_review"]:
        st.subheader("Final Review Report")
        st.markdown(st.session_state.review_state["final_review"])
    if st.session_state.review_state['improved_code']:
        st.subheader("Improved Code")
        st.code(st.session_state.review_state['improved_code'],language='python')
    
    
if st.session_state.review_state['history']:
    with st.expander("Review History"):
        for i, entry in enumerate(st.session_state.review_state['history'],start=1):
            st.markdown(f"**Round {i}:**\n\n{entry}")


