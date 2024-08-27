import os
import PyPDF2
import re

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        # Extract text from all pages of the PDF, joining them with newlines
        return ''.join(page.extract_text() + "\n" for page in reader.pages)

def clean_content(content):
    """Clean the extracted content by removing unnecessary text and empty lines."""
    content = content.replace('.', '')
    start_index = content.find("Question  Answer  Mark")
    # Set end_index to the last line of the document
    end_index = len(content)
    
    if start_index != -1 and end_index != -1:
        content = content[start_index:end_index].strip()
    
    # Split the content into lines and join them back together with newlines
    return '\n'.join(
        # Create a new list of lines using a list comprehension
        line for line in content.split('\n') 
        # Only include lines that meet both of these conditions:
        if line.strip()  # 1. The line is not empty after stripping whitespace
    )

def process_pdf():
    """Process the PDF file and save the extracted text."""
    # List comprehension to find PDF files in the current directory
    # that end with '.pdf' (case-insensitive) and contain 'question' in their name
    pdf_files = [f for f in os.listdir() if f.lower().endswith('.pdf') and 'mark' in f.lower()]
    if not pdf_files:
        print("No PDF files found in the current directory.")
        return

    output_file_path = 'extracted_marks.txt'
    
    if not os.path.exists(output_file_path):
        pdf_path = "./" + pdf_files[0]
        extracted_marks = extract_text_from_pdf(pdf_path)
        cleaned_content = clean_content(extracted_marks)

        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(cleaned_content)
        print(f"Extracted text and saved to '{output_file_path}'.")
    else:
        print(f"'{output_file_path}' already exists. Skipping extraction.")

def main():
    """Main function to process the PDF and display questions."""
    process_pdf()

if __name__ == "__main__":
    main()
