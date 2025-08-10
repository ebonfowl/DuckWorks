# 🦆 DUCKWORKS SUITE 

**Educational Automation That Just Works!** 

DuckWorks is a collection of AI-powered tools designed to enhance educational productivity through desktop automation. All tools are controlled by a single, modern graphical user interface.

## [DuckGrade](#-duckgrade---ai-powered-assignment-grading)

DuckGrade is the first tool in the **DuckWorks Educational Automation Suite**. It leverages AI to automate a large proportion of the grading process and save educators time. It has many advanced features such as direct integration with learning management systems, submission anonymization, fully custimizable grading options, course material uploads, precise cost estimation (don't worry, OpenAI's API is almost free), and GUI-based grading review.

**Coming Soon**: DuckTest, DuckBuild

## Installation

1. **Clone or download this repository** to your local machine

2. **Ensure Conda environment is active** (already set up in your workspace)

3. **All required packages are already installed**:
   - openai
   - pandas
   - openpyxl
   - python-docx
   - PyPDF2
   - requests (for Canvas API)
   - tiktoken
   - PyQt

**Note:** This project uses its own conda environment located in a `.conda/` folder within the working directory. This is a standard conda environment set up, but all batch files will refer to that folder to execute the GUI script so you must have your environment set up in the same way to take advantage of the batch files.

**Coming Soon:** Windows executable with compiled C++ binaries! (No more conda stuff)

## Quick Start

### 🌟 Enhanced Versions (RECOMMENDED - New Features!)

#### **Command Line**
```powershell
.conda\python.exe duckgrade_canvas_complete.py
```
**Or simply double-click:** `start_duckgrade_canvas_direct.bat`

## Setup Instructions

### 1. Get OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Copy and save your API key securely

