import os  # Added import for handling directories
import requests
import csv
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import sys

# Configure logging
log_file = "app.log"
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# API endpoint and headers
url = "http://localhost:1234/v1/chat/completions"
headers = {
    "Content-Type": "application/json"
}

def get_user_input():
    """Get user input for prompt and number of requests, with basic validation."""
    print("Welcome to the API interaction tool.")
    print("You will be asked for a prompt and how many times to call the API.")
    prompt = input("Enter your prompt: ").strip()

    while True:
        num_requests_str = input("Enter the number of API calls to make: ").strip()
        if not num_requests_str.isdigit():
            print("Please enter a valid integer.")
            continue
        num_requests = int(num_requests_str)
        if num_requests <= 0:
            print("Number of requests must be a positive integer.")
            continue
        break

    logging.info(f"User prompt: {prompt}")
    logging.info(f"Number of requests: {num_requests}")
    return prompt, num_requests

def create_payload(prompt):
    """Create the main payload for the user prompt requests."""
    payload = {
        "model": "lmstudio-community/qwen2.5-7b-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "response",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "A response based on the prompt."
                            }
                        },
                        "required": ["content"]
                    }
                }
            }
        ]
    }
    logging.debug(f"Main request payload created: {json.dumps(payload, indent=2)}")
    return payload

def create_filename_payload(prompt):
    """Create a payload to get a filename from the system."""
    payload = {
        "model": "lmstudio-community/qwen2.5-7b-instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that generates concise, descriptive filenames based on user prompts."},
            {"role": "user", "content": f"Provide a filename for the following prompt: '{prompt}'"}
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "filename_response",
                "strict": "true",
                "schema": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "A concise filename under 50 characters, relevant to the prompt."
                        }
                    },
                    "required": ["filename"]
                }
            }
        },
        "temperature": 0.7,
        "max_tokens": 10
    }
    logging.debug(f"Filename request payload created: {json.dumps(payload, indent=2)}")
    return payload

def fetch_response(payload, request_id):
    """Send a request to the API and return the parsed response content."""
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=100)
        if response.status_code != 200:
            logging.error(f"Request {request_id} failed with status {response.status_code}: {response.text}")
            return (request_id, f"Error: Received status {response.status_code}")
        response_data = response.json()
        content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "No response returned")
        logging.info(f"Request {request_id} successful. Response: {content[:100]}...")
        return (request_id, content)
    except requests.exceptions.RequestException as e:
        logging.error(f"Request {request_id} failed: {str(e)}")
        return (request_id, f"Error: {str(e)}")
    except ValueError as e:
        # JSON parsing error
        logging.error(f"Request {request_id} returned invalid JSON: {str(e)}")
        return (request_id, "Error: Invalid JSON in response")

def parse_filename_content(content):
    """Parse the filename from the assistant's response, which may be incomplete or malformed JSON."""
    # Attempt to parse as JSON directly
    try:
        parsed_content = json.loads(content)
        filename = parsed_content.get("filename", "default_filename")
        return filename
    except json.JSONDecodeError:
        logging.warning("Incomplete or malformed JSON in filename response. Attempting fallback extraction.")
    
    # Fallback: Use a regex to find something that looks like a filename in the content
    match = re.search(r'filename"\s*:\s*"([^"]+)', content)
    if match:
        filename = match.group(1)
        return filename
    return "default_filename"

def sanitize_filename(filename):
    """Ensure filename is alphanumeric (plus underscore and dash), trimmed and under 50 chars."""
    # Keep only alphanumeric, underscores, and dashes
    clean_name = "".join(c if c.isalnum() or c in ('_', '-') else '' for c in filename)
    clean_name = clean_name[:50].strip().replace(" ", "_")
    return clean_name if clean_name else "default_filename"

def get_filename(prompt):
    """Obtain a filename from the model, with robust error handling."""
    print("Fetching a descriptive filename, please wait...")
    payload = create_filename_payload(prompt)
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=100)
        if response.status_code != 200:
            logging.error(f"Filename request failed with status {response.status_code}: {response.text}")
            print("Failed to fetch filename. Using 'default_filename' instead.")
            return "default_filename"
        response_data = response.json()
        logging.debug(f"Filename response data: {json.dumps(response_data, indent=2)}")

        content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not content:
            logging.info("No content returned for filename, using default.")
            return "default_filename"

        filename = parse_filename_content(content)
        filename = sanitize_filename(filename)

        logging.info(f"Generated filename: {filename}")
        return filename or "default_filename"

    except requests.exceptions.RequestException as e:
        logging.error(f"Network error fetching filename: {str(e)}")
        print(f"Network error: {str(e)}. Using 'default_filename'.")
        return "default_filename"
    except ValueError as e:
        # JSON parsing error
        logging.error(f"Invalid JSON when fetching filename: {str(e)}")
        print("Invalid JSON returned for filename. Using 'default_filename'.")
        return "default_filename"
    except Exception as e:
        logging.error(f"Unexpected error fetching filename: {str(e)}")
        print(f"Unexpected error: {str(e)}. Using 'default_filename'.")
        return "default_filename"

def main():
    # Get user input
    prompt, num_requests = get_user_input()
    payload = create_payload(prompt)

    # Get the filename
    filename = get_filename(prompt)
    
    # Ensure 'results' directory exists
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)  # Creates the directory if it doesn't exist

    output_file = os.path.join(results_dir, f"{filename}.csv")  # Stores the CSV in the 'results' folder
    print(f"Responses will be saved to: {output_file}")
    logging.info(f"Output file: {output_file}")

    # Perform concurrent requests
    print(f"Performing {num_requests} API calls...")
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Response Number", "Response"])

        # Use a ThreadPoolExecutor for concurrency
        with ThreadPoolExecutor(max_workers=min(num_requests, 100)) as executor:
            futures = [executor.submit(fetch_response, payload, i) for i in range(1, num_requests + 1)]

            completed = 0
            total = num_requests
            for future in as_completed(futures):
                request_id, content = future.result()
                writer.writerow([request_id, content])
                completed += 1
                # Show progress to the user
                sys.stdout.write(f"\rFetched {completed}/{total} responses...")
                sys.stdout.flush()

    print(f"\nFinished! Responses saved to {output_file}")
    logging.info(f"Finished! Responses saved to {output_file}")

if __name__ == "__main__":
    main()
