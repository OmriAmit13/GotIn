# import requests
# import json
# import sys
# import traceback
# import os

# def main():
#     # Load configuration
#     with open("../config.json", encoding="utf-8") as f:
#         config = json.load(f)

#     # Load test data
#     with open("testData.json", encoding="utf-8") as f:
#         test_data = json.load(f)

#     servers = [
#         (f"http://127.0.0.1:{config['ports']['bgu']}/BenGurion", 'Ben-Gurion University'),
#         (f"http://127.0.0.1:{config['ports']['tel_aviv']}/TelAviv", 'Tel Aviv University'),
#         (f"http://127.0.0.1:{config['ports']['hebrew_university']}/HebrewUniversity", 'Hebrew University'),
#         (f"http://127.0.0.1:{config['ports']['technion']}/Technion", 'Technion University')
# ]

#     # Test against each university
#     for endpoint, uni_name in servers:
#         failures = []

#         print(f"\nTesting {uni_name} at {endpoint}...")
        
#         for entry in test_data:
#             try:
#                 response = requests.post(endpoint, json=entry)
#                 if not response.ok:
#                     try:
#                         error_json = response.json()
#                     except Exception:
#                         error_json = {}
#                     failure = {
#                         "input": entry,
#                         "errorMessage": error_json.get("message", response.text),
#                         "stackTrace": error_json.get("stack", "")
#                     }
#                     failures.append(failure)
#             except Exception as e:
#                 failure = {
#                     "input": entry,
#                     "errorMessage": str(e),
#                     "stackTrace": traceback.format_exc()
#                 }
#                 failures.append(failure)

#         # Write failures to university-specific log file
#         log_filename = f"{uni_name}TestResults.json"
#         if failures:
#             with open(log_filename, "w", encoding="utf-8") as f:
#                 json.dump(failures, f, ensure_ascii=False, indent=4)
#             print(f"{len(failures)} failures logged to {log_filename}")
#         else:
#             # Create empty file even if no failures
#             with open(log_filename, "w", encoding="utf-8") as f:
#                 json.dump([], f)
#             print("All tests passed!")

# if __name__ == "__main__":
#     main()

import requests
import json
import sys
import traceback
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_server(endpoint, uni_name, test_data):
    failures = []
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
                failures.append(failure)
        except Exception as e:
            failure = {
                "input": entry,
                "errorMessage": str(e),
                "stackTrace": traceback.format_exc()
            }
            failures.append(failure)

    # Write failures to university-specific log file
    log_filename = f"{uni_name}TestResults.json"
    if failures:
        with open(log_filename, "w", encoding="utf-8") as f:
            json.dump(failures, f, ensure_ascii=False, indent=4)
        print(f"{len(failures)} failures logged to {log_filename}")
    else:
        with open(log_filename, "w", encoding="utf-8") as f:
            json.dump([], f)
        print("All tests passed!")

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

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(test_server, endpoint, uni_name, test_data)
            for endpoint, uni_name in servers
        ]
        for future in as_completed(futures):
            # This will re-raise any exceptions from the threads
            future.result()

if __name__ == "__main__":
    main()