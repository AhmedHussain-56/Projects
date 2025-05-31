# import streamlit as st
# import sqlite3
# import ollama

# def create_database():
#     """Creates a sample database with a test table."""
#     conn = sqlite3.connect('database.db')
#     cursor = conn.cursor()
#     cursor.execute('''CREATE TABLE IF NOT EXISTS employees (
#                       id INTEGER PRIMARY KEY, 
#                       name TEXT, 
#                       age INTEGER, 
#                       department TEXT)''')
#     conn.commit()
#     conn.close()

# def generate_sql(user_query):
#     """Converts natural language to SQL using Ollama."""
#     if not user_query:
#         return "No query provided"
    
#     model_prompt = f"Convert the following natural language query into an SQL statement: {user_query}"
#     # response = ollama.chat(model='mistral', messages=[{"role": "user", "content": model_prompt}])
#     response = ollama.chat(model='llama3.2', messages=[{"role": "user", "content": model_prompt}])
#     sql_query = response.get("message", {}).get("content", "")
#     return sql_query

# def execute_sql(sql_query):
#     """Executes a given SQL query and returns results."""
#     if not sql_query:
#         return "No SQL query provided"
    
#     try:
#         conn = sqlite3.connect('database.db')
#         cursor = conn.cursor()
#         cursor.execute(sql_query)
#         results = cursor.fetchall()
#         conn.commit()
#         conn.close()
#         return results
#     except Exception as e:
#         return str(e)

# # Streamlit UI
# st.title("Natural Language to SQL Query Conversion")

# # Create database
# create_database()

# # User input for NL query
# user_query = st.text_input("Enter your natural language query:")

# if st.button("Generate SQL"):
#     sql_query = generate_sql(user_query)
#     st.text_area("Generated SQL Query:", sql_query, height=100)
    
#     if st.button("Execute SQL"):
#         results = execute_sql(sql_query)
#         st.write("Results:", results)


import streamlit as st
import sqlite3
import ollama

def create_database():
    """Creates a sample database with a test table."""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS employees (
                      id INTEGER PRIMARY KEY, 
                      name TEXT, 
                      age INTEGER, 
                      department TEXT)''')
    conn.commit()
    conn.close()

def generate_sql(user_query):
    """Converts natural language to SQL using Ollama."""
    if not user_query:
        return "No query provided"
    
    model_prompt = f"Convert the following natural language query into an SQL statement: {user_query}"
    response = ollama.chat(model='llama3.2', messages=[{"role": "user", "content": model_prompt}])
    sql_query = response.get("message", {}).get("content", "")
    return sql_query

def execute_sql(sql_query):
    """Executes a given SQL query and returns results."""
    if not sql_query:
        return "No SQL query provided"
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        conn.commit()
        conn.close()
        return results
    except Exception as e:
        return str(e)

# Streamlit UI
st.title("Natural Language to SQL Query Conversion")

# Create database
create_database()

# Initialize session state for SQL query
if "sql_query" not in st.session_state:
    st.session_state.sql_query = ""

# User input for NL query
user_query = st.text_input("Enter your natural language query:")

if st.button("Generate SQL"):
    st.session_state.sql_query = generate_sql(user_query)  # Store in session state

# st.text_area("Generated SQL Query:", st.session_state.sql_query, height=100)
user_querypro = st.text_area("Generated SQL Query:", st.session_state.sql_query, height=100)
if st.button("Execute SQL"):
    if st.session_state.sql_query:  # Ensure an SQL query is stored
        # user_query = st.text_area("Generated SQL Query:", st.session_state.sql_query, height=100)
        results = execute_sql(user_querypro)
        st.write("Results:", results)
    else:
        st.warning("Please generate an SQL query first!")
