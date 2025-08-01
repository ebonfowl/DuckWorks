# GradingAgent Configuration
# Copy this file to config.py and fill in your settings

# OpenAI API Configuration
OPENAI_API_KEY = "your-openai-api-key-here"

# Default file paths
DEFAULT_RUBRIC_PATH = "./sample_rubric.json"
DEFAULT_PAPERS_FOLDER = "./student_papers"
DEFAULT_OUTPUT_FOLDER = "./grading_results"

# Grading settings
DEFAULT_OUTPUT_FORMAT = "xlsx"  # "xlsx" or "csv"
GPT_MODEL = "gpt-4"  # or "gpt-3.5-turbo" for lower cost
TEMPERATURE = 0.3  # Lower = more consistent, Higher = more creative

# Logging settings
LOG_LEVEL = "INFO"
LOG_FILE = "grading_log.txt"

# Mail merge settings
MAIL_MERGE_TEMPLATE = """
Dear {Student_Name},

Your term paper has been graded. Here are your results:

Overall Score: {Overall_Score}/{Max_Score} ({Percentage}%)
Letter Grade: {Letter_Grade}

Overall Feedback:
{Overall_Feedback}

Strengths:
{Strengths}

Areas for Improvement:
{Areas_for_Improvement}

Detailed Criterion Feedback:
{detailed_feedback}

If you have any questions about your grade, please feel free to reach out during office hours.

Best regards,
[Your Name]
"""
