# =============================================================
# LANTERN INTELLIGENCE v2 — retrieve.py
# Phase 3: Live SQL execution + ChromaDB concept retrieval
# =============================================================
# WHAT THIS SCRIPT DOES:
#   1. Connects to the selected company SQLite database
#   2. Runs all 8 financial queries live and returns results
#   3. Queries ChromaDB for relevant concept documents
#   4. Returns both to be used by the LLM in Phase 5
#
# This script is the data backbone of the adviser.
# It never generates answers — it only fetches the context
# that the LLM needs to generate a grounded answer.
# =============================================================
import os
import sqlite3
import chromadb

from sentence_transformers import SentenceTransformer 
# -------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------
CHROMA_STORE_DIR = "/workspace/Lantern_V2/chroma_store"
COLLECTION_NAME  = "lantern_financial_concepts"
TOP_K_CONCEPTS   = 3  # how many concept docs to retrieve per question
SQL_DIR = "/workspace/Lantern_V2/matrix_queries"
DB_PATHS = {
    "service1": "/workspace/Lantern_V2/databases/service1.db",
    "service2": "/workspace/Lantern_V2/databases/service2.db",
    "service3": "/workspace/Lantern_V2/databases/service3.db"
}

# -------------------------------------------------------------
# MAP QUERY NAMES TO .SQL FILES
# -------------------------------------------------------------
# Keys are human-readable names used throughout the system.
# Values are the actual filenames in matrix_queries/
# -------------------------------------------------------------
 
SQL_FILES = {
    "net_profit_margin":      "01_net_profit_margin.sql",
    "monthly_revenue_trend":  "02_monthly_revenue_trend.sql",
    "days_sales_outstanding": "03_days_sales_outstanding.sql",
    "client_concentration":   "04_client_concentration.sql",
    "burn_rate_runway":       "05_burn_rate_runway.sql",
    "expense_breakdown":      "06_expense_breakdown.sql",
    "revenue_per_employee":   "07_revenue_per_employee.sql",
    "client_churn_rate":      "08_client_churn_rate.sql"
}

# -------------------------------------------------------------
# LOAD SQL QUERIES FROM FILES
# -------------------------------------------------------------
# Reads all .sql files once at startup and stores them in a
# dictionary. This way we only read from disk once — not on
# every query execution.
# -------------------------------------------------------------
def load_sql_queries():
    """
    Read all .sql files from SQL_DIR and return as a dictionary.
    Called once at startup.
 
    Returns:
    dict: {query_name: sql_string}
    """
    queries = {}
    for query_name, filename in SQL_FILES.items():
        filepath = os.path.join(SQL_DIR, filename)

        if not os.path.exists(filepath):
            print(f"WARNING: SQL file not found: {filepath}")
            queries[query_name] = None
            continue
        with open(filepath, "r", encoding = 'utf-8') as f:
            sql = f.read().strip()
        
        queries[query_name] = sql
        print(f" Loaded SQL: {filename}")
    return queries 



# -------------------------------------------------------------
# LOAD EMBEDDING MODEL AND CHROMADB
# -------------------------------------------------------------
# These are loaded once when the module is imported.
# Loading them here avoids reloading on every function call.
# -------------------------------------------------------------

