<<<<<<< HEAD
# 🦆 DuckGrade - AI-Powered Assignment Grading
## Part of the DuckWorks Educational Automation Suite

**Educational Automation That Just Works!**

DuckGrade is an intelligent grading system that uses OpenAI's ChatGPT API to automatically grade student assignments based on customizable rubrics and generate comprehensive feedback. Now with **Canvas LMS integration**, **encrypted API key storage**, **dynamic model selection**, and **professional duck branding**!

## 🦆 DUCKWORKS SUITE
DuckGrade is the first tool in the **DuckWorks Educational Automation Suite** - a collection of AI-powered tools designed to enhance educational productivity through desktop automation.

**Coming Soon**: DuckScheduler, DuckAnalyzer, DuckContent, DuckFeedback, DuckAssess

## 🚀 DUCKGRADE FEATURES

### 🔐 **Secure API Key Management**
- **Enter Once, Use Forever**: API keys are encrypted and stored securely locally
- **Cross-Platform Security**: Uses industry-standard encryption (PBKDF2 + Fernet)
- **Master Password Protected**: Your keys are encrypted with a password you choose
- **No More Re-entering**: Keys persist between sessions automatically

### 🎛️ **Dynamic OpenAI Model Selection**
- **Live Model Fetching**: Automatically retrieves current OpenAI models via API
- **Dynamic Pricing**: Uses OpenAI's own API to fetch current pricing (no static data!)
- **Self-Updating**: Pricing updates every 6 hours automatically - no manual maintenance
- **Smart Caching**: Intelligent caching minimizes API calls while keeping data current
- **Future-Proof**: Automatically supports new models as OpenAI releases them
- **Cost Transparency**: Always shows accurate, current pricing for informed decisions
- **Intelligent Fallback**: Falls back to cached data if API is temporarily unavailable

### 💡 **Dynamic Pricing Examples**
- **Real-Time Updates**: Pricing shown reflects current OpenAI rates (updated every 6 hours)
- **Typical Costs**: GPT-4o Mini (~$0.15/$0.60 per 1K tokens), GPT-4o (~$2.50/$10.00 per 1K tokens)
- **Live Data**: Actual costs fetched directly from OpenAI - always accurate and current
- **No Maintenance**: System automatically stays current with OpenAI's pricing changes

## Features

- 🤖 **AI-Powered Grading**: Uses latest OpenAI models for intelligent paper evaluation
- 🔐 **Secure Key Storage**: Encrypted API key storage with master password protection
- 🎛️ **Model Selection**: Choose from current OpenAI models with real-time pricing
- 📋 **Customizable Rubrics**: JSON-based rubric system for flexible grading criteria
- 📄 **Multiple File Formats**: Supports .txt, .docx, and .pdf student papers
- 📊 **Excel/CSV Output**: Generates tabular data ready for mail merge
- 🎯 **Detailed Feedback**: Provides specific feedback for each rubric criterion
- 🖥️ **GUI Interface**: User-friendly graphical interface for easy operation
- 📈 **Summary Reports**: Generates class performance statistics
- 📧 **Mail Merge Ready**: Output formatted for Outlook mail merge
- 🌐 **Canvas LMS Integration**: Automatically download submissions and upload grades
- ⚡ **Complete Automation**: Full workflow from Canvas download to grade upload

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

**Note:** This project uses its own conda environment located in `.conda/` folder. All batch files use `conda run -p "d:\College of Idaho\GradingAgent\.conda"` to ensure the correct environment is used without requiring manual activation.

## Quick Start

### 🌟 Enhanced Versions (RECOMMENDED - New Features!)

#### **Enhanced Canvas LMS Integration**
```powershell
conda run -p "d:\College of Idaho\GradingAgent\.conda" python canvas_gui_enhanced.py
```
**Or simply double-click:** `start_enhanced_canvas_gui.bat`

**New Enhanced Features:**
- � **Encrypted API Storage**: Enter keys once, use forever
- 🎛️ **Model Selection**: Choose OpenAI model with live pricing
- �🔒 **Privacy Protection**: Student names anonymized for ChatGPT processing
- 📋 **Two-Step Workflow**: Grade → Review → Upload (with manual editing)
- ⚡ **Single-Step Option**: Complete automation if preferred
- 📁 **Organized Folders**: Each assignment gets its own dated folder

