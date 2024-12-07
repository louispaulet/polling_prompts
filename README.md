# polling_prompts

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-blue.svg)](https://github.com/louispaulet/polling_prompts)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/louispaulet/polling_prompts/blob/main/LICENSE)

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Introduction

**polling_prompts** is a Python-based tool designed to interact with AI models by sending a user-defined prompt multiple times (N times) and analyzing the resulting responses. This tool is particularly useful for assessing the consistency, accuracy, and variability of AI-generated answers to the same question.

Whether you're curious about how many "Rs" are in the word "strawberry," the height of the Eiffel Tower, or the length of a banana, **polling_prompts** allows you to gather multiple responses efficiently and analyze them collectively.

## Features

- **Multiple API Calls:** Send a single prompt to an AI model multiple times concurrently.
- **Concurrent Processing:** Utilizes multithreading to perform API calls efficiently.
- **Response Analysis:** Collect and store responses for further analysis.
- **Dynamic Filename Generation:** Automatically generates descriptive filenames based on the prompt.
- **Robust Error Handling:** Handles network issues, invalid responses, and other potential errors gracefully.
- **Logging:** Detailed logging of operations and errors for troubleshooting.
- **Results Organization:** Stores output CSV files in a dedicated `results` folder for better organization.

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/louispaulet/polling_prompts.git
   cd polling_prompts
   ```

2. **Create a Virtual Environment (Optional but Recommended)**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   > **Note:** Ensure you have Python 3.6 or higher installed.

## Usage

1. **Configure the API Endpoint**

   Ensure that the AI service API endpoint is correctly set in the script. By default, it's set to:

   ```python
   url = "http://localhost:1234/v1/chat/completions"
   ```

   Update this URL if your API endpoint differs.

2. **Run the Script**

   ```bash
   python polling_prompts.py
   ```

3. **Follow the Prompts**

   - **Enter your prompt:** Input the question or statement you want to poll the AI with.
   - **Enter the number of API calls to make:** Specify how many times you want the prompt to be sent to the AI.

4. **View Results**

   After completion, the responses will be saved as a CSV file in the `results` folder. The filename is generated based on your prompt for easy identification.

## Examples

Here are some example prompts you can use with **polling_prompts**:

- **Counting Letters:**
  
  *Prompt:* "How many Rs are in the word 'strawberry'?"

- **Factual Information:**
  
  *Prompt:* "What is the height of the Eiffel Tower?"

- **Measuring Objects:**
  
  *Prompt:* "What is the average length of a banana?"

Each prompt will be sent multiple times to the AI, and the varied responses can help in understanding the AI's consistency and reliability.

## Project Structure

```
polling_prompts/
├── results/               # Folder where CSV results are stored
├── polling_prompts.py     # Main Python script
├── app.log                # Log file for debugging and error tracking
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
└── LICENSE                # License information
```

## Contributing

Contributions are welcome! If you'd like to improve **polling_prompts**, please follow these steps:

1. **Fork the Repository**

2. **Create a Feature Branch**

   ```bash
   git checkout -b feature/YourFeature
   ```

3. **Commit Your Changes**

   ```bash
   git commit -m "Add your feature"
   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/YourFeature
   ```

5. **Open a Pull Request**

Please ensure that your code adheres to the existing style and includes appropriate documentation.

## License

This project is licensed under the [MIT License](https://github.com/louispaulet/polling_prompts/blob/main/LICENSE).

## Contact

For any questions, suggestions, or feedback, feel free to reach out:

- **Author:** Louis Paulet
- **GitHub:** [louispaulet](https://github.com/louispaulet)
- **Email:** [your.email@example.com](mailto:your.email@example.com)

---

*Happy Polling!*
