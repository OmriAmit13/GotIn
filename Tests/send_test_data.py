import requests
import json
import sys
import traceback

def main():
    if len(sys.argv) != 2:
        print("Usage: python send_test_data.py <api_endpoint>")
        sys.exit(1)

    api_endpoint = sys.argv[1]

    with open("testData.json", encoding="utf-8") as f:
        test_data = json.load(f)

    failures = []
    successes = []

    for entry in test_data:
        try:
            response = requests.post(api_endpoint, json=entry)
            if not response.ok:
                try:
                    error_json = response.json()
                except Exception:
                    error_json = {}
                failure = {
                    "Failed json": entry,
                    "Error message": error_json.get("message", response.text),
                    "StackTrace": error_json.get("stack", "")
                }
                failures.append(failure)
            else:
                try:
                    result_json = response.json()
                except Exception:
                    result_json = response.text
                success = {
                    "Succeeded json": entry,
                    "Result": result_json
                }
                successes.append(success)
        except Exception as e:
            failure = {
                "Failed json": entry,
                "Error message": str(e),
                "StackTrace": traceback.format_exc()
            }
            failures.append(failure)

    if failures:
        with open("failures.txt", "w", encoding="utf-8") as f:
            for fail in failures:
                f.write(json.dumps(fail, ensure_ascii=False, indent=4))
                f.write("\n\n")
        print(f"{len(failures)} failures logged to failures.txt")
    else:
        print("All requests succeeded.")

    if successes:
        with open("successes.txt", "w", encoding="utf-8") as f:
            for succ in successes:
                f.write(json.dumps(succ, ensure_ascii=False, indent=4))
                f.write("\n\n")
        print(f"{len(successes)} successes logged to successes.txt")

if __name__ == "__main__":
    main()