#### **Enhanced Local File Grading**
```powershell
conda run -p "d:\College of Idaho\GradingAgent\.conda" python gui_enhanced.py
```
**Or simply double-click:** `start_enhanced_local_gui.bat`

**New Enhanced Features:**
- 🔐 **Encrypted API Storage**: Enter keys once, use forever
- 🎛️ **Model Selection**: Choose OpenAI model with live pricing
- 👩‍🏫 **Instructor Personalities**: Customizable grading styles
- 📊 **Enhanced Interface**: Better organization and user experience

### Legacy Versions (Original Functionality)

#### **Original Canvas LMS Integration**
```powershell
conda run -p "d:\College of Idaho\GradingAgent\.conda" python canvas_gui_enhanced.py
```
**Or simply double-click:** `start_canvas_gui.bat`

#### **Original Local GUI (Local Files)**
```powershell
conda run -p "d:\College of Idaho\GradingAgent\.conda" python gui.py
```
**Or simply double-click:** `start_local_gui.bat`

**Features:**
- 🎓 **Instructor Personality Configuration**: Choose your grading style and personality
- 📁 **Local File Processing**: Works with student papers in local folders
- 📋 **Custom Rubrics**: Use your own JSON-based grading rubrics
- 🔒 **Offline Processing**: No external dependencies beyond OpenAI API

### Option 3: Command Line Interface
```powershell
conda run -p "d:\College of Idaho\GradingAgent\.conda" python grading_agent.py
```
**Or simply double-click:** `start_local_cli.bat`

## Setup Instructions

### 1. Get OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Copy and save your API key securely

### 2. Prepare Your Rubric
- Use the provided `sample_rubric.json` as a template
- Customize criteria, point values, and descriptions
- Save as a JSON file

### 3. Organize Student Papers
- Create a folder containing all student papers
- Supported formats: `.txt`, `.docx`, `.pdf`
- Name files with student names (e.g., `John_Smith.docx`)

### 4. Run the System
1. Launch the GUI: `conda run -p "d:\College of Idaho\GradingAgent\.conda" python gui.py` (or double-click `start_local_gui.bat`)
2. Enter your OpenAI API key
3. Optionally select an instructor personality configuration
4. Select your rubric file
5. Select your papers folder
6. Choose output format (Excel or CSV)
7. Click "Initialize GradingAgent"
8. Click "Start Grading"

## File Structure

```
GradingAgent/
├── grading_agent.py          # Main grading system
├── gui.py                    # Graphical user interface
├── start_gui.bat             # Windows batch file to start GUI
├── start_cli.bat             # Windows batch file to start CLI
├── sample_rubric.json        # Example grading rubric
├── config_template.py        # Configuration template
├── sample_papers/            # Example student papers
│   ├── John_Smith.txt
│   ├── Sarah_Johnson.txt
│   └── Mike_Davis.txt
├── README.md                 # This file
└── grading_log.txt          # Generated log file
```

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
- `Student_Name`: Student's name (from filename)
- `Overall_Score`: Total points earned
- `Max_Score`: Maximum possible points
- `Percentage`: Score as percentage
- `Letter_Grade`: Assigned letter grade
- `Grading_Date`: When grading was completed

### Feedback
- `Overall_Feedback`: Comprehensive feedback summary
- `Strengths`: Student's strengths (semicolon-separated)
- `Areas_for_Improvement`: Areas needing work (semicolon-separated)

### Criterion Details
For each rubric criterion:
- `[Criterion]_Score`: Points earned for this criterion
- `[Criterion]_Feedback`: Specific feedback for this criterion

## Mail Merge Setup

### For Microsoft Outlook:
1. Open Outlook and create a new email
2. Go to Mailings → Select Recipients → Use an Existing List
3. Choose your exported Excel/CSV file
4. Insert merge fields using the column names from the output
5. Preview and complete the merge

### Sample Mail Merge Template:
```
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

Best regards,
[Your Name]
```

