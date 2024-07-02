# code-hanon: A Coding Practice Tool

`code-hanon` is a command-line tool designed to help you practice and improve your coding skills by creating personalized coding exercises. It provides two main functionalities: analyzing your codebase to extract the most frequent patterns and generating practice exercises based on those patterns. 

## Features

*   **Code Analysis:** Analyzes your codebase to identify and extract the most frequent code patterns, providing insights into your coding patterns.
*   **Practice Generation:** Creates coding exercises tailored to the frequent patterns found in your code, allowing you to practice and reinforce your knowledge.
*   **Customizable Practice:** Adjust the number of practice challenges generated to suit your preferences.
*   **Language Support:** Currently supports analysis and practice generation for specific languages, with more planned for the future.

## Usage

For the time being, the usage of this tool is entirely through the source code. 

1.  **Clone the repository:**

```bash
git clone <repository_url>
```

1. **Navigate to the project directory:**

```bash
cd code-hanon
```

1. **Create virtual environment and install dependencies**

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

1. **Use the `hanon.py` script to invoke the application**

```bash
./hanon.py <command> [args]
```

## Available Commands

### **Analyze**

Analyze a set of directories for a given language and extract the most common patterns.

```bash
./hanon.py analyze -l <language> -o <output_directory> <directories_to_analyze>
```

*   `-l, --language`: Specify the programming language to analyze (e.g., Python).
*   `-o, --output`: (Optional) Specify the output directory for storing the extracted patterns (default is "exercises").
*   `<directories_to_analyze>`: List the directories you want to analyze.

### **Practice**

Practice using the set of extracted patterns from the `analyze` command. You can also edit the `patterns.txt` file to
manually define the patterns to practice with.

```bash
./hanon.py practice -i <input_directory> -c <challenge_count>
```

*   `-i, --input-directory`: (Optional) Specify the directory containing the generated practice exercises (default is "exercises").
*   `-c, --count`: (Optional) Specify the number of coding challenges to generate (default is 25).

### **Stats**

Display your current performance metrics. These include the latency per ngram and pattern, and the error rate. Stats
will not be considered significant unless there are at least 3 samples of the same ngram and pattern. 

```bash
./hanon.py stats [-s error_rate|latency]
```

*   `-s, --sort-by`: (Optional) Specify the criteria by which to sort the stats (`latency` or `error_rate`).

## Contributing
Contributions to code-hanon are welcome! Please feel free to submit bug reports, feature requests, or pull requests.

## License
This project is licensed under the GPL license.

## Disclaimer
This README.md file is generated based on the provided entrypoint file and may not be fully comprehensive. Please refer to the project's official documentation for more detailed information.




