# Cypher Queries — Week 2 Person B

## Q1 — See full graph
MATCH (n) RETURN n LIMIT 50

## Q2 — List accused by prior cases
MATCH (a:Accused)
RETURN a.name, a.prior_cases
ORDER BY a.prior_cases DESC LIMIT 10

## Q3 — FIRs for a specific accused
MATCH (a:Accused)-[:ACCUSED_IN]->(f:FIR)
WHERE a.name CONTAINS "Rajeshri"
RETURN a.name, f.fir_number, f.crime_type, f.date_filed

## Q4 — Call network
MATCH (c:Accused)-[call:CALLED]->(r:Accused)
RETURN c.name, r.name, call.duration, call.call_date LIMIT 20

## Q5 — 2-degree network expansion
MATCH path = (a:Accused {accused_id:1})-[*1..2]-(connected)
RETURN path

## Q6 — Habitual offenders
MATCH (a:Accused)-[:ACCUSED_IN]->(f:FIR)
WITH a, COUNT(f) AS n WHERE n >= 3
RETURN a.name, a.district, n ORDER BY n DESC