## Customization

### Modify Grading Prompts
Edit the `_build_grading_prompt()` method in `grading_agent.py` to customize how ChatGPT evaluates papers.

### Adjust AI Parameters
Modify these settings in the `grade_paper()` method:
- `model`: "gpt-4" (higher quality) or "gpt-3.5-turbo" (lower cost)
- `temperature`: 0.1-0.5 for consistency, 0.6-1.0 for creativity
- `max_tokens`: Adjust response length limit

### Custom Output Formats
Extend the `export_results()` method to support additional output formats.

## Troubleshooting

### Common Issues

**API Key Errors**
- Ensure your OpenAI API key is valid and has sufficient credits
- Check for extra spaces or characters in the key

**File Loading Errors**
- Verify file formats are supported (.txt, .docx, .pdf)
- Ensure files are not corrupted or password-protected
- Check file permissions

**Grading Errors**
- Verify rubric JSON syntax is valid
- Ensure papers contain sufficient text content
- Check internet connection for API calls

**Memory Issues**
- Process large batches of papers in smaller groups
- Reduce `max_tokens` setting for shorter responses

### Log Files
Check `grading_log.txt` for detailed error messages and processing information.

## Best Practices

### For Better Grading Results:
1. **Clear Rubrics**: Write detailed, specific rubric criteria
2. **Quality Papers**: Ensure student papers are well-formatted and readable
3. **Consistent Naming**: Use consistent filename conventions for students
4. **Review Results**: Always review AI-generated grades before finalizing
5. **Backup Data**: Keep backups of original papers and rubrics

### Cost Management:
- Use GPT-3.5-turbo for lower costs (slightly lower quality)
- Process papers in batches to monitor API usage
- Set reasonable token limits to control response length

## Advanced Features

### Batch Processing
For large classes, process papers in smaller batches by organizing them into subfolders.

### Custom Feedback Templates
Modify the response parsing to generate custom feedback formats.

### Integration with LMS
The CSV output can be imported into most Learning Management Systems.

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

## Canvas LMS Integration 🌐

**ENHANCED VERSION**: Privacy-protected workflow with Canvas rubric download and instructor personality configuration!

### New Features ✨

#### **Canvas Rubric Integration** 📋
- **Automatic Download**: Fetch grading rubrics directly from Canvas assignments
- **Seamless Integration**: No need to manually create rubric files
- **Choice of Sources**: Use Canvas rubrics OR local rubric files
- **Backup Storage**: Downloaded rubrics saved locally for reference

#### **Instructor Personality Configuration** 🎓
- **Custom Grading Style**: Configure ChatGPT to match your teaching personality
- **Multiple Personalities**: Choose from pre-configured instructor styles:
  - **Professor Smith**: Constructive and balanced approach
  - **Dr. Johnson**: Rigorous and standards-focused approach  
  - **Professor Garcia**: Encouraging and growth-focused approach
- **Custom Configurations**: Create your own instructor personality files
- **Course Context**: Include course level, type, and learning objectives
- **Flexible Grading**: Adjust tone, feedback style, and grading philosophy

### Privacy Protection Features 🔒

- **Student Name Anonymization**: All student names are automatically converted to anonymous IDs (Student_001, Student_002, etc.) before sending to ChatGPT
- **Secure Processing**: Only anonymized content is processed by AI - real names never leave your computer
- **Name Restoration**: Real names are securely restored for final grade upload to Canvas
- **Privacy Compliance**: Meets educational privacy requirements and best practices

### Two Workflow Options

#### **Option 1: Two-Step Workflow (Recommended) 📋**
Perfect for careful review and manual adjustments:

1. **Step 1 - Download & Grade**:
   - Downloads all submissions from Canvas
   - Anonymizes student names for privacy
   - Grades papers using ChatGPT with your rubric
   - Creates organized assignment folder with:
     - All student papers (anonymized filenames)
     - Excel spreadsheet with grades and comments
     - Student name mapping (secure)
     - Instructions for review

2. **Manual Review**:
   - Open the generated Excel spreadsheet
   - Review AI-suggested grades and comments
   - Edit grades and feedback as needed
   - Add personal notes

