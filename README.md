# knee_xray_analysis_to_pdf.py

## Description
A Flyte workflow that analyzes knee X-ray images using OpenAI's o3 (GPT-5.2 thinking) vision model to identify potential issues and abnormalities. The workflow accepts individual X-ray image files, processes each image with preprocessing (format conversion and resizing), performs radiological analysis using base64-encoded images, and generates an HTML report with embedded images and analysis results.

## Goal
Automate the preliminary analysis of knee X-ray images using AI-powered vision capabilities to assist in identifying conditions such as arthritis, fractures, bone spurs, and joint space narrowing, with results formatted as a professional HTML report.

## Technical Details
- **Language:** Python
- **Entry File:** main.py
- **Created:** 2026-01-26T21:30:55.147Z
- **Orchestration:** Flyte workflows and tasks
- **AI Model:** OpenAI o3 (GPT-5.2 thinking) vision API with base64 image encoding
- **Container Image:** Custom ImageSpec with openai and pillow packages
- **Registry:** ghcr.io/unionai-oss

### Workflow Components
1. **analyze_single_xray task** - Analyzes a single knee X-ray image using o3 vision:
   - Accepts a FlyteFile image and a patient_id string parameter
   - Converts images to JPEG format for API compatibility using PIL
   - Handles RGBA and P mode images by converting to RGB
   - Resizes large images (max 2048px on longest side) for efficiency using LANCZOS resampling
   - Encodes images as base64 for API transmission
   - Saves to BytesIO buffer as JPEG with 95% quality
   - Uses base64 data URL format with "image_url" content type and "high" detail setting
   - Retrieves OpenAI API key from Flyte secrets
   - Uses max_completion_tokens of 2000 for analysis responses (o3 model parameter)
   - No system message (o3 model requirement) - prompt included in user message instructs the model to act as an expert radiologist and return plain text only without asterisks, markdown, or special formatting
   - User prompt requests structured analysis: IMAGE QUALITY, ANATOMICAL STRUCTURES, FINDINGS, SEVERITY, and RECOMMENDATIONS
   - Returns a dictionary containing filename, patient_id, analysis text, and base64-encoded image data

2. **generate_html_report task** - Generates a styled HTML report:
   - Accepts a list of analysis dictionaries from analyze_single_xray tasks
   - Creates a professional HTML document with inline CSS styling
   - Features gradient header (purple gradient from #667eea to #764ba2)
   - Card-based layout with white background, rounded corners (10px border-radius)
   - Card header uses #4a5568 background color
   - Card content uses flexbox layout with flex-wrap for responsive design
   - Image section (dark #1a1a2e background) and analysis section side by side with min-width of 300px each
   - Image section displays embedded base64 images with max-height of 500px and 5px border-radius
   - Analysis section uses pre-wrap whitespace for formatted text display
   - Body uses #f5f5f5 background with max-width of 1200px centered layout and 20px padding
   - Box shadow on cards (0 2px 10px rgba(0,0,0,0.1)) for depth effect
   - Includes disclaimer section with warning-styled formatting (#fff3cd background, #ffc107 border, 10px border-radius)
   - Displays generation timestamp (YYYY-MM-DD HH:MM format) and total image count in header
   - Returns the report as a FlyteFile

## Files
- `main.py` - Main workflow entry point with Flyte tasks and workflow definitions
- `README.md` - This file

## Change Log
| Date | Changes |
|------|---------|
| 2026-01-26 | Initial workflow creation |
| 2026-01-26 | Implemented X-ray analysis with GPT-4o vision and PDF report generation |
| 2026-01-26 | Added patient_id parameter to analyze_xray task for patient tracking |
| 2026-01-26 | Added find_xray_images task for automatic image discovery from workspace directories |
| 2026-01-26 | Added analyze_all_xrays task for batch processing multiple images sequentially |
| 2026-01-26 | Refactored to simplified two-task architecture: analyze_xrays (accepts List[FlyteFile]) and generate_pdf_report; removed find_xray_images and separate analyze tasks |
| 2026-01-26 | Added sanitize_text helper function to handle Unicode character encoding for PDF compatibility |
| 2026-01-26 | Replaced PDF output with HTML report generation; added image preprocessing (JPEG conversion, resizing); added retry logic for failed vision API responses; embedded base64 images in output report |
| 2026-01-26 | Updated prompt to request plain text without markdown formatting; added regex-based cleanup to remove remaining markdown (bold/italic) from analysis responses |
| 2026-01-26 | Simplified to single analyze_xrays task; removed generate_pdf_report task; updated prompt format to use structured sections with explicit formatting instructions |
| 2026-01-26 | Switched from base64 image_url to OpenAI file upload API; images now uploaded via client.files.create() and referenced by file_id in vision requests |
| 2026-01-26 | Reverted to base64 image_url approach; restored two-task architecture with analyze_xrays and generate_html_report; simplified prompt to single-line format |
| 2026-01-26 | Upgraded from GPT-4o to o3 (GPT-5.2 thinking) model; changed from max_tokens to max_completion_tokens (2000); removed system message per o3 requirements |
| 2026-01-26 | Updated main workflow code with refined HTML styling and layout details |
| 2026-01-26 | Added disclaimer section to HTML report with warning-styled formatting |
| 2026-01-26 | Code cleanup and documentation update |
| 2026-01-26 | Refactored to three-task architecture: added find_images_in_dir task accepting FlyteDirectory; analyze_xrays now accepts List[str] image paths instead of List[FlyteFile]; simplified HTML report styling |
| 2026-01-26 | Updated main workflow code with current implementation |
| 2026-01-26 | Refactored to analyze_single_xray task accepting individual FlyteFile; removed find_images_in_dir and batch analyze_xrays tasks; enhanced HTML report styling with card layout, image/analysis side-by-side display |
| 2026-01-26 | Updated HTML report with responsive flex-wrap layout, refined card styling with box shadows and border-radius details |
| 2026-01-26 | Code cleanup and synchronization with current implementation |
| 2026-01-26 | Updated main workflow code |