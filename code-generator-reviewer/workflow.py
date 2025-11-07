from typing import TypedDict,Optional,List
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.graph import StateGraph,END
import re
load_dotenv()
class ReviewState(TypedDict):
    task:str
    code:str
    style_guide:Optional[str]
    focus:Optional[str]
    initial_review:Optional[str]
    reflection:Optional[str]
    final_review:Optional[str]
    improved_code:Optional[str]
    history:List[str]
    needs_refinement:bool
    
    
llm=ChatOpenAI(model="gpt-4o-mini",temperature=0.3)


def generate_code_agent(state:ReviewState):
    prompt=f"""Write code for the following task:
    {state['task']}
    Language:Python
    Keep it simple,clean, and efficient.
    """
    code=llm.invoke(prompt).content
    return{"code":code}

def review_agent(state:ReviewState):
    prompt=f""" 
    You are a code reviewer.
    Review the following code:
    {state['code']}
    Style guide:{state.get('style_guide','None')}
    Focus:{state.get('focus','General')}
    Give feedback on:
    - Correctness
    - Style / Readability
    - Performance (Time complexity & Space complexity)
    - Security
    - Suggestions
    
    At the end, state clearly:"REFINEMENT NEEDED: YES" or "REFINEMENT NEEDED: NO".
    """
    review=llm.invoke(prompt).content
    needs_refinement="YES" in review.upper()
    state['history'].append(f"Initial Review:\n{review}")
    return {"initial_review":review,"needs_refinement":needs_refinement,"history":state['history']}
def reflect_agent(state:ReviewState):
    past_reviews="\n".join(state['history']) if state['history'] else "None"
    prompt=f"""
    here is the current review:
    {state['initial_review']}
    Past review history:
    {past_reviews}
    Reflect on the current review. Did I miss anything compared to earlier reviews?
    Add improvements or corrections if needed.
    
    """
    reflection=llm.invoke(prompt).content
    state["history"].append(f"Reflection:\n{reflection}")
    return {"reflection":reflection,"history":state["history"]}

def finalize_agent(state:ReviewState):
    prompt=f"""
    Combine the initial review and reflection into a final structure report.
    At the end of your report, ALWAYS include an "Improved Code" section.
    - if the original code is already optimal, repeat it under this section.
    - if changes were suggested, show the improved version instead.
    Only include ONE final version of the code inside a python code block
    Code to review:
    {state['code']}
    Initial Review:
    {state['initial_review']}
    Reflection:
    {state['reflection']}
    """
    final_output=llm.invoke(prompt).content
    code_blocks=re.findall(r"```(?:python)?\n([\s\S]*?)```",final_output)
    improved_code=code_blocks[0].strip() if code_blocks else None
    
    state['history'].append(f"Final Report:\n{final_output}")
    
    
    return {"final_review":final_output,"improved_code":improved_code,"history":state['history']}

def choose_path(state:ReviewState):
    if state.get("code"):
        return "review"
    elif state.get("task"):
        return "generate"
    else:
        raise ValueError("State must include either code or task")
    
def refine_review(state:ReviewState,new_focus:Optional[str]=None):
    if new_focus:
        state["focus"]=new_focus
    state['code']=state.get("improved_code",state['code'])
    return app.invoke(state,start_at="review")
    
    
def check_refinement(state:ReviewState):
    if state.get("needs_refinement"):
        return "reflect"
    else:
        return "finalize"
    
    

graph=StateGraph(ReviewState)

graph.add_node("generate",generate_code_agent)
graph.add_node("review",review_agent)
graph.add_node("reflect",reflect_agent)
graph.add_node("finalize",finalize_agent)
graph.add_node("start",lambda state:state)

graph.set_entry_point("start")
graph.add_conditional_edges("start",choose_path,{"generate":"generate","review":"review"})
graph.add_edge("generate","review")
graph.add_conditional_edges("review",check_refinement,{
    "reflect":"reflect",
    "finalize":"finalize"
})
graph.add_edge("reflect","finalize")
graph.add_edge("finalize",END)


app=graph.compile()