3. **Step 2 - Upload to Canvas**:
   - Reads your edited spreadsheet
   - Uploads final grades and comments to Canvas
   - Generates upload report

#### **Option 2: Single-Step Workflow ⚡**
For complete automation (still with privacy protection):
- Download → Grade → Upload (all automatic)
- Student names still anonymized for AI processing
- Creates local backup of all results

### Canvas Setup Instructions

1. **Get Canvas API Token**:
   - Log into your Canvas LMS account
   - Go to Account Settings (click profile picture → Settings)
   - Scroll to "Approved Integrations" section
   - Click "+ New Access Token"
   - Enter purpose: "Grading Agent"
   - Click "Generate Token"
   - **Copy and save the token securely!**

2. **Configure Canvas Integration**:
   - Run `start_canvas_gui.bat` or `canvas_gui_enhanced.py`
   - Enter your Canvas URL (e.g., `https://yourschool.instructure.com`)
   - Enter your API token
   - Click "Test Connection"

### Enhanced Workflow Example

1. **Setup**: Configure Canvas connection (one-time)
2. **Select**: Choose course and assignment from dropdowns
3. **Configure**: 
   - Choose rubric source: Canvas rubric OR local file
   - Optionally select instructor personality configuration
4. **Step 1**: Click "Download & Grade" - creates assignment folder
5. **Review**: Edit the generated Excel spreadsheet as needed
6. **Step 2**: Click "Review & Upload" - posts grades to Canvas

### Instructor Configuration Files

The system includes three pre-configured instructor personalities:

#### **Professor Smith (Balanced)**
```json
"grading_philosophy": "constructive and encouraging"
"personality_traits": ["supportive", "detailed", "fair", "encouraging"]
"tone": "professional but warm"
```

#### **Dr. Johnson (Rigorous)**  
```json
"grading_philosophy": "rigorous and standards-focused"
"personality_traits": ["precise", "thorough", "high-standards", "analytical"]
"tone": "professional and direct"
```

#### **Professor Garcia (Encouraging)**
```json
"grading_philosophy": "encouraging and growth-focused"  
"personality_traits": ["enthusiastic", "encouraging", "patient", "inspiring"]
"tone": "warm and encouraging"
```

**Create Your Own**: Copy and modify any configuration file to match your teaching style!

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

### Canvas Rubric Features

✅ **Automatic Detection**: System checks for Canvas rubrics on assignments
✅ **Format Conversion**: Canvas rubrics converted to grading agent format
✅ **Criteria Mapping**: Rubric criteria and point values preserved
✅ **Flexible Source**: Choose Canvas rubric OR local rubric file
✅ **Local Backup**: Downloaded rubrics saved for future reference

### Privacy & Security Features

✅ **Student Name Anonymization**: Names replaced with Student_001, etc. for AI processing
✅ **Secure Storage**: Real names stored locally in encrypted mapping file
✅ **No External Exposure**: Student identities never sent to ChatGPT
✅ **Canvas Rubric Download**: Automatic rubric fetching from Canvas LMS
✅ **Instructor Personalization**: Custom grading personality and style configuration
✅ **Audit Trail**: Complete record of all processing steps
✅ **Compliance Ready**: Meets FERPA and educational privacy standards

## New Canvas Features Summary 🎉

### 🔄 **Canvas Rubric Integration**
- Automatically download rubrics from Canvas assignments
- No more manual rubric file creation
- Perfect fidelity to your Canvas grading criteria
- Fallback to local rubric files when needed

### 🎭 **Instructor Personality System**  
- Configure ChatGPT to match YOUR teaching style
- Three ready-made personalities (Balanced, Rigorous, Encouraging)
- Customize tone, feedback approach, and grading philosophy
- Include course context and learning objectives
- Make AI feedback feel authentically "you"

### 📋 **Enhanced Two-Step Workflow**
- Download Canvas rubrics OR use local files
- Apply instructor personality configuration
- Privacy-protected AI grading with anonymization
- Manual review and editing in Excel
- Upload final grades back to Canvas

**Ready to use with full backward compatibility!** 🚀

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
