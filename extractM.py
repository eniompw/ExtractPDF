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
    end_index = len(content)
    
    if start_index != -1 and end_index != -1:
        content = content[start_index:end_index].strip()
    
    # Split the content into lines and join them back together with newlines
    return '\n'.join(
        # Remove leading digits and spaces from lines, keeping only the question number and content
        re.sub(r'^(\d{2}\s\d)', r'\1', re.sub(r'^\d+\s+(\d+)', r'\1', line))
        for line in content.split('\n') 
        if line.strip()  # Only include non-empty lines
    )

def extract_question_line(content):
    """Extract a specific question line from the content."""
    pattern = r'^(\d+(?:\s*\([a-z]\))*(?:\s*\([i-v]+\))*)\s*(.*)'
    question_lines = []
    
    for line in content.split('\n'):
        match = re.match(pattern, line.strip())
        if match:
            question_lines.append(line.strip())
    
    return question_lines

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
    process_pdf()
    with open('extracted_marks.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    question_lines = extract_question_line(content)
    for line in question_lines:
        print(line)

if __name__ == "__main__":
    main()
