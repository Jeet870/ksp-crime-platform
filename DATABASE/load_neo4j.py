import os, random
import psycopg2
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv(r"C:\ksp-crime-platform\AI-BACKEND\.env")

pg = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT", "5432"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    sslmode="require"
)
cur = pg.cursor()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687"),
    auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "ksp12345"))
)

def clear_graph(s):
    s.run("MATCH (n) DETACH DELETE n")
    print("Graph cleared")

def load_accused(s):
    cur.execute("SELECT accused_id,name,alias,age,gender,phone_number,prior_cases_count,district FROM accused")
    rows = cur.fetchall()
    for aid,name,alias,age,gender,phone,prior,district in rows:
        s.run("""MERGE (a:Accused {accused_id:$id})
                 SET a.name=$name, a.alias=$alias, a.age=$age,
                     a.gender=$gender, a.phone=$phone,
                     a.prior_cases=$prior, a.district=$district""",
              id=aid, name=name, alias=alias or "", age=age or 0,
              gender=gender or "", phone=phone or "", prior=prior or 0, district=district or "")
    print(f"Loaded {len(rows)} Accused nodes")

def load_firs(s):
    cur.execute("SELECT fir_id,fir_number,date_filed,police_station,district,crime_type,status FROM firs")
    rows = cur.fetchall()
    for fid,fnum,date,ps,dist,ctype,status in rows:
        s.run("""MERGE (f:FIR {fir_id:$id})
                 SET f.fir_number=$fnum, f.date_filed=$date,
                     f.police_station=$ps, f.district=$dist,
                     f.crime_type=$ctype, f.status=$status""",
              id=fid, fnum=fnum, date=str(date), ps=ps, dist=dist, ctype=ctype, status=status)
    print(f"Loaded {len(rows)} FIR nodes")

def load_accused_in(s):
    cur.execute("SELECT fir_id,accused_id,role_in_case,arrest_status FROM fir_accused")
    rows = cur.fetchall()
    for fid,aid,role,arrest in rows:
        s.run("""MATCH (a:Accused {accused_id:$aid})
                 MATCH (f:FIR {fir_id:$fid})
                 MERGE (a)-[r:ACCUSED_IN]->(f)
                 SET r.role=$role, r.arrest_status=$arrest""",
              aid=aid, fid=fid, role=role or "accused", arrest=arrest or "unknown")
    print(f"Loaded {len(rows)} ACCUSED_IN relationships")

def load_calls(s):
    cur.execute("""SELECT DISTINCT fa1.accused_id, fa2.accused_id
                   FROM fir_accused fa1 JOIN fir_accused fa2
                   ON fa1.fir_id=fa2.fir_id AND fa1.accused_id<fa2.accused_id
                   LIMIT 100""")
    rows = cur.fetchall()
    for caller, receiver in rows:
        s.run("""MATCH (c:Accused {accused_id:$c})
                 MATCH (r:Accused {accused_id:$r})
                 MERGE (c)-[call:CALLED]->(r)
                 SET call.duration=$dur, call.call_date=$date""",
              c=caller, r=receiver,
              dur=random.randint(30,600),
              date=f"2024-0{random.randint(1,9)}-{random.randint(1,28):02d}")
    print(f"Loaded {len(rows)} CALLED relationships")

def create_indexes(s):
    s.run("CREATE INDEX IF NOT EXISTS FOR (a:Accused) ON (a.accused_id)")
    s.run("CREATE INDEX IF NOT EXISTS FOR (f:FIR) ON (f.fir_id)")
    s.run("CREATE INDEX IF NOT EXISTS FOR (a:Accused) ON (a.district)")
    s.run("CREATE INDEX IF NOT EXISTS FOR (f:FIR) ON (f.district)")
    print("Indexes created")

def verify(s):
    print("\n=== VERIFICATION ===")
    for label in ["Accused", "FIR"]:
        c = s.run(f"MATCH (n:{label}) RETURN COUNT(n) AS c").single()["c"]
        print(f"  {label}: {c}")
    for rel in ["ACCUSED_IN", "CALLED"]:
        c = s.run(f"MATCH ()-[r:{rel}]->() RETURN COUNT(r) AS c").single()["c"]
        print(f"  {rel}: {c}")
    result = s.run("""MATCH (a:Accused)-[:ACCUSED_IN]->(f:FIR)
                      RETURN a.name, COUNT(f) AS n ORDER BY n DESC LIMIT 3""")
    print("  Top habitual offenders:")
    for rec in result:
        print(f"    {rec['a.name']}: {rec['n']} FIRs")

if __name__ == "__main__":
    with driver.session() as s:
        clear_graph(s)
        load_accused(s)
        load_firs(s)
        load_accused_in(s)
        load_calls(s)
        create_indexes(s)
        verify(s)
    driver.close()
    cur.close()
    pg.close()
    print("Done")