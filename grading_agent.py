"""
GradingAgent: An automated grading system using ChatGPT API
Loads rubrics, student papers, grades them, and outputs results for mail merge
"""

import os
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
import openai
from docx import Document
import PyPDF2
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('grading_log.txt'),
        logging.StreamHandler()
    ]
)

class GradingAgent:
    """Main class for the automated grading system"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize the GradingAgent
        
        Args:
            api_key (str): OpenAI API key
            model (str): OpenAI model to use for grading
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.rubric = None
        self.students_data = []
        self.graded_results = []
        self.instructor_config = None
        
    def load_instructor_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load instructor grading configuration
        
        Args:
            config_path (str): Path to the instructor config JSON file
            
        Returns:
            Dict: Loaded configuration data
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.instructor_config = config
                print(f"✅ Loaded instructor configuration: {config.get('instructor_name', 'Unknown')}")
                print(f"   Grading style: {config.get('grading_philosophy', 'Standard')}")
                return config
        except FileNotFoundError:
            print(f"❌ Instructor config file not found: {config_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in instructor config: {e}")
            return {}
        except Exception as e:
            print(f"❌ Error loading instructor config: {e}")
            return {}
        
    def load_rubric(self, rubric_path: str) -> Dict[str, Any]:
        """
        Load grading rubric from JSON file
        
        Args:
            rubric_path (str): Path to the rubric JSON file
            
        Returns:
            Dict: Loaded rubric data
        """
        try:
            with open(rubric_path, 'r', encoding='utf-8') as file:
                self.rubric = json.load(file)
            logging.info(f"Rubric loaded successfully from {rubric_path}")
            return self.rubric
        except Exception as e:
            logging.error(f"Error loading rubric: {str(e)}")
            raise
    
    def load_student_papers(self, papers_folder: str) -> List[Dict[str, str]]:
        """
        Load student papers from a folder (supports .txt, .docx, .pdf)
        
        Args:
            papers_folder (str): Path to folder containing student papers
            
        Returns:
            List[Dict]: List of student paper data
        """
        papers_path = Path(papers_folder)
        self.students_data = []
        
        supported_extensions = ['.txt', '.docx', '.pdf']
        
        for file_path in papers_path.iterdir():
            if file_path.suffix.lower() in supported_extensions:
                try:
                    student_name = file_path.stem
                    content = self._extract_text_from_file(file_path)
                    
                    self.students_data.append({
                        'name': student_name,
                        'filename': file_path.name,
                        'content': content
                    })
                    logging.info(f"Loaded paper for {student_name}")
                    
                except Exception as e:
                    logging.error(f"Error loading {file_path.name}: {str(e)}")
                    
        logging.info(f"Loaded {len(self.students_data)} student papers")
        return self.students_data
    
    def _extract_text_from_file(self, file_path: Path) -> str:
        """
        Extract text content from different file types
        
        Args:
            file_path (Path): Path to the file
            
        Returns:
            str: Extracted text content
        """
        # Enhanced debugging for the file path parameter
        print(f"🔍 _extract_text_from_file called with: {repr(file_path)}")
        print(f"🔍 file_path type: {type(file_path)}")
        
        if file_path is None:
            raise ValueError("file_path cannot be None")
        
        if not isinstance(file_path, Path):
            print(f"⚠️ file_path is not a Path object, converting from: {type(file_path)}")
            try:
                file_path = Path(file_path)
            except Exception as e:
                raise ValueError(f"Cannot convert file_path to Path object: {e}")
        
        print(f"🔍 Working with Path object: {file_path}")
        print(f"🔍 Path exists: {file_path.exists()}")
        
        extension = file_path.suffix.lower()
        print(f"🔍 File extension: {extension}")
        
        if extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
                
        elif extension == '.docx':
            print(f"🔍 Processing DOCX file: {file_path}")
            doc = Document(file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            
        elif extension == '.pdf':
            print(f"🔍 Processing PDF file: {file_path}")
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ''
                for page in pdf_reader.pages:
                    text += page.extract_text() + '\n'
                return text
                
        elif extension in ['.html', '.htm']:
            print(f"🔍 Processing HTML file: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
                
        elif extension in ['.rtf', '.odt']:
            print(f"🔍 Processing {extension.upper()} file as text: {file_path}")
            # Try to read as text file for basic content extraction
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            except UnicodeDecodeError:
                # Try with different encoding
                try:
                    with open(file_path, 'r', encoding='latin-1') as file:
                        return file.read()
                except Exception as e:
                    raise ValueError(f"Could not read {extension} file with available methods: {e}")
                
        else:
            raise ValueError(f"Unsupported file type: {extension}")
    
    def grade_paper(self, student_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Grade a single student paper using ChatGPT
        
        Args:
            student_data (Dict): Student paper data
            
        Returns:
            Dict: Grading results
        """
        if not self.rubric:
            raise ValueError("Rubric not loaded. Please load a rubric first.")
        
        # Construct the grading prompt
        prompt = self._build_grading_prompt(student_data['content'])
        
        try:
            # Build system message based on instructor configuration
            system_message = self._build_system_message()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Parse the response
            grading_result = self._parse_grading_response(
                response.choices[0].message.content,
                student_data['name']
            )
            
            logging.info(f"Graded paper for {student_data['name']}")
            return grading_result
            
        except Exception as e:
            logging.error(f"Error grading paper for {student_data['name']}: {str(e)}")
            raise
    
    def _build_system_message(self) -> str:
        """
        Build the system message for ChatGPT based on instructor configuration
        
        Returns:
            str: Customized system message
        """
        if self.instructor_config and self.instructor_config.get('custom_system_message'):
            # Use custom system message from configuration
            base_message = self.instructor_config['custom_system_message']
        else:
            # Default system message
            base_message = "You are an expert academic grader. Provide detailed, constructive feedback based on the given rubric."
        
        # Add additional instructions if available
        if self.instructor_config:
            additional_instructions = []
            
            # Add grading philosophy
            if philosophy := self.instructor_config.get('grading_philosophy'):
                additional_instructions.append(f"Your grading approach should be {philosophy}.")
            
            # Add specific instructions
            if specific_instructions := self.instructor_config.get('specific_instructions'):
                additional_instructions.extend(specific_instructions)
            
            # Add comment preferences
            if comment_prefs := self.instructor_config.get('comment_preferences'):
                if comment_prefs.get('include_strengths'):
                    additional_instructions.append("Always highlight what the student did well.")
                if comment_prefs.get('include_suggestions'):
                    additional_instructions.append("Provide specific suggestions for improvement.")
                if comment_prefs.get('personal_touch'):
                    additional_instructions.append("Make comments personal and encouraging.")
            
            if additional_instructions:
                base_message += " " + " ".join(additional_instructions)
        
        return base_message
    
    def _build_grading_prompt(self, paper_content: str) -> str:
        """
        Build the grading prompt for ChatGPT
        
        Args:
            paper_content (str): The student's paper content
            
        Returns:
            str: Formatted prompt
        """
        rubric_str = json.dumps(self.rubric, indent=2)
        
        # Build context from instructor configuration
        context_parts = []
        
        if self.instructor_config:
            if course_context := self.instructor_config.get('course_context'):
                context_parts.append(f"COURSE CONTEXT:")
                context_parts.append(f"- Course level: {course_context.get('course_level', 'Not specified')}")
                context_parts.append(f"- Course type: {course_context.get('course_type', 'Not specified')}")
                context_parts.append(f"- Student background: {course_context.get('student_background', 'Mixed levels')}")
                
                if learning_objectives := course_context.get('learning_objectives'):
                    context_parts.append(f"- Learning objectives: {', '.join(learning_objectives)}")
                context_parts.append("")
            
            if expertise := self.instructor_config.get('subject_expertise'):
                context_parts.append(f"INSTRUCTOR EXPERTISE: {', '.join(expertise)}")
                context_parts.append("")
        
        context_str = '\n'.join(context_parts) if context_parts else ""
        
        prompt = f"""
Please grade the following student paper based on the provided rubric. 

{context_str}RUBRIC:
{rubric_str}

STUDENT PAPER:
{paper_content}

Please provide your response in the following JSON format:
{{
    "overall_score": <total_points>,
    "max_possible_score": <maximum_points>,
    "percentage": <percentage_score>,
    "letter_grade": "<letter_grade>",
    "criteria_scores": {{
        "<criterion_name>": {{
            "score": <points>,
            "max_score": <max_points>,
            "feedback": "<specific_feedback>"
        }}
    }},
    "overall_feedback": "<comprehensive_feedback>",
    "strengths": ["<strength1>", "<strength2>"],
    "areas_for_improvement": ["<improvement1>", "<improvement2>"]
}}

Be specific, constructive, and fair in your grading. Provide actionable feedback.
"""
        return prompt
    
    def _parse_grading_response(self, response_text: str, student_name: str) -> Dict[str, Any]:
        """
        Parse ChatGPT's grading response
        
        Args:
            response_text (str): Raw response from ChatGPT
            student_name (str): Student's name
            
        Returns:
            Dict: Parsed grading results
        """
        try:
            # Extract JSON from the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            json_str = response_text[start_idx:end_idx]
            
            grading_data = json.loads(json_str)
            grading_data['student_name'] = student_name
            grading_data['grading_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            return grading_data
            
        except Exception as e:
            logging.error(f"Error parsing grading response: {str(e)}")
            # Return a default structure if parsing fails
            return {
                'student_name': student_name,
                'overall_score': 0,
                'max_possible_score': 100,
                'percentage': 0,
                'letter_grade': 'F',
                'criteria_scores': {},
                'overall_feedback': f"Error in grading: {str(e)}",
                'strengths': [],
                'areas_for_improvement': [],
                'grading_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def grade_all_papers(self) -> List[Dict[str, Any]]:
        """
        Grade all loaded student papers
        
        Returns:
            List[Dict]: All grading results
        """
        if not self.students_data:
            raise ValueError("No student papers loaded.")
        
        self.graded_results = []
        
        for student_data in self.students_data:
            try:
                result = self.grade_paper(student_data)
                self.graded_results.append(result)
            except Exception as e:
                logging.error(f"Failed to grade {student_data['name']}: {str(e)}")
                
        logging.info(f"Completed grading {len(self.graded_results)} papers")
        return self.graded_results
    
    def export_results(self, output_format: str = 'xlsx', filename: Optional[str] = None) -> str:
        """
        Export grading results to Excel or CSV for mail merge
        
        Args:
            output_format (str): 'xlsx' or 'csv'
            filename (str, optional): Output filename
            
        Returns:
            str: Path to the exported file
        """
        if not self.graded_results:
            raise ValueError("No grading results to export.")
        
        # Create DataFrame for export
        export_data = []
        
        for result in self.graded_results:
            row = {
                'Student_Name': result['student_name'],
                'Overall_Score': result['overall_score'],
                'Max_Score': result['max_possible_score'],
                'Percentage': result['percentage'],
                'Letter_Grade': result['letter_grade'],
                'Overall_Feedback': result['overall_feedback'],
                'Strengths': '; '.join(result.get('strengths', [])),
                'Areas_for_Improvement': '; '.join(result.get('areas_for_improvement', [])),
                'Grading_Date': result['grading_date']
            }
            
            # Add individual criteria scores
            for criterion, details in result.get('criteria_scores', {}).items():
                row[f'{criterion}_Score'] = details.get('score', 0)
                row[f'{criterion}_Feedback'] = details.get('feedback', '')
            
            export_data.append(row)
        
        df = pd.DataFrame(export_data)
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'grading_results_{timestamp}.{output_format}'
        
        # Export based on format
        if output_format.lower() == 'xlsx':
            df.to_excel(filename, index=False)
        elif output_format.lower() == 'csv':
            df.to_csv(filename, index=False, encoding='utf-8')
        else:
            raise ValueError("Unsupported format. Use 'xlsx' or 'csv'.")
        
        logging.info(f"Results exported to {filename}")
        return filename
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """
        Generate a summary report of all grading results
        
        Returns:
            Dict: Summary statistics
        """
        if not self.graded_results:
            return {}
        
        scores = [result['percentage'] for result in self.graded_results]
        letter_grades = [result['letter_grade'] for result in self.graded_results]
        
        summary = {
            'total_papers': len(self.graded_results),
            'average_score': sum(scores) / len(scores),
            'highest_score': max(scores),
            'lowest_score': min(scores),
            'grade_distribution': pd.Series(letter_grades).value_counts().to_dict(),
            'completion_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return summary


def main():
    """Example usage of the GradingAgent"""
    # Initialize with your OpenAI API key
    api_key = input("Enter your OpenAI API key: ")
    agent = GradingAgent(api_key)
    
    try:
        # Load rubric
        rubric_file = input("Enter path to rubric JSON file: ")
        agent.load_rubric(rubric_file)
        
        # Load student papers
        papers_folder = input("Enter path to folder containing student papers: ")
        agent.load_student_papers(papers_folder)
        
        # Grade all papers
        print("Grading papers...")
        results = agent.grade_all_papers()
        
        # Export results
        output_format = input("Export format (xlsx/csv): ").lower()
        output_file = agent.export_results(output_format)
        
        # Generate summary
        summary = agent.generate_summary_report()
        print(f"\nGrading Summary:")
        print(f"Total papers: {summary['total_papers']}")
        print(f"Average score: {summary['average_score']:.2f}%")
        print(f"Results exported to: {output_file}")
        
    except Exception as e:
        logging.error(f"Error in main execution: {str(e)}")
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
