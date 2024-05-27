# resumer2

resumer2 is a Python-based tool for generating resumes in either Portuguese or English using Google's Generative AI API. By leveraging advanced AI capabilities, this tool produces professional resumes based on user inputs such as job title and description, and it automatically translates the content to the desired language.

## Features

- Generate professional resumes in both Portuguese and English.
- Automatically translate resume content to the desired language.
- Customize resumes based on user inputs such as job title and description.

## Requirements

- Python 3.7 or higher
- [Google's Generative AI API](https://cloud.google.com/gen-ai)
- Required Python libraries: google-generativeai, pdfkit, requests

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/XiaoXieXiao/resumer2.git
    ```
2. Navigate to the project directory:
    ```bash
    cd resumer2
    ```
3. Install the required Python libraries:
    ```bash
    pip install -q -U google-generativeai
    pip install pdfkit
    pip install google-api-core
    pip install requests
    ```

## Setup

1. Obtain API credentials for Google's Generative AI API and save the JSON key file as `secret.json` in the project directory or input your key in the `secret.json` pre-existing file.

## Usage

1. Run the main script:
    ```bash
    python resumer2.py
    ```
2. Follow the prompts to input the job title, job description, and desired language.

## Example

When you run the script, you will be prompted to enter the job title, job description, and the desired language for the resume. For example:

Enter the job title: Software Engineer
Enter the job description: Develop and maintain software applications.
Enter the language (en for English, pt for Portuguese): en

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Acknowledgements

- Google's Generative AI API for providing the underlying AI capabilities.
- The Python community for various open-source libraries and tools.
