# Research generate system based on AI agent
By inputting a research topic, the system can automatically complete the process of "keyword extraction to data retrieval to report generation to manual review". And this system will output a research report in Markdown format with references.

! Please add your own API key.
## Workflow
<img width="3405" height="1809" alt="1" src="https://github.com/user-attachments/assets/bfc84a3c-c25f-4a48-9158-0dec2a78a7cd" />

## Agents and roles
**Coordinator Agent**: manages the workflow and determines next agent to execute based on system state

**Planner Agent**: extracts keywords from user query and generate reasonable research tasks

**Researcher Agent**: executes parallel multi-source retrieval and summarizes findings

**Reporter Agent**: creates research results into structured Markdown report with references

**Human Review**: provides visual interface for human validation of draft reports

## System layer
**Interactive layer**: Users input research topics and visualize the review window via the terminal.

**Agent Layer**: Each agent takes turns completing its task.

**Tools Layer**:The auxiliary modules include Groq large language model, Tavily web search and arXiv paper retrieval.

**Record Layer**: ResearchState class and Markdown generation
