from flytekit import task, workflow, current_context, ImageSpec, dynamic
from flytekit.types.file import FlyteFile
from typing import List
import os

image_spec = ImageSpec(
    name="knee-xray-analyzer",
    packages=[
        "openai",
        "pillow",
    ],
    registry="ghcr.io/unionai-oss",
)


@task(container_image=image_spec)
def analyze_single_xray(image_file: FlyteFile, patient_id: str) -> dict:
    """Analyze a single knee X-ray using OpenAI's vision API."""
    import base64
    from openai import OpenAI
    from PIL import Image
    import io
    
    api_key = current_context().secrets.get("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    
    print(f"Analyzing: {os.path.basename(image_file.path)}")
    
    # Convert image to JPEG format
    img = Image.open(image_file.path)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    
    # Resize if too large
    max_size = 2048
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=95)
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    
    # Using o3 (GPT-5.2 thinking) - no system message, uses max_completion_tokens
    response = client.chat.completions.create(
        model="o3",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """You are an expert radiologist. Analyze this knee X-ray. Provide: IMAGE QUALITY, ANATOMICAL STRUCTURES, FINDINGS, SEVERITY, and RECOMMENDATIONS. Use plain text only, no markdown or asterisks."""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ],
        max_completion_tokens=2000
    )
    
    return {
        "filename": os.path.basename(image_file.path),
        "patient_id": patient_id,
        "analysis": response.choices[0].message.content,
        "image_base64": image_base64
    }


@task(container_image=image_spec)
def generate_html_report(analyses: List[dict]) -> FlyteFile:
    """Generate an HTML report with inline images and analyses."""
    from datetime import datetime
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Knee X-Ray Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        .header {{ text-align: center; background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
        .card {{ background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 30px; overflow: hidden; }}
        .card-header {{ background: #4a5568; color: white; padding: 15px 20px; }}
        .card-content {{ display: flex; flex-wrap: wrap; }}
        .image-section {{ flex: 1; min-width: 300px; padding: 20px; background: #1a1a2e; text-align: center; }}
        .image-section img {{ max-width: 100%; max-height: 500px; border-radius: 5px; }}
        .analysis-section {{ flex: 1; min-width: 300px; padding: 20px; white-space: pre-wrap; }}
        .disclaimer {{ background: #fff3cd; border: 1px solid #ffc107; border-radius: 10px; padding: 20px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Knee X-Ray Analysis Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        <p>Total Images: {len(analyses)}</p>
    </div>
"""
    
    for i, analysis in enumerate(analyses, 1):
        html_content += f"""
    <div class="card">
        <div class="card-header"><h2>Image {i}: {analysis['filename']}</h2><small>Patient: {analysis['patient_id']}</small></div>
        <div class="card-content">
            <div class="image-section"><img src="data:image/jpeg;base64,{analysis['image_base64']}" alt="{analysis['filename']}"></div>
            <div class="analysis-section">{analysis['analysis']}</div>
        </div>
    </div>
"""
    
    html_content += """
    <div class="disclaimer">
        <h3>Disclaimer</h3>
        <p>This AI-generated analysis is for informational purposes only and should NOT replace professional medical diagnosis.</p>
    </div>
</body>
</html>
"""
    
    output_path = "/tmp/knee_xray_report.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return FlyteFile(output_path)


@dynamic(container_image=image_spec)
def analyze_all_xrays(image_files: List[FlyteFile], patient_id: str) -> List[dict]:
    """Dynamically analyze any number of X-ray images in parallel."""
    analyses = []
    for image_file in image_files:
        analysis = analyze_single_xray(image_file=image_file, patient_id=patient_id)
        analyses.append(analysis)
    return analyses


@workflow
def knee_xray_analysis(
    knee_images: List[FlyteFile],
    patient_id: str = "abcd"
) -> FlyteFile:
    """Analyze any number of knee X-ray images and generate an HTML report."""
    # Analyze all images (runs in parallel via @dynamic!)
    analyses = analyze_all_xrays(image_files=knee_images, patient_id=patient_id)
    
    # Generate consolidated report
    return generate_html_report(analyses=analyses)


if __name__ == "__main__":
    result = knee_xray_analysis(
        knee_images=[
            FlyteFile("knee1.png"),
            FlyteFile("knee2.png"),
            FlyteFile("knee3.png"),
        ],
        patient_id="abcd"
    )
    print(f"Report: {result}")