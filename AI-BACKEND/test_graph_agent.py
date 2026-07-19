# test_graph_agent.py
from graph_agent import GraphAgent
import time

agent = GraphAgent()

print("=== TEST 1: Natural language query ===")
result = agent.query(
    "Find all accused persons who have more than 1 prior case",
    district="Bengaluru East"
)
print(f"Cypher: {result['cypher']}")
print(f"Records: {result['count']}")
if result['records']:
    print(f"First record: {result['records'][0]}")

time.sleep(1)

print("\n=== TEST 2: Get FIR network ===")
network = agent.get_fir_network(fir_id=3, district="Bengaluru East")
print(f"Nodes: {len(network['nodes'])}")
print(f"Edges: {len(network['edges'])}")
if network['nodes']:
    print(f"Sample node: {network['nodes'][0]}")

time.sleep(1)

print("\n=== TEST 3: Phone call network ===")
result = agent.query(
    "Show all accused persons who called each other",
    district="Bengaluru East"
)
print(f"Records returned: {result['count']}")
print(f"Cypher used: {result['cypher']}")

agent.close()
print("\nAll graph tests complete")