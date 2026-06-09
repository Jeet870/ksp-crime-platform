# Neo4j Setup Notes — Person B

## Installation
- Installed Neo4j Desktop 2.1.4 on Windows
- Created local instance: ksp-crime-graph (Version 2026.05.0)
- Connection URI: neo4j://127.0.0.1:7687
- Database user: neo4j

## Sample Nodes Created (Week 1 Test Data)
5 Accused nodes created with properties: accused_id, name, district, prior_cases, phone

## Relationships Created
- Raju Kumar -[:CALLED]-> Venkat Reddy (date: 2024-03-14)
- Raju Kumar -[:CO_ACCUSED_WITH]-> Suresh Gowda
- Venkat Reddy -[:CALLED]-> Mohammed Ismail (date: 2024-03-13)

## Week 2 Plan
- Load real accused nodes from PostgreSQL into Neo4j using Python neo4j driver
- Add RBAC district filters to all Cypher queries