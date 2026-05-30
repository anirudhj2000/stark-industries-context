# Agent Memory

## Preferences

- [2026-05-16] [correction] Prefers read-only database access - use `execute_sql_read_only` instead of `execute_sql` to avoid accidental data modifications.

## Technical Context

- [2026-05-16] Works with Medallion Architecture (Bronze → Silver → Gold) in Databricks Unity Catalog.
- [2026-05-16] Familiar with SAP ERP table structures (kna1=customers, vbak=sales orders, mara=materials).
