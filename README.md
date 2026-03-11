# Research generate system based on AI agent
By inputting a research topic, the system can automatically complete the process of "keyword extraction to data retrieval to report generation to manual review". And this system will output a research report in Markdown format with references.
## Workflow
graph TD
    A[User Input: Research Query] --> B[Coordinator Agent]
    B -->|No tasks generated| C[Planner Agent: Keyword Extraction & Task Breakdown]
    C --> B
    B -->|Tasks exist, no research results| D[Researcher Agent: Parallel Multi-Source Retrieval]
    D --> B
    B -->|Research results exist, no draft| E[Reporter Agent: Markdown Report Generation]
    E --> B
    B -->|Draft exists, not approved| F[Human Review: GUI-Based Approval/Revision]
    F -->|Approved| G[Persist Final Report as Markdown]
    F -->|Revised| B
    G --> H[Workflow Termination]
