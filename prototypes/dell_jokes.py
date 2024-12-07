import requests
import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# API endpoint
url = "http://localhost:1234/v1/chat/completions"

# Headers for the request
headers = {
    "Content-Type": "application/json"
}

# Request payload
payload = {
    "model": "lmstudio-community/qwen2.5-7b-instruct",
    "messages": [{"role": "user", "content": "Tell me a joke about Dell products under $50."}],
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "joke_response",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "joke": {
                            "type": "string",
                            "description": "A joke about Dell products."
                        }
                    },
                    "required": ["joke"]
                }
            }
        }
    ]
}

# File to save the jokes
output_file = "dell_jokes.csv"

# Number of requests
num_requests = 100
parallel_calls = 10

def fetch_joke(request_id):
    try:
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()

        # Extract the joke from the response
        joke = response_data.get("choices", [{}])[0].get("message", {}).get("content", "No joke returned")
        return (request_id, joke)

    except Exception as e:
        return (request_id, f"Error: {str(e)}")

# Main function to fetch jokes in parallel and save to CSV
def main():
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Joke Number", "Joke"])

        with ThreadPoolExecutor(max_workers=parallel_calls) as executor:
            futures = [executor.submit(fetch_joke, i) for i in range(1, num_requests + 1)]

            for future in as_completed(futures):
                request_id, joke = future.result()
                print(f"Fetched joke {request_id}: {joke[:60]}...")
                writer.writerow([request_id, joke])

    print(f"Finished! Jokes saved to {output_file}")

if __name__ == "__main__":
    main()
