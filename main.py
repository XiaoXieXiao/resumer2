import json
import pdfkit
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted


class ResumeGenerator:
    """
    A class to generate resumes in either Portuguese or English using Google's Generative AI API.
    """

    def __init__(self, secrets_file="data/secret.json", model_name='gemini-1.5-pro-latest'):
        """
        Initializes the ResumeGenerator class.

        Args:
            secrets_file: Path to the file containing the API key (default: "data/secret.json").
            model_name: Name of the generative model to use (default: "gemini-1.5-pro-latest").

        Prompts the user to choose the language.
        """
        self.secrets_file = secrets_file
        self.model_name = model_name

        # Parse API key from secrets file
        self.api_key = self.get_api_key()

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 0,
                "max_output_tokens": 8192,
            },
            safety_settings={
                "HARASSMENT": "BLOCK_NONE",
                "HATE": "BLOCK_NONE",
                "SEXUAL": "BLOCK_NONE",
                "DANGEROUS": "BLOCK_NONE",
            }
        )

        self.chat = self.model.start_chat(history=[])

        # Get language input from the user
        while True:
            self.language = input("Enter desired language (pt for Portuguese, eng for English): ").lower()
            if self.language in ("pt", "eng"):
                break
            else:
                print("Invalid language. Please enter 'pt' or 'eng'.")

    @staticmethod
    def get_data(json_file):
        """
        Reads JSON data from a file.

        Args:
            json_file: Path to the JSON file.

        Returns:
            The data loaded from the JSON file.
        """
        with open(json_file, encoding='utf-8') as f:
            json_data = json.load(f)
        return json_data

    def get_api_key(self):
        """
        Retrieves the API key from the secrets file.

        Returns:
            The API key if found, otherwise None.
        """
        try:
            secrets = self.get_data(self.secrets_file)
            return secrets['api-key']
        except (FileNotFoundError, KeyError):
            print("Error: API key not found in 'secret.json'. Please check the file.")
            return None

    @staticmethod
    def fill_template(html_template, data):
        """
        Fills a template with available JSON data, leaving unfilled placeholders.

        Args:
            html_template: The HTML template string.
            data: A dictionary containing the data to fill the template.

        Returns:
            The filled HTML template with available data replaced, and remaining placeholders untouched.
        """
        for key, value in data.items():
            if isinstance(value, dict):
                for inner_key, inner_value in value.items():
                    html_template = html_template.replace(f"{{{key}.{inner_key}}}", str(inner_value))
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    html_template = html_template.replace(f"{{{key}[{i}]}}", str(item))
            else:
                html_template = html_template.replace(f"{{{key}}}", str(value))
        return html_template

    def create_template(self, data_pt=None, data_eng=None):
        """
        Fills templates with available JSON data, leaving unfilled placeholders.

        Args:
            data_pt: Data in the Portuguese language.
            data_eng: Data in the English language.

        Returns:
            Filled HTML templates, with available data replaced in their respective languages, and remaining placeholder
            untouched.
        """
        datas = [data_pt, data_eng]
        templates = []

        for data in datas:
            if 'pt' in str(data):
                lang = 'pt'
            elif 'eng' in str(data):
                lang = 'eng'
            else:
                lang = 'Unknown'

            template = f"template-{lang}.html"

            if data is not None:
                with open(f"template/{template}", "r", encoding='utf-8') as f:
                    html_template = f.read()
                lang_filled = self.fill_template(html_template, data)
                templates.append(lang_filled)
        return templates

    def create_resume(self, personal, prompt_file):
        """
        Generates a resume based on user input and data.

        Args:
            personal: Personal data dictionary.
            prompt_file: Path to the JSON file containing the prompt parts.
        """
        job = input("Titulo da vaga | Job tittle: ")
        description = input("Descrição da vaga | Job description: ")
        # objectives, personal characteristics, qualifications
        fields = "Objetivo; Características Pessoais; Resumo das qualificações;"

        # Load prompt_parts from the file
        prompt_parts = []  # This line is now correct!

        prompts = self.get_data('data/prompt-parts.json')

        for prompt in prompts:
            i = 0
            j = 0

            for key in list(prompt):
                a = key
                b = prompts[j][a]

                linha = a + ": " + b

                i += 1
                prompt_parts.append(linha)

            j += 1

        input_job = "input: " + job
        input_description = "DESCRICAO: " + description  # DESCRICAO = DESCRIPTION
        input_personal = "PESSOAL: " + str(personal)  # PESSOAL = PERSONAL
        input_fields = "CAMPOS: " + fields  # CAMPOS = FIELDS
        output_string = "output: "

        inputs = [input_job, input_description, input_personal, input_fields, output_string]
        for input_i in inputs:
            prompt_parts.append(input_i)

        try:
            response = self.chat.send_message(prompt_parts)
        except ResourceExhausted:
            print("Google API request limit reached. Please try again later.")
            return

        response_text = response.text

        # Split the text based on double newlines, assuming each section is separated by them
        sections = response_text.split("\n\n")

        # Assign each section to a variable
        objectives_pt, characteristics_pt, qualifications_pt = sections

        objectives_pt = objectives_pt.split(":", 1)[1].strip()
        characteristics_pt = characteristics_pt.split(":", 1)[1].strip()
        qualifications_pt = qualifications_pt.split(":", 1)[1].strip()

        data = {
            "objetivo": objectives_pt,  # objetivo = objectie
            "pessoais": characteristics_pt,  # pessoais = personal
            "resumo": qualifications_pt,  # resumo = summary
        }

        # Read the HTML template from a file
        with open("template/template-pt.html", "r", encoding='utf-8') as f:
            html_template = f.read()

        # Fill the template with data and print the result
        filled_html = self.fill_template(html_template, data)

        # Convert HTML to PDF
        pdfkit.from_string(filled_html, 'output.pdf')  # You can change 'output.pdf' to your desired filename

        objective = ""
        caracteristics = ""
        qualifications = ""

        answers = [objectives_pt, characteristics_pt, qualifications_pt]
        answers_eng = [objective, caracteristics, qualifications]
        # Translate to english without changing the format, only translate
        prompt = "Traduza para inglês sem mudar o formato, apenas traduza "

        for i in answers:
            k = 0
            try:
                answer_text = self.chat.send_message(prompt + i)
            except ResourceExhausted:
                print("Google API request limit reached. Please try again later.")
                return
            answers_eng[k] = answer_text.text
            k += 1

        data_eng = {
            "objective": objective,
            "pessoais": caracteristics,
            "resumo": qualifications,
        }

        # Read the HTML template from a file
        with open("template/template-eng.html", "r", encoding='utf-8') as f:
            html_template = f.read()

        # Fill the template with data and print the result
        filled_html = self.fill_template(html_template, data_eng)

        # Convert HTML to PDF
        pdfkit.from_string(filled_html, 'output-eng.pdf')  # You can change 'output.pdf' to your desired filename

        return print("Resumes created successfully!")

    def generate_resumes(self):
        """
        Main function to handle resume generation based on the selected language.
        """
        personal_pt = self.get_data('data/data-pt.json')
        personal_eng = self.get_data('data/data-eng.json')

        self.create_template(personal_pt, personal_eng)

        if self.language == "pt":
            prompt = self.get_data('data/prompt-parts.json')
            self.create_resume(personal_pt, prompt)  # Pass the file path
        elif self.language == "eng":
            prompt = self.get_data('data/prompt-parts.json')
            self.create_resume(personal_eng, prompt)  # Pass the file path
        else:
            print("Invalid language")


if __name__ == '__main__':
    """
    This is the main execution block of the script.

    To use this script:

    1. Ensure you have a 'secret.json' file in the 'data' folder containing your Google Generative AI API key:
       ```json
       {
           "api-key": "YOUR_API_KEY_HERE"
       }
       ```

    2. Run the script. It will prompt you for:
       - Job title
       - Job description

    3. The script will then generate a resume in the chosen language as a PDF file.
    """
    resume_generator = ResumeGenerator()
    resume_generator.generate_resumes()
