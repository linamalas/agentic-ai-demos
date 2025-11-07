import streamlit as st 
from workflow import app



st.title("Agent Recipe Generator +Critic")


topic=st.text_input("What recipe do you want?")
preferences=st.text_input("Any preferences? (opitional)")

if st.button("Generate Recipe"):
    state={
        "recipe":None,
        "feedback":None,
        "history":[],
        "topic":topic,
        "preferences":preferences
    }
    
    st.subheader("Converation History")
    
    with st.container():
        final_state=app.invoke(state)
        
    if "no further refinement is needed" in final_state["feedback"].lower():
        st.success("Recipe approved! No further refinement needed.")
