# Agent Memory

## Preferences

- [2026-05-16] Prefers read-only database access for safety - explicitly requested using `execute_sql_read_only` instead of `execute_sql` to avoid accidental data modifications

## Technical Knowledge

- [2026-05-16] Works with Medallion Architecture (Bronze → Silver → Gold) in Databricks
- [2026-05-16] Familiar with SAP ERP table structures (kna1=customers, vbak=sales orders, mara=materials, etc.)
- [2026-05-16] Data sources include: SAP ERP, DMS (dealer management), SFA (sales force automation), APRISO (manufacturing), D365, Loyalty, Data Science ML models

## Observations

- [2026-05-16] Databricks SQL MCP may have connectivity issues - experienced disconnection during session
- [2026-05-16] execute_sql tool was NOT blocked as expected - configuration may need update if write restriction is desired
- [2026-05-18] Dual Databricks MCP setup (mcp__databricks__ and mcp__databricks_other__) both point to the same Unity Catalog workspace
