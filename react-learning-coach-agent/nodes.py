import json
import re
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from state import GraphState
from tools import fetch_docs, analyze_code_snippet

llm = ChatOpenAI(model="gpt-4o-mini")

# --- Onboarding Node ---
def onboarding_node(state: GraphState) -> GraphState:
    # If already onboarded, skip to coaching
    if state.get("status") not in ["onboarding", ""]:
        return state
    
    last_msg = state["messages"][-1]
    user_text = last_msg.content

    system = SystemMessage(content=(
        "React/TypeScript project coach. Extract ONLY valid JSON:\n"
        '{"project_summary": "brief description", '
        '"features": ["feature1", "feature2"], '
        '"assumed_level": "beginner" | "intermediate" | "advanced"}\n'
        "Assume 'beginner' if unclear. No extra text."
    ))

    resp = llm.invoke([system, HumanMessage(content=user_text)])
    content = resp.content.strip().replace("```json", "").replace("```", "")

    try:
        data = json.loads(re.search(r'\{.*\}', content, re.DOTALL).group(0))
    except Exception:
        data = {"project_summary": user_text, "features": ["basic app"], "assumed_level": "beginner"}

    state["project_spec"] = {"summary": data["project_summary"], "features": data["features"]}
    state["learner_profile"] = {"assumed_level": data["assumed_level"]}
    state["status"] = "onboarding_complete"

    level_desc = {
        "beginner": "new to React/TypeScript (detailed fundamentals)",
        "intermediate": "knows basics (best practices focus)",
        "advanced": "experienced (advanced patterns)"
    }

    msg = (
        f"✅ **Project Confirmed**\n\n"
        f"**Build:** {data['project_summary']}\n\n"
        f"**Features:** {', '.join(data['features'])}\n\n"
        f"**Level:** {data['assumed_level'].title()} - {level_desc[data['assumed_level']]}\n\n"
        f"💡 Say 'I'm actually [level]' to adjust\n\n"
        f"Creating learning plan..."
    )
    state["messages"].append(AIMessage(content=msg))
    return state

# --- Planning Node ---
def planning_node(state: GraphState) -> GraphState:
    spec = state["project_spec"]
    level = state["learner_profile"]["assumed_level"]
    is_replan = state.get("status") == "replan"

    system = SystemMessage(content=(
        f"React/TS planner for {level} learners. 4-6 stages covering {spec['features']}.\n"
        "Each stage: name, goal, tasks[], fundamentals[], docs[], features[].\n"
        f"JSON only:\n"
        '{"stages": [{"name": "...", "goal": "...", "tasks": [...], '
        '"fundamentals": [...], "docs": [...], "features": [...]}]}'
    ))

    resp = llm.invoke([
        system,
        HumanMessage(content=f"Project: {spec['summary']}\nFeatures: {spec['features']}\nLevel: {level}")
    ])

    content = resp.content.strip().replace("```", "")
    try:
        data = json.loads(re.search(r'\{.*\}', content, re.DOTALL).group(0))
        state["stages"] = data["stages"]
    except Exception:
        state["stages"] = [{"name": "Setup", "goal": "Basic app", "tasks": [], "fundamentals": [], "docs": [], "features": spec["features"]}]

    if not is_replan:
        state["current_stage_index"] = 0

    current = state.get("current_stage_index", 0) + 1
    if is_replan:
        header = f"## 🔄 Updated Learning Plan\n**Current: Stage {current}\n\n**Stages:**\n\n"
        footer = f"\n✅ Features integrated!\nSay **'continue'** or **'go to stage X'**"
    else:
        header = "## 📘 Learning Plan\n\n"
        footer = (
            "\n## 💬 Commands:\n"
            "**Nav:** continue/start • done/next • go to stage X\n"
            "**Learn:** exercises • questions\n"
            "**Plan:** add feature • I'm actually [level]\n\n"
            "Ready? **'continue'**!"
        )

    plan_text = header
    for i, stage in enumerate(state["stages"], 1):
        marker = " ← **YOU ARE HERE**" if is_replan and i == current else ""
        feats = f" ({', '.join(stage.get('features', []))})" if stage.get('features') else ""
        plan_text += f"**Stage {i}: {stage['name']}**{marker}{feats}\n  Goal: {stage['goal']}\n\n"

    state["messages"].append(AIMessage(content=plan_text + "---" + footer))
    state["status"] = "coaching"
    return state

