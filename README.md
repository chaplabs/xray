# knee_xray_analysis_to_pdf.py

## Description
A Flyte workflow that analyzes knee X-ray images using OpenAI's GPT-4o vision model to identify potential issues and abnormalities. The workflow accepts a list of X-ray image files with patient ID tracking, processes images with preprocessing (format conversion and resizing), performs radiological analysis using base64-encoded images, and generates an HTML report with embedded images and analysis results.

## Goal
Automate the preliminary analysis of knee X-ray images using AI-powered vision capabilities to assist in identifying conditions such as arthritis, fractures, bone spurs, and joint space narrowing, with results formatted as a professional HTML report.

## Technical Details
- **Language:** Python
- **Entry File:** main.py
- **Created:** 2026-01-26T21:30:55.147Z
- **Orchestration:** Flyte workflows and tasks
- **AI Model:** OpenAI GPT-4o vision API with base64 image encoding
- **Container Image:** Custom ImageSpec with openai and pillow packages
- **Registry:** ghcr.io/unionai-oss

### Workflow Components
1. **analyze_xrays task** - Analyzes all knee X-ray images using GPT-4o vision:
   - Accepts a list of FlyteFile image files and a patient_id string parameter
   - Processes images sequentially within a single task
   - Converts images to JPEG format for API compatibility using PIL
   - Handles RGBA and P mode images by converting to RGB
   - Resizes large images (max 2048px on longest side) for efficiency using LANCZOS resampling
   - Encodes images as base64 for API transmission
   - Saves to BytesIO buffer as JPEG with 95% quality
   - Uses base64 data URL format with "image_url" content type and "high" detail setting
   - Retrieves OpenAI API key from Flyte secrets
   - Uses max_tokens of 1000 for analysis responses
   - System prompt instructs the model to act as an expert radiologist and return plain text only without asterisks, markdown, or special formatting
   - User prompt requests structured analysis: IMAGE QUALITY, ANATOMICAL STRUCTURES, FINDINGS, SEVERITY, and RECOMMENDATIONS
   - Returns list of dictionaries containing filename, patient_id, analysis text, and base64-encoded image data

2. **generate_html_report task** - Generates a styled HTML report:
   - Accepts the list of analysis dictionaries from analyze_xrays
   - Creates a professional HTML document with inline CSS styling
   - Features gradient header, card-based layout with shadows and rounded corners
   - Displays images alongside their analysis in a responsive flex layout
   - Dark-themed image section with light analysis section
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