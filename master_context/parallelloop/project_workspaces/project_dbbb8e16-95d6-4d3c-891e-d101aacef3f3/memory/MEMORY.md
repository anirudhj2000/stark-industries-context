# Agent Memory

## Preferences

- [2026-05-16] Prefers read-only database access for safety - explicitly requested using `execute_sql_read_only` instead of `execute_sql` to avoid accidental data modifications

## Technical Knowledge

- [2026-05-16] Works with Medallion Architecture (Bronze → Silver → Gold) in Databricks
- [2026-05-16] Familiar with SAP ERP table structures (kna1=customers, vbak=sales orders, mara=materials, etc.)
- [2026-05-16] Data sources include: SAP ERP, DMS (dealer management), SFA (sales force automation), APRISO (manufacturing), D365, Loyalty, Data Science ML models

## Observations

- [2026-05-18] Dual Databricks MCP setup (mcp__databricks__ and mcp__databricks_other__) both point to the same Unity Catalog workspace
- [2026-05-26] Power BI MCP integration working. Workspace "Power BI test WS" available in India Central region (ID: 0998ae17-6763-4356-a46a-bdc3b0f609fc). Tools available: list_workspaces, list_datasets, list_reports, execute_queries, get_dataset_metadata, refresh_dataset
- [2026-05-27] Tally MCP available (24 tools for form management, blocks, styling, logic, data fetching) but requires authentication setup before use
- [2026-05-27] Google Calendar MCP working via Composio - successfully fetching calendar events
- [2026-05-16] execute_sql tool was NOT blocked as expected - configuration may need update if write restriction is desired

## Available MCP Ecosystem

- [2026-05-22] Composio-managed: Figma, GitHub, Gmail, Google Calendar, Google Drive, LinkedIn, Notion, Slack
- [2026-05-22] Data & Analytics: Tableau, Power BI, Databricks
- [2026-05-22] Internal Platform: Plais Nucleus, Memory Tools
- [2026-05-27] Form Builder: Tally (requires authentication)

## Working Integrations
- Databricks SQL (dual MCP, read-only preferred)
- Power BI (workspace: "Power BI test WS")
- Slack (via Composio)
- Google Calendar (via Composio)
