from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from tavily import TavilyClient
import arxiv
from dotenv import load_dotenv
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from langgraph.types import Command

load_dotenv()
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

class ResearchState(TypedDict):
    query: str
    keywords: str
    tasks: List[str]
    research_results: List[Dict]
    draft_report: str
    final_report: str
    approved: bool

def coordinator_agent(state):
    if not state.get("tasks"):
        goto = "planner"
    elif not state.get("research_results"):
        goto = "researcher"
    elif not state.get("draft_report"):
        goto = "reporter"
    elif not state.get("approved"):
        goto = "human_review"
    else:
        goto = END

    return Command(update={}, goto=goto)
    
keyword_prompt = PromptTemplate.from_template(
"""
Extract the research keywords from the query.
Remove question words and meaningless words (e.g., what, how, explain, tell).

Query:
{query}

Return only keywords separated by commas.
"""
)

planner_prompt = PromptTemplate.from_template(
"""
You are a research planner.

Based on the following research keywords, generate a list of simple research tasks.

Keywords:
{keywords}

Return a numbered list of tasks, and do not include any additional text only tasks in the list.
"""
)

def planner_agent(state):

    keyword_prompt_text = keyword_prompt.format(query=state["query"])
    keyword_response = llm.invoke(keyword_prompt_text)

    keywords = keyword_response.content.strip()
    print("\nExtracted keywords:", keywords)

    planner_prompt_text = planner_prompt.format(keywords=keywords)
    response = llm.invoke(planner_prompt_text)

    tasks = []
    for line in response.content.split("\n"):
        line = line.strip()
        if not line:
            continue

        line = re.sub(r'^\d+\.\s*', '', line)
        line = line.replace("**", "").replace(":", "")

        tasks.append(line)

    print("\nGenerated tasks:", tasks)

    return {
        "keywords": keywords,
        "tasks": tasks
    }


def search_tavily(query):
    try:
        results = tavily.search(query=query, max_results=3)
        return [{"text": r["content"], "url": r.get("url","")} for r in results.get("results",[])]
    except:
        return []

def search_arxiv(query):
    query = query[:100]
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=2,
        sort_by=arxiv.SortCriterion.Relevance)
    results = client.results(search)
    return [{"text": r.summary, "url": r.entry_id} for r in results]

research_prompt = PromptTemplate.from_template(
"""
You are a research assistant.

Task:
{task}

Information from sources (URLs included):
{sources}

Summarize the key findings in clear and concise language with proper citations, no more than 500 characters.
"""
)

def researcher_task(task):
    web_results = search_tavily(task)
    arxiv_results = search_arxiv(task)
    all_results = web_results + arxiv_results

    sources_text = "\n".join([f"{r['text']} (source: {r['url']})" for r in all_results])

    prompt = research_prompt.format(task=task, sources=sources_text)
    summary = llm.invoke(prompt).content

    return {"task": task, "summary": summary, "sources": [r["url"] for r in all_results]}

def researcher_agent(state):
    print("\nResearcher agent is working on tasks...")
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        for t in state["tasks"]:
            future = executor.submit(researcher_task, t)
            futures[future] = t
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                results.append({"task": futures[future], "summary": "", "sources": []})
    return {"research_results": results}

report_prompt = PromptTemplate.from_template(
"""
You are a research report writer.

Using the research findings below, generate a detailed research report
in Markdown format with headings and numbered references.

Research Question:
{query}

Findings:
{findings}

References:
{references}
"""
)

def reporter_agent(state):
    findings_md = ""
    all_refs = set()

    for j, res in enumerate(state["research_results"], 1):
        findings_md += f"### Task {j}: {res['task']}\n{res['summary']}\n\n"
        all_refs.update([url for url in res['sources'] if url])

    references_md = "\n".join([f"- {url}" for url in all_refs])

    prompt = report_prompt.format(
        query=state["query"],
        findings=findings_md,
        references=references_md
    )

    full_report = llm.invoke(prompt).content
    print("\nDraft report generated, Please review the report and approve or request revisions.")
    return {"draft_report": full_report}

def human_review(state):

    decision = {"approved": False}

    root = tk.Tk()
    root.title("Draft Research Report Review")
    root.geometry("1200x800")

    text_area = ScrolledText(root, wrap=tk.WORD, font=("Arial", 12))
    text_area.pack(fill="both", expand=True, padx=10, pady=10)

    text_area.insert(tk.END, state["draft_report"])
    text_area.config(state="disabled")

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    approve_btn = tk.Button(
        button_frame,
        text="Approve",
        width=15,
        bg="green",
        fg="white",
        command=lambda: (decision.update({"approved": True}), root.destroy())
    )

    revise_btn = tk.Button(
        button_frame,
        text="Revise",
        width=15,
        bg="orange",
        fg="black",
        command=lambda: (decision.update({"approved": False}), root.destroy())
    )

    approve_btn.pack(side="left", padx=20)
    revise_btn.pack(side="right", padx=20)

    root.mainloop()

    if decision["approved"]:
        print("\nReport approved. Final report saved.")
        return {
            "approved": True,
            "final_report": state["draft_report"]
        }
    else:
        print("\nReport rejected. Research needed.")
        return {
            "approved": False,
            "research_results": [],
            "draft_report": ""
        }


builder = StateGraph(ResearchState)

builder.add_node("coordinator", coordinator_agent)
builder.add_node("planner", planner_agent)
builder.add_node("researcher", researcher_agent)
builder.add_node("reporter", reporter_agent)
builder.add_node("human_review", human_review)

builder.set_entry_point("coordinator")
builder.add_edge("planner", "coordinator")
builder.add_edge("researcher", "coordinator")
builder.add_edge("reporter", "coordinator")
builder.add_edge("human_review", "coordinator")

graph = builder.compile()

if __name__ == "__main__":
    query = input("\nPlease enter your research topic:")
    result = graph.invoke({"query": query})
    
    print("\nThe final report has been saved to a Markdown file.\n")

    filename = query.replace(" ", "_") + "_report.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(result["final_report"])