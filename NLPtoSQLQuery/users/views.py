from django.shortcuts import render,HttpResponse
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import UserRegistrationModel, QueryLog
import datetime
from django.conf import settings
import sqlite3
import ollama
import re
# Create your views here.
def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            print('Data is Valid')
            form.save()
            messages.success(request, 'You have been successfully registered')
            form = UserRegistrationForm()
            return render(request, 'UserRegistrations.html', {'form': form})
        else:
            messages.success(request, 'Email or Mobile Already Existed')
            print("Invalid form")
    else:
        form = UserRegistrationForm()
    return render(request, 'UserRegistrations.html', {'form': form})
def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginname')
        pswd = request.POST.get('pswd')
        print("Login ID = ", loginid, ' Password = ', pswd)
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            status = check.status
            print('Status is = ', status)
            if status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                print("User id At", check.id, status)
                return render(request, 'users/UserHome.html', {})
            else:
                messages.success(request, 'Your Account Not at activated')
                return render(request, 'UserLogin.html')
        except Exception as e:
            print('Exception is ', str(e))
            pass
        messages.success(request, 'Invalid Login id and password')
    return render(request, 'UserLogin.html', {})
def UserHome(request):
    return render(request, 'users/UserHome.html', {})

def GenerateSQL(request):
    return render(request, 'users/GenerateSQL.html',{})


def generate_sql(user_query):
    if not user_query:
        return "No query provided"
    
    model_prompt = f"Convert the following natural language query into an SQL statement: {user_query}"
    response = ollama.chat(model='llama3.2', messages=[{"role": "user", "content": model_prompt}])
    
    full_response = response.get("message", {}).get("content", "")
    print("Full Response from Llama:", full_response)  # Debugging

    # Step 1: Extract SQL code block (if present)
    sql_block_match = re.search(r"```sql\n(.*?)\n```", full_response, re.DOTALL)

    if sql_block_match:
        sql_query = sql_block_match.group(1).strip()  # Extract SQL inside markdown block
    else:
        # Step 2: Fallback: Extract SQL query using general regex
        sql_match = re.search(r"(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER).*?;", full_response, re.IGNORECASE | re.DOTALL)
        sql_query = sql_match.group(0).strip() if sql_match else "Failed to extract SQL query."

    print("Extracted SQL Query:", sql_query)  # Debugging
    Sqlstring =sql_query
    print("sst :", Sqlstring)

    return Sqlstring


def GenerateSQLProcess(request):
    if request.method == 'POST':
        Naturalquery = request.POST.get('Naturalquery')
        if not Naturalquery:
            return render(request, "users/GenerateSQL.html", {'error': 'Please enter a query'})
 
        # Generate SQL query
        sql_query = generate_sql(Naturalquery)
        print("Type of sql_query:", type(sql_query)) 
        print("sql_query:", sql_query) 

        # Send response to template
        
        usrname  = request.session['loginid']
        email = request.session['email']
        QueryLog.objects.create(username=usrname, email=email, natural_query=Naturalquery, sql_query=sql_query)
        return render(request, "users/GenerateSQL.html", {'Messages': sql_query, 'Naturalquery': Naturalquery})
    
    return render(request, "users/GenerateSQL.html")


def ExecuteSQLProcess(request):
    if request.method == 'POST':
        SQLQuery = request.POST.get('SQLQuery')
        if not SQLQuery:
            return render(request, "users/GenSQLResults.html", {'error': 'No SQL query provided'})

        try:
            conn = sqlite3.connect('db.sqlite3')
            cursor = conn.cursor()
            cursor.execute(SQLQuery)
            
            # Handle different query types
            if SQLQuery.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
            else:
                conn.commit()
                results = f"Query executed successfully. Rows affected: {cursor.rowcount}"
                columns = None

            conn.close()
            
            return render(request, "users/GenSQLResults.html", {
                'results': results,
                'columns': columns,
                'query': SQLQuery
            })

        except sqlite3.Error as e:
            return render(request, "users/GenSQLResults.html", {'error': f"Database error: {str(e)}"})
        except Exception as e:
            return render(request, "users/GenSQLResults.html", {'error': f"Error: {str(e)}"})

    return render(request, "users/GenSQLResults.html", {'error': 'Invalid request method'})

def UserDatasetViewPraw(request):
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    table_list= []
    for table in tables:
        table_list.append(table[0])

    return render(request,"users/viewDataset.html",{'data':table_list})

# def UserTableRowsResults(request):
#     conn = sqlite3.connect("db.sqlite3")
#     cursor = conn.cursor()
#     cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
#     tables = cursor.fetchall()
#     conn.close()
#     table_list= []
#     for table in tables:
#         table_list.append(table[0])
    
#     return render(request,"users/UserTableRowsResults.html",{'data':table_list})



def UserTableRowsResults(request):
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()

    # Fetch available tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]

    selected_table = request.GET.get('selected_table', None)
    records = []
    columns = []

    if selected_table:
        try:
            # Fetch column names
            cursor.execute(f"PRAGMA table_info({selected_table})")
            columns = [col[1] for col in cursor.fetchall()]

            # Fetch table records
            cursor.execute(f"SELECT * FROM {selected_table} LIMIT 10")  # Fetch limited records
            records = cursor.fetchall()
        except sqlite3.Error as e:
            print("Database error:", e)

    conn.close()

    return render(request, "users/UserTableRowsResults.html", {
        'tables': tables,
        'selected_table': selected_table,
        'columns': columns,
        'records': records
    })




def UserSearchHistoryResults(request):
    usrname = request.session['loginid']
    data = QueryLog.objects.filter(username=usrname)
    return render(request,"users/UserSearchHistory.html",{"data":data})

