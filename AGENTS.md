# AGENTS.md — 1C Web Console

## Project Annotation
Web console for 1C:Enterprise 8.3.x cluster management on Ubuntu. Provides full administration capabilities through modern web interface.

## Keywords
`1C` `enterprise` `cluster` `administration` `rac` `fastapi` `react` `typescript` `ant-design` `postgresql` `redis` `websocket` `ubuntu`

## Technology Stack
- **Backend**: Python 3.11, FastAPI 0.109
- **Frontend**: React 18, TypeScript 5, Ant Design 5
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **1C Integration**: rac CLI utility
- **Auth**: JWT (local)

## Documentation Artifacts
- `docs/requirements.xml` — Use cases and functional requirements
- `docs/technology.xml` — Technology decisions and versions
- `docs/development-plan.xml` — Module breakdown, contracts, phases
- `docs/knowledge-graph.xml` — Module map, dependencies, exports

## Unique Tag Convention
- Modules: `M-BE-xxx` (backend), `M-FE-xxx` (frontend)
- Phases: `Phase-N`
- Steps: `step-N`
- Data flows: `DF-xxx`
- Exports: `export-name`

## Module Taxonomy
- ENTRY_POINT — HTTP handlers, WebSocket, CLI
- CORE_LOGIC — Business rules, auth, RAC adapter
- DATA_LAYER — Database models, cache
- UI_COMPONENT — React components, pages
- UTILITY — Config, logging, exceptions
- INTEGRATION — External service adapters

## Development Workflow
1. Read `docs/development-plan.xml` for module contracts
2. Read `docs/knowledge-graph.xml` for dependencies
3. Generate code with GRACE markup (MODULE_CONTRACT, MODULE_MAP, blocks)
4. Update knowledge-graph.xml after changes
5. Run verification (typecheck, lint, tests)

## Code Style
- Python: PEP 8, type hints, async/await
- TypeScript: strict mode, functional components, hooks
- Comments: GRACE semantic markup (START_BLOCK/END_BLOCK)