# --- Coaching Node ---
def coaching_node(state: GraphState) -> GraphState:
    # Only process human messages, skip if last message is from AI
    if not state["messages"] or state["messages"][-1].type != "human":
        return state
    
    stages = state.get("stages", [])
    idx = state.get("current_stage_index", 0)
    level = state["learner_profile"].get("assumed_level", "beginner")

    if idx >= len(stages):
        state["status"] = "finished"
        state["messages"].append(AIMessage("🎉 **Complete!** You've built your project! 🚀"))
        return state

    stage = stages[idx]
    msg = state["messages"][-1].content.lower()

    if "go to stage" in msg or "jump to stage" in msg:
        match = re.search(r'stage\s+(\d+)', msg)
        if match:
            try:
                target = int(match.group(1)) - 1
                if 0 <= target < len(stages):
                    state["current_stage_index"] = target
                    new_stage = stages[target]
                    state["messages"].append(AIMessage(
                        f"📍 **Jumped to Stage {target+1}/{len(stages)}: {new_stage['name']}**\n"
                        f"**Goal:** {new_stage['goal']}\n"
                        f"**Features:** {', '.join(new_stage.get('features', []))}\n\n"
                        f"💬 `continue`=instructions, `exercises`=practice"
                    ))
                    state["status"] = "coaching"
                    return state
            except ValueError:
                pass

    if "i'm actually" in msg or "i am actually" in msg:
        for lvl in ["beginner", "intermediate", "advanced"]:
            if lvl in msg:
                state["learner_profile"]["assumed_level"] = lvl
                state["status"] = "replan"
                state["messages"].append(AIMessage(
                    f"✅ **{lvl.title()}** level activated!\n🔄 Replanning..."
                ))
                return state

    if "done with exercise" in msg or "done with exercises" in msg:
        state["messages"].append(AIMessage(
            f"✅ **Exercises complete!** Stage {idx+1}/{len(stages)}: {stage['name']}\n\n"
            f"• `continue` = instructions\n• `exercises` = more\n• `done` = next\n• `go to stage X`"
        ))
        state["status"] = "coaching"
        return state

    if any(x in msg for x in ["done", "next stage", "move on"]):
        if "exercise" not in msg:
            state["current_stage_index"] += 1
            if state["current_stage_index"] >= len(stages):
                state["status"] = "finished"
                state["messages"].append(AIMessage(
                    f"🎉 **All Done!** Built: **{state['project_spec']['summary']}** 🚀"
                ))
            else:
                next_stage = stages[state["current_stage_index"]]
                state["messages"].append(AIMessage(
                    f"✅ **Stage {idx+1} Complete!**\n\n"
                    f"**Next: Stage {state['current_stage_index']+1}/{len(stages)}**\n"
                    f"**{next_stage['name']}** - {next_stage['goal']}\n\n"
                    f"💬 `continue`=`start`, `go to stage X`=`jump`, `exercises`=`practice`"
                ))
        state["status"] = "coaching"
        return state

    if "add feature" in msg:
        feature = re.split(r'add feature[:\s]+', msg, flags=re.I)[1].strip() if "add feature" in msg else "new feature"
        state["project_spec"]["features"].append(feature)
        state["status"] = "replan"
        state["messages"].append(AIMessage(
            f"🔄 **Adding: {feature}**\n"
            f"📍 Stage {idx+1}/{len(stages)}\n"
            f"🔄 Replanning to integrate..."
        ))
        return state

    if "exercise" in msg or "practice" in msg:
        topic = msg.split("for ", 1)[1].strip() if "for " in msg else None
        system = SystemMessage(content=(
            f"{level.title()} React/TS coach. 3 progressive exercises for stage '{stage['name']}'.\n"
            "## 🏋️ Exercises\n**Ex 1:**\n- Task\n- Verify\n\n**Ex 2:**\n...\n\n## 💡 Hints\n...\n\n"
            "'done with exercises'=stay, 'done'=next stage"
        ))
        resp = llm.invoke([system, HumanMessage(content=f"Stage: {stage['name']} | Topic: {topic or 'fundamentals'}")])
        
        state["messages"].append(AIMessage(
            f"📍 **Stage {idx+1}/{len(stages)}: {stage['name']}**\n\n{resp.content}"
        ))
        state["status"] = "coaching"
        return state

    # Check if user is sharing code for review
    if "```" in state["messages"][-1].content:
        # Extract code from message (find code block)
        code_match = re.search(r'```(?:javascript|typescript|jsx|tsx|js|ts)?\s*\n(.*?)```', 
                               state["messages"][-1].content, re.DOTALL)
        if code_match:
            code = code_match.group(1).strip()
            stage_info = f"Stage: {stage['name']}\nGoal: {stage['goal']}\nFundamentals: {', '.join(stage.get('fundamentals', []))}"
            
            try:
                feedback = analyze_code_snippet(code, stage_info)
                
                state["messages"].append(AIMessage(
                    f"📍 **Stage {idx+1}/{len(stages)}: {stage['name']}**\n\n"
                    f"## 🔍 Code Review\n\n"
                    f"**Issues Found:**\n{feedback.get('issues', 'None detected')}\n\n"
                    f"**Concepts to Review:**\n{feedback.get('suggested_fundamentals', 'N/A')}\n\n"
                    f"**💡 Hint:**\n{feedback.get('high_level_hint', 'Keep practicing!')}\n\n"
                    f"---\n💬 `continue` for more help • `exercises` for practice • `done` when ready"
                ))
                state["status"] = "coaching"
                return state
            except Exception as e:
                # If code analysis fails, fall through to default coaching
                pass

    # Default coaching or questions
    docs = fetch_docs(" ".join(stage.get("fundamentals", [])))
    docs_text = "\n".join(f"- {d['topic']}: {d['link']}" for d in docs[:3]) or "No docs"

    system = SystemMessage(content=(
        f"{level.title()} React/TS coach. Stage: {stage['name']}.\n"
        "## 📋 Instructions (3-5 steps w/ `bash` blocks)\n"
        "## 🎯 Foundations (2-4 bullets)\n"
        "## 📚 Docs\n{docs_text}\n"
        "## 💡 Example (5 lines max)\n"
        "## ❓ `continue`/`exercises`/`done`/`go to stage X`"
    ))
    
    resp = llm.invoke([system, HumanMessage(content=f"User: {msg}\nStage: {stage['name']}")])
    
    state["messages"].append(AIMessage(
        f"📍 **Stage {idx+1}/{len(stages)}: {stage['name']}**\n"
        f"*Goal: {stage['goal']}*\n\n---\n\n{resp.content}"
    ))
    state["status"] = "coaching"
    return state

# --- Routing Node ---
def route_next_node(state: GraphState) -> str:
    """Route based on status to next node."""
    status = state.get("status", "coaching")
    if status == "finished":
        return "finished"
    if status in ["planning", "replan"]:
        return "planning"
    return "coaching"
