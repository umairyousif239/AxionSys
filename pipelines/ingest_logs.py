from backend.services.log_parser import parse_log

logs = []

def ingest_logs(log_text: str) -> list[dict]:
    parsed = parse_log(log_text)
    
    for entry in parsed:
        logs.append(entry)
    
    return logs

if __name__ == "__main__":
    with open("data/logs/sample.log") as f:
        log_text = f.read()

    entries = ingest_logs(log_text)
    print(f"Parsed {len(entries)} error(s)")
    
    for e in entries:
        print(f"\nError:   {e['error']}")
        print(f"Type:    {e['type']}")
        print(f"Primary: {e['primary_query']}")
        print(f"Secondary: {e['secondary_queries']}")