print("Loading retrieval system ...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path=CHROMA_STORE_DIR)
collection = chroma_client.get_collection(name=COLLECTION_NAME)
print("Embedding model and ChromaDB ready. \n")
print("Loading SQL queries from matrix_queries/...")
SQL_QUERIES = load_sql_queries()
print(f"{len([q for q in SQL_QUERIES.values() if q])} SQL queries loaded.\n")

# -------------------------------------------------------------
# FUNCTION 1: GET LIVE FINANCIAL DATA FROM SQLITE
# -------------------------------------------------------------
# Connects to the selected company database, runs all 8
# queries, and returns the results as a dictionary.
# Each result is a list of row dictionaries.
# -------------------------------------------------------------

def get_live_data(db_key):
    """
    Connect to the selected company database and run all 
    8 financial queries. Returns a dictionary of results.

    Args: 
        db_key: "service1", "service2", or "service3"
    
    Returns:
        dict: {query_name: [list of result row dicts]}
    """
    if db_key not in DB_PATHS:
        raise ValueError(f"Unknown database: {db_key}." f"choose from: {list(DB_PATHS.keys())}")
    
    db_path= DB_PATHS[db_key]
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found: {db_path}")
    
    results = {}
    # row_factory makes results come back as named dictionaries
    # so the LLM can read row["net_profit_margin_pct"]
    # instead of row[0]
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()
        for query_name,sql in SQL_QUERIES.items():
                
            # skip any queries that failed to load
            if sql is None:
                results[query_name] = {"error": "SQL file not found"}
                continue
            try:
                cursor.execute(sql)
                rows = cursor.fetchall()
                                # convert Row objects to plain dictionaries
                results[query_name] = [dict(row) for row in rows]
 
            except sqlite3.Error as e:
                # if one query fails, record the error and continue
                # don't let one bad query crash the whole retrieval
                results[query_name] = {"error": str(e)}
                print(f"  WARNING: Query failed — {query_name}: {e}")
 
    finally:
        # always close the connection even if something fails
        conn.close()
 
    return results
 
 # -------------------------------------------------------------
# FUNCTION 2: GET RELEVANT CONCEPT DOCUMENTS FROM CHROMADB
# -------------------------------------------------------------
# Embeds the user question and retrieves the most relevant
# concept documents from ChromaDB.
# -------------------------------------------------------------

def get_concepts(question):
    """
    Retrieve the most relevant financial concept document for a given user questions.
    Args:
        questions: plain ENglish user question (string)
    Returns:
        list of dicts: [{metric, text, score}, ....]
    """
    query_vector = embedding_model.encode([question]).tolist()
    results = collection.query(
        query_embeddings = query_vector,
        n_results = TOP_K_CONCEPTS,
        include= ["documents", 'metadatas', "distances"]
    )
    concepts = []
    for i in range(len(results["ids"][0])):
        concepts.append({
            "metric": results["metadatas"][0][i]["metric"],
            "text": results["documents"][0][i],
            "score": round(1 - results["distances"][0][i], 4)
        })
    return concepts 

# -------------------------------------------------------------
# FUNCTION 3: FULL RETRIEVAL — combines both functions
# -------------------------------------------------------------
# This is the main function the adviser will call.
# One call returns everything needed to build the LLM prompt.
# -------------------------------------------------------------
def retrieve(question, db_key):
    """
    Full retrieval pipeline. Given a user question and a
    selected database, returns both live financial data and
    relevant concept documents.
 
    Args:
        question: plain English user question
        db_key:   "service1", "service2", or "service3"
 
    Returns:
        dict: {
            "live_data": {query_name: [rows]},
            "concepts":  [{metric, text, score}]
        }
    """
    live_data = get_live_data(db_key)
    concepts = get_concepts(question)
    return {
        "live_data": live_data,
        "concepts": concepts
    }
# -------------------------------------------------------------
# QUICK TEST — runs when you execute this script directly
# -------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("Retreive.py - Quick test")
    print("=" * 60)
    test_question = 'Is our cash runway safe?'
    test_db = "service1"
    print(f"\nQuestions: {test_question}")
    print(f"Database: {test_db}\n")
    result = retrieve(test_question, test_db)

    #show concept retrieval results
    print("CONCEPTS RETRIEVED:")
    # After "CONCEPTS RETRIEVED:" you need:
    for concept in result["concepts"]:
        print(f"  {concept['metric']} (score: {concept['score']})")
    print("-" * 40)
    for query_name, rows in result["live_data"].items():
        if isinstance(rows, list) and len(rows) > 0:
            print(f" {query_name}:")
            for row in rows[:2]: # show max 2 rows per query
                print(f"   {row}")
        else:
            print(f" {query_name}: {rows}")

    print("\n" + "=" * 60)
    print("retrieve.py is working. Ready for Phase 4.")
    print("=" * 60)