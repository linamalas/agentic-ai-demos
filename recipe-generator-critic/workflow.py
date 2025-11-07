from typing import TypedDict,List, Optional
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os 
import streamlit as st 

from langgraph.graph import StateGraph,END

load_dotenv()


class RecipeState(TypedDict):
    recipe:Optional[str]
    feedback:Optional[str]
    history:List[str]
    topic:str
    preferences:Optional[str]
    




llm=ChatOpenAI(model="gpt-4o-mini",temperature=0.7)

def recipe_agent(state:RecipeState,container=None):
    
    stream_text=""
    prompt=f"Create a detiled recipe for:{state['topic']}"
    if state["preferences"]:
        prompt+=f"\nUser preferences:{state['preferences']}"
    
    if state["feedback"]:
        prompt+=f"\nRefine the recipe based on this feedback:{state['feedback']}"
    
    if container is None:
        container=st.empty()
        
    for chunk in llm.stream(prompt):
        stream_text+=chunk.content
        container.markdown(
            f"""
            <div style='background-color:#f0fdf4;
                        color:#1a1a1a;
                        padding:15px;
                        border-left:5px solid #16a34a;
                        border-radius:5px;
                        margin-bottom:10px;'>
                🧑‍🍳 <b>Recipe Agent:</b><br>{stream_text}
            </div>
            """,
            unsafe_allow_html=True
        )
    #response=llm.invoke(prompt)
    
    return{
        "recipe":stream_text,
        "feedback":None,
        "history":state["history"]+["Recipe Agent:"+stream_text]
    }
    
def critic_agent(state:RecipeState,container=None):
    stream_text=""
    recipe_text=state["recipe"]
    prompt=f"""   
    Review the following recipe for:
    - Nutritional balance
    - Clarity (easy to follow)
    - Feasibility (ingredients,steps realistic)
    if the recipe is already good enough, say exactly:
    "No further refinement is needed."
    Recipe:
    {recipe_text}
    
    """
    if container is None:
        container=st.empty()
        
    for chunk in llm.stream(prompt):
        stream_text+=chunk.content
        container.markdown(
            f"""
            <div style='background-color:#fffbea;
                        color:#1a1a1a;
                        padding:15px;
                        border-left:5px solid #ca8a04;
                        border-radius:5px;
                        margin-bottom:10px;'>
                📝 <b>Critic Agent:</b><br>{stream_text}
            </div>
            """,
            unsafe_allow_html=True
        )



    return{
        "recipe":state["recipe"],
        "feedback":stream_text,
        "history":state["history"]+["Critic Agent:" + stream_text]
    }
    
MAX_CYCLES=5
def should_continue(state:RecipeState):
    history_len=len(state["history"])
    if state["feedback"] and "no further refinement is needed" in state["feedback"].lower():
        return "end"
    if history_len>=MAX_CYCLES*2:
        return"end"
    return "loop"
    
    
    
    
    
workflow=StateGraph(RecipeState)

workflow.add_node("recipe_agent",recipe_agent)
workflow.add_node("critic_agent",critic_agent)

workflow.add_edge("recipe_agent","critic_agent")
workflow.add_conditional_edges(
    "critic_agent",
    should_continue,
    {
        "end":END,
        "loop":"recipe_agent"
    }
)
workflow.set_entry_point("recipe_agent")

app=workflow.compile()


    
# for manual testing 
"""
state={
        "recipe":None,
        "feedback":None,
        "history":[],
        "topic":"Chicken Dinner"
    
}


state=recipe_agent(state)

print("===Recipe Agent Output===")
print("Recipe:\n",state["recipe"])
print("History:",state["history"])

state=critic_agent(state)
print("\n===Critic Agent Output==")
print("Feedback:\n",state["feedback"])
print("History:",state["history"])


topic=input("what recipe do you want?\n")

preferences=input("do you have any preferences?\n")

state={
    "recipe":None,
    "feedback":None,
    "history":[],
    "topic":topic,
    "preferences":preferences
}

final_state=app.invoke(state)


print("\n===Conversation History ===")
for entry in final_state['history']:
    print(entry)
    print("-"*40)
"""
