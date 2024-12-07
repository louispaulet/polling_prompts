import requests
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

# API endpoint
url = "http://localhost:1234/v1/chat/completions"

# Headers for the request
headers = {
    "Content-Type": "application/json"
}

# Request payload for fun facts
payload = {
    "model": "lmstudio-community/qwen2.5-7b-instruct",
    "messages": [{"role": "user", "content": "Tell me a fun fact about Dell products under $50."}],
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "fun_fact_response",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fun_fact": {
                            "type": "string",
                            "description": "A fun fact about Dell products."
                        }
                    },
                    "required": ["fun_fact"]
                }
            }
        }
    ]
}

# File to save the fun facts
output_file = "dell_fun_facts.csv"

# Number of requests
num_requests = 100

def fetch_fun_fact(request_id):
    try:
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()

        # Extract the fun fact from the response
        fun_fact = response_data.get("choices", [{}])[0].get("message", {}).get("content", "No fun fact returned")
        return (request_id, fun_fact)

    except Exception as e:
        return (request_id, f"Error: {str(e)}")

# Main function to fetch fun facts in parallel and save to CSV
def main():
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Fun Fact Number", "Fun Fact"])

        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(fetch_fun_fact, i) for i in range(1, num_requests + 1)]

            for future in as_completed(futures):
                request_id, fun_fact = future.result()
                print(f"Fetched fun fact {request_id}: {fun_fact[:60]}...")
                writer.writerow([request_id, fun_fact])

    print(f"Finished! Fun facts saved to {output_file}")

if __name__ == "__main__":
    main()
