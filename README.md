# code-hanon: A Coding Practice Tool

`code-hanon` is a command-line tool designed to help you practice and improve your coding skills by creating personalized coding exercises. It provides two main functionalities: analyzing your codebase to extract the most frequent expressions and generating practice exercises based on those expressions. 

## Features

*   **Code Analysis:** Analyzes your codebase to identify and extract the most frequent code expressions, providing insights into your coding patterns.
*   **Practice Generation:** Creates coding exercises tailored to the frequent expressions found in your code, allowing you to practice and reinforce your knowledge.
*   **Customizable Practice:** Adjust the number of practice challenges generated to suit your preferences.
*   **Language Support:** Currently supports analysis and practice generation for specific languages, with more planned for the future.

## Usage

1.  **Clone the repository:**

```bash
git clone <repository_url>
```

1. **Navigate to the project directory:**

```bash
cd code-hanon
```

1. **Use the `hanon.py` script to invoke the application**

```bash
python3 hanon.py <command> [args]
```

## Available Commands

- **Analyze**
```bash
python3 hanon.py analyze -l <language> -o <output_directory> <directories_to_analyze>
```

*   `-l, --language`: Specify the programming language to analyze (e.g., Python).
*   `-o, --output`: (Optional) Specify the output directory for storing the extracted expressions (default is "exercises").
*   `<directories_to_analyze>`: List the directories you want to analyze.

- **Practice**
```bash
python3 hanon.py practice -i <input_directory> -c <challenge_count>
```

*   `-i, --input-directory`: (Optional) Specify the directory containing the generated practice exercises (default is "exercises").
*   `-c, --count`: (Optional) Specify the number of coding challenges to generate (default is 25).

## Contributing
Contributions to code-hanon are welcome! Please feel free to submit bug reports, feature requests, or pull requests.

## License
This project is licensed under the MIT license.

## Disclaimer
This README.md file is generated based on the provided entrypoint file and may not be fully comprehensive. Please refer to the project's official documentation for more detailed information.




