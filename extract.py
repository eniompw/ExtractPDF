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
    year = input("Enter the year of the exam paper (e.g., 2023): ")
    content = content.replace('.', '')
    start_index = content.find(f"© OCR {year}")
    end_index = content.find("END OF QUESTION PAPER")
    
    if start_index != -1 and end_index != -1:
        content = content[start_index:end_index].strip()
    
    return '\n'.join(line for line in content.split('\n') 
                     if line.strip() 
                     and f"Turn  over © OCR {year}" not in line 
                     and f"© OCR {year}" not in line
                     and not line.strip().isdigit())

def process_pdf():
    """Process the PDF file and save the extracted text."""
    pdf_files = [f for f in os.listdir() if f.lower().endswith('.pdf') and 'question' in f.lower()]
    if not pdf_files:
        print("No PDF files found in the current directory.")
        return

    output_file_path = 'extracted_questions.txt'
    
    if not os.path.exists(output_file_path):
        pdf_path = "./" + pdf_files[0]
        extracted_questions = extract_text_from_pdf(pdf_path)
        cleaned_content = clean_content(extracted_questions)

        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(cleaned_content)
        print(f"Extracted text and saved to '{output_file_path}'.")
    else:
        print(f"'{output_file_path}' already exists. Skipping extraction.")

def analyze_content():
    """Analyze the content of the extracted text file."""
    with open('extracted_questions.txt', 'r', encoding='utf-8') as input_file:
        content = input_file.read()

    # Define regular expression patterns for identifying different parts of the question structure
    patterns = {
        'question_stem_line': r'^\d+[\s*].*[a-z].*$',  # Matches lines starting with a number, followed by text containing lowercase letters
        'subquestion_line': r'^\s*\([a-z]+\).*',       # Matches lines starting with a lowercase letter in parentheses
        'marks_line': r'.*\[.*\].*'                    # Matches lines containing square brackets (typically used for marks)
    }

    # Create a dictionary of match objects for each pattern
    # Uses re.finditer() to find all non-overlapping matches
    # re.MULTILINE allows ^ and $ to match line beginnings and ends
    return content, {key: list(re.finditer(pattern, content, re.MULTILINE)) 
                     for key, pattern in patterns.items()}

def select_question(content, matches, question_number):
    """Select a specific question from the content."""
    question_stems = matches['question_stem_line']
    if question_number < 1 or question_number > len(question_stems):
        print(f"Invalid question number. Please choose between 1 and {len(question_stems)}.")
        return None, None, None, None, None

    selected_stem = question_stems[question_number - 1]
    next_stem = question_stems[question_number] if question_number < len(question_stems) else None
    
    start = selected_stem.end()
    end = next_stem.start() if next_stem else len(content)
    
    # Filter subquestions that fall within the current question's range (between start and end)
    # and extract the content of the current question
    subquestions = [sq for sq in matches['subquestion_line'] if start <= sq.start() < end]
    question_content = content[start:end].strip()
    
    return question_content, subquestions, start, end, selected_stem.group()

def display_subquestion(question_content, subquestions, subq_index, start, end):
    """Display a specific subquestion."""
    if 0 <= subq_index < len(subquestions):
        subq = subquestions[subq_index]
        next_subq = subquestions[subq_index + 1] if subq_index + 1 < len(subquestions) else None
        
        subq_start = subq.start() - start
        subq_end = (next_subq.start() - start) if next_subq else len(question_content)
        
        subq_text = question_content[subq_start:subq_end].strip()
        
        lines = [line.strip() for line in subq_text.split('\n') if line.strip()]
        content = [subq.group().strip()]
        
        content.extend([line for line in lines[1:] if not re.match(r'^\s*\([a-z]+\)', line)])
        
        return '\n'.join(content)
    else:
        return "Invalid subquestion index."

def main():
    """Main function to process the PDF and display questions."""
    process_pdf()
    # Analyze the content of the extracted questions file
    # Returns the full content and a dictionary of regex matches for different question components
    content, matches = analyze_content()
    
    question_stems = matches['question_stem_line']
    total_questions = len(question_stems)
    
    while True:
        try:
            question_number = int(input(f"Enter the question number (1-{total_questions}) or 0 to quit: "))
            if question_number == 0:
                break
            if 1 <= question_number <= total_questions:
                question_content, subquestions, start, end, question_stem = select_question(content, matches, question_number)
                
                if question_stem is not None:
                    print(f"\nQuestion {question_number}:")
                    print(question_stem)
                    
                    if subquestions:
                        for subq_index, subq in enumerate(subquestions):
                            subq_content = display_subquestion(question_content, subquestions, subq_index, start, end)
                            print(subq_content)
                            
                            # Check if the last line contains marks
                            if re.search(r'.*\[.*\].*', subq_content.split('\n')[-1]):
                                user_input = input("Press 0 to quit, or any other key to continue: ").lower()
                                if user_input == '0':
                                    break
                    else:
                        print("No subquestions available for this question.")
                else:
                    print(f"Question {question_number} not found.")
            else:
                print(f"Invalid question number. Please choose between 1 and {total_questions}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()
