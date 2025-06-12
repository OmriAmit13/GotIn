import requests
import json
import sys
import traceback
import os

def main():
    # Load configuration
    with open("../config.json", encoding="utf-8") as f:
        config = json.load(f)

    # Load test data
    with open("testData.json", encoding="utf-8") as f:
        test_data = json.load(f)

    servers = [
        (f"http://127.0.0.1:{config['ports']['bgu']}/BenGurion", 'Ben-Gurion University'),
        (f"http://127.0.0.1:{config['ports']['tel_aviv']}/TelAviv", 'Tel Aviv University'),
        (f"http://127.0.0.1:{config['ports']['hebrew_university']}/HebrewUniversity", 'Hebrew University'),
        (f"http://127.0.0.1:{config['ports']['technion']}/Technion", 'Technion University')
    ]

    failures = {
        "Ben-Gurion University": [],
        "Tel Aviv University": [],
        "Hebrew University": [],
        "Technion University": []
    }

    # Test against each university
    for endpoint, uni_name in servers:

        print(f"\nTesting {uni_name} at {endpoint}...")
        
        for entry in test_data:
            try:
                response = requests.post(endpoint, json=entry)
                if not response.ok:
                    try:
                        error_json = response.json()
                    except Exception:
                        error_json = {}
                    failure = {
                        "input": entry,
                        "errorMessage": error_json.get("message", response.text),
                        "stackTrace": error_json.get("stack", "")
                    }
                    failures[uni_name].append(failure)
            except Exception as e:
                failure = {
                    "input": entry,
                    "errorMessage": str(e),
                    "stackTrace": traceback.format_exc()
                }
                failures[uni_name].append(failure)
    

    # Print summary of failures
    for uni_name, uni_failures in failures.items():

        # Write failures to university-specific log file
        log_filename = f"{uni_name.replace(' ', '_')}TestResults.json"
        if uni_failures:
            with open(log_filename, "w", encoding="utf-8") as f:
                json.dump(uni_failures, f, ensure_ascii=False, indent=4)
            print(f"{len(uni_failures)} failures logged to {log_filename}")
        else:
            # Create empty file even if no failures
            with open(log_filename, "w", encoding="utf-8") as f:
                json.dump([], f)
            print("All tests passed!")

if __name__ == "__main__":
    main()