### 2. Get Canvas API Token
1. Log into your Canvas LMS instance
2. Click on your account profile (top left corner)
3. Select "Settings" from the dropdown menu
4. Scroll down to "Approved Integrations" section
5. Click "+ New Access Token" button
6. Enter a purpose/description (e.g., "DuckGrade Automation")
7. Set an expiration date (optional but recommended)
8. Click "Generate Token"
9. **Important**: Copy the token immediately - it will only be shown once
10. Store the token securely (you'll need it for DuckGrade configuration) 

### 3. Connect
1. Launch the GUI: `.conda\python.exe duckgrade_canvas_complete.py` (or double-click `start_duckgrade_canvas_direct.bat`)
2. Enter your OpenAI API key
3. Enter Canvas API token
4. (Optional) Save your configuration so it can be loaded again later

## [Development Roadmap](#development-roadmap-1)

See what we have planned for the future of DuckWorks! Big things are coming...

--- 

# 🦆 DuckGrade - AI-Powered Assignment Grading
## Part of the DuckWorks Educational Automation Suite

DuckGrade is an intelligent grading system that uses OpenAI's ChatGPT API to automatically grade student assignments based on customizable rubrics and generate comprehensive feedback. Now with **Canvas LMS integration**, **encrypted API key storage**, **AI grader instructor configuration**, **multi-file submission support**, **course material uploads**, **OpenAI pricing transparency**, and **professional GUI with duck branding**!

## 🚀 Duckgrade Features

- 🤖 **AI-Powered Grading**: Uses latest OpenAI models for intelligent submission evaluation
- 🔐 **Secure Key Storage**: Encrypted API key storage with master password protection
- 🔒 **Privacy Protection**: Student names anonymized for ChatGPT processing
- 🎛️ **Model Selection**: Choose from current OpenAI models with real-time pricing
- 📋 **Direct Rubric Download**: Download an existing Canvas rubric instead of making a new one
- 📋 **Customizable Rubrics**: JSON-based rubric system for flexible grading criteria
- 🎓 **Instructor Configuration**: Tell the AI to behave exactly as you want it to while grading
- 📄 **Multiple File Formats**: Supports .txt, .docx, .pdf submissions and many other types
- 📁 **Multi-File Submissions**: Submissions can contain multiple files (lab report/data, etc.)
- 📊 **Excel/CSV Output**: Generates backup grading data in tabular format
- 🎯 **Detailed Feedback**: Provides specific feedback for each rubric criterion
- 🖥️ **GUI Interface**: User-friendly graphical interface for easy operation
- 📈 **Summary Reports**: Generates class performance statistics 
- 🌐 **Canvas LMS Integration**: Automatically download submissions and upload grades
- ⚡ **Complete Automation**: Full workflow from Canvas download to grade upload
- 📄 **Course Material Uploads**: Upload your course materials to use during grading
- 📈 **OpenAI pricing transparency**: Create a budget to track AI usage costs with accurate estimation 

## Instructions

1. Choose course and assignment from dropdowns
2. (Optional) Select an instructor personality configuration or create a new one
3. Select your rubric file or tell the grader to download the assignment rubric from Canvas
4. (Optional) Add any additional grading instructions
5. Start Step 1: Download submissions
6. (Optional) Add course materials for grading context
7. Review the budget and cost estimations
8. Start Step 2: AI Grading
9. Review grades and comments in the integrated Review tab and make changes where necessary
10. Save your changes
11. Start Step 3: Push grades and comments back to Canvas

## Rubric Format

Create a JSON file with the following structure:

```json
{
  "assignment_title": "Your Assignment Title",
  "total_points": 100,
  "criteria": {
    "criterion_name": {
      "description": "What this criterion evaluates",
      "points": 25,
      "levels": {
        "excellent": {
          "points": "23-25",
          "description": "Excellent performance description"
        },
        "good": {
          "points": "20-22",
          "description": "Good performance description"
        }
      }
    }
  },
  "grading_scale": {
    "A": {"min": 90, "max": 100},
    "B": {"min": 80, "max": 89}
  }
}
```

## Output Format

The system generates a spreadsheet with the following columns:

### Student Information
- `Student_Name`: Student's name (never sent to AI)
- `Canvas_User_ID`: unique Canvas identifier
- `AI_Score`: Total points earned
- `Max_Score`: Maximum possible points
- `Percentage`: Score as percentage
- `Final_Grade`: Final score that will be passed back to Canvas
- `Grading_Date`: When grading was completed

### Feedback
- `AI_Comments`: Comprehensive overall and individual criterion feedback, will provide each criterion score
- `Final_Comments`: Feedback that will be passed back to Canvas

## Troubleshooting

### Common Issues

**API Key Errors**
- Ensure your OpenAI API key is valid and has sufficient credits
- Check for extra spaces or characters in the key

**File Loading Errors**
- Verify file formats are supported
- Ensure files are not corrupted or password-protected
- Check file permissions

**Grading Errors**
- Verify rubric JSON syntax is valid (or tell the application to download the assignment rubric from Canvas)
- Ensure papers contain sufficient text content
- Check internet connection for API calls 

### Log Files
Check `grading_log.txt` for detailed error messages and processing information.

## Best Practices

### For Better Grading Results:
1. **Clear Rubrics**: Write detailed, specific rubric criteria
2. **Instructor Configuration**: Create an instructor configuration file that closely matches your style, beliefs, and philosophy; then test grade with the configuration to ensure grading validity
3. **Quality Papers**: Ensure student papers are well-formatted and readable (recommend .docx for papers/reports and tabular formats for data)
4. **Consistent Naming**: Use consistent filename conventions for students
5. **Review Results**: Always review AI-generated grades before finalizing
6. **Backup Data**: Keep backups of original papers and rubrics

### Cost Management:
- Use gpt mini models for (much) lower costs (may impact quality, but this is usually imperceptable)
- Have students submit .docx (Microsoft Word) files for papers/reports and tabular formats (.xlsx, .csv) for data
- Be targeted in course material uploads (e.g., relevant chapters instead of the full textbook)
- Set a reasonable budget

## Support and Contribution

### Getting Help
1. Check the troubleshooting section
2. Review log files for error details
3. Verify all requirements are met

### Contributing
This system can be extended with:
- Additional file format support
- Advanced analytics and reporting
- Integration with learning management systems
- Custom AI model fine-tuning

## Feature Details ✨

### **Canvas Rubric Integration** 📋
- **Automatic Download**: Fetch grading rubrics directly from Canvas assignments
- **Seamless Integration**: No need to manually create rubric files
- **Choice of Sources**: Use Canvas rubrics OR local rubric files
- **Backup Storage**: Downloaded rubrics saved locally for reference

### **Instructor Personality Configuration** 🎓
- **Custom Grading Style**: Configure ChatGPT to match your teaching personality
- **Multiple Personalities**: Choose from pre-configured instructor styles:
  - **Professor Smith**: Constructive and balanced approach
  - **Dr. Johnson**: Rigorous and standards-focused approach  
  - **Professor Garcia**: Encouraging and growth-focused approach
- **Custom Configurations**: Create your own instructor personality files
- **Course Context**: Include course level, type, and learning objectives
- **Flexible Grading**: Adjust tone, feedback style, and grading philosophy

### **Privacy Protection** 🔒
- **Student Name Anonymization**: All student names are automatically converted to anonymous IDs (Student_001, Student_002, etc.) before sending to ChatGPT
- **Secure Processing**: Only anonymized content is processed by AI - real names never leave your computer
- **Name Restoration**: Real names are securely restored for grading review and final grade upload to Canvas
- **Privacy Compliance**: Meets educational privacy requirements and best practices

## Instructor Configuration Files

The system includes three pre-configured instructor personalities:

### **Professor Smith (Balanced, Default)**
```json
"grading_philosophy": "constructive and encouraging"
"personality_traits": ["supportive", "detailed", "fair", "encouraging"]
"tone": "professional but warm"
```

### **Dr. Johnson (Rigorous)**  
```json
"grading_philosophy": "rigorous and standards-focused"
"personality_traits": ["precise", "thorough", "high-standards", "analytical"]
"tone": "professional and direct"
```

### **Professor Garcia (Encouraging)**
```json
"grading_philosophy": "encouraging and growth-focused"  
"personality_traits": ["enthusiastic", "encouraging", "patient", "inspiring"]
"tone": "warm and encouraging"
```

**Create Your Own**: Copy and modify any configuration file to match your teaching style!

**NEW**: Or use the new instructor configuration GUI builder to create your own configuration!

### Assignment Folder Structure
```
Assignment_Name_20250128_143022/
├── INSTRUCTIONS.txt              # Detailed instructions
├── submissions/                  # Student papers (anonymized names)
│   ├── Student_001_12345/
│   ├── Student_002_12346/
│   └── ...
├── results/
│   ├── Assignment_Name_REVIEW.xlsx  # Editable grades/comments
│   └── upload_report.txt         # Upload confirmation
├── student_mapping.json          # Secure name mapping
├── canvas_rubric.json           # Downloaded Canvas rubric (if used)
├── rubric_used.json             # Copy of local rubric (if used)
├── instructor_config_used.json  # Copy of instructor config (if used)
└── assignment_metadata.json     # Canvas details
``` 

## License and Disclaimer

This tool is provided for educational purposes. Always review AI-generated grades before sharing with students. The quality of grading depends on:
- Clarity of rubric criteria
- Quality of student papers
- Appropriateness of AI model for your specific needs

Remember that AI grading should supplement, not replace, human judgment in educational assessment.

**Canvas Integration**: This tool uses the Canvas LMS API in compliance with Canvas terms of service. Users are responsible for ensuring proper authorization and compliance with their institution's policies.

## Version History

- **v1.0**: Initial release with core grading functionality
- GUI interface, multiple file format support, Excel/CSV export

---

**Happy Grading! 🎓**

--- 

# Development Roadmap

## Currently in Development
- DuckTest: Uses AI to intelligently generate exams, quizzes, and queston banks, then automatically pushes the products to your LMS once reviewed for accuracy
- DuckBuild: Takes a syllabus as input and uses AI to automatically build your course shell within your LMS in accordance with your syllabus and course schedule
- Windows executable with compiled C++ binaries to elminate the need for any end-user knowledge of python

## Long-Term Development Goals
- Selectable integration with multiple learning management systems such as Blackboard and Google Classroom; just toggle to your LMS, input the relevant API credentials, and get to work!
- MacOS executable version