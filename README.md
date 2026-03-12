# Research generate system based on AI agent
By inputting a research topic, the system can automatically complete the process of "keyword extraction to data retrieval to report generation to manual review". And this system will output a research report in Markdown format with references.

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

## How to run the code
1.Register to get API key:
   - Groq API Key：https://console.groq.com/
   - Tavily API Key：https://tavily.com/
2. Python 3.9 or higher required
3. Download the files in this page
4. 
5. Put the API key into the environment file
6. Install all necessary dependency packages
7. Run the code in the terminal and input the research topic into the terminal
8. It will take a few minutes for the system to run
9. When the monitor window pops up, it sometimes doesn't cover the current window; you need to look through all open windows to find it.
10. Choose whether to accept the current assembly version. If not, the process will return to the coordinator and all operations will be repeated. If accepted, a Markdown document will be generated
   
