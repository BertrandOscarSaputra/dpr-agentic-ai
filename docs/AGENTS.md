# Agent Design & LangGraph Workflow

## Agent Overview

The system uses a **LangGraph Supervisor** pattern with specialized sub-agents:

| Agent | Responsibility |
|-------|---------------|
| **Supervisor** | Orchestrates workflow, routes tasks |
| **Twitter Collection** | Collects tweets via API |
| **News Collection** | Collects news via RSS feeds |
| **Analysis** | IndoBERT sentiment + Gemini AKD classification |
| **Trend** | Z-score anomaly detection per AKD |
| **Insight** | Gemini-powered narrative summarization |
| **Recommendation** | Generates actionable recommendations |
| **Report** | PDF report generation |

## Workflow

```
[Supervisor] → [Collection Agents] → [Analysis Agent] → [Trend Agent]
                                                              ↓
                                          [Insight Agent] ← [Trend Agent]
                                                ↓
                                      [Recommendation Agent]
                                                ↓
                                         [Report Agent]
```

<!-- TODO: Add detailed LangGraph StateGraph configuration and state schema -->
