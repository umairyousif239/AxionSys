from backend.services.log_parser import parse_log

# Test 1 - Python traceback
traceback = """
Traceback (most recent call last):
  File "api/routes.py", line 12, in user_route
    return get_user_data()
  File "services/user_service.py", line 8, in get_user_data
    conn = connect_db()
  File "db/connection.py", line 7, in connect_db
    return conn.cursor()
AttributeError: 'NoneType' object has no attribute 'cursor'
"""

# Test 2 - log file style
log_text = """
2024-01-15 10:23:41 INFO Starting application
2024-01-15 10:23:42 ERROR Database connection failed: NoneType has no attribute cursor
2024-01-15 10:23:42 CRITICAL Service unavailable
"""

# Test 3 - free form
free_form = "why does cursor fail when connecting to the database"

for name, text in [("TRACEBACK", traceback), ("LOG FILE", log_text), ("FREE FORM", free_form)]:
    print(f"\n{'='*40}")
    print(f"TEST: {name}")
    print('='*40)

    results = parse_log(text)

    for r in results:
        print(f"\nError:     {r['error']}")
        print(f"Type:      {r['type']}")
        print(f"Primary:   {r['primary_query']}")
        print(f"Secondary: {r['secondary_queries']}")
        if r['files_mentioned']:
            print(f"Files:     {[f['file'] for f in r['files_mentioned']]}")