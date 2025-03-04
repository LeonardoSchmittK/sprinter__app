import boto3
import os
from django.conf import settings
from .models import Sprint
from dotenv import load_dotenv
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json

load_dotenv()

S3_BUCKET_NAME = "sprinter-app"

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME,
    config=boto3.session.Config(signature_version="s3v4")
)


import logging
import boto3
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Sprint  # Ensure Sprint model is imported

# Initialize S3 client
s3_client = boto3.client("s3")

# Setup logger
logger = logging.getLogger(__name__)

def upload_sprint_file_s3(request, sprint_id):
    """
    Handles file upload to S3 for a specific sprint.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    if "file" not in request.FILES:
        return JsonResponse({"error": "No file provided"}, status=400)

    sprint = get_object_or_404(Sprint, id=sprint_id)
    file = request.FILES["file"]
    s3_key = f"{sprint.s3_folder}/{file.name}"  # Store file inside sprint's S3 folder

    try:
        s3_client.upload_fileobj(
            file,
            settings.AWS_STORAGE_BUCKET_NAME,
            s3_key
        )


        file_url = s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "Key": s3_key
            },
            ExpiresIn=3600  
        )

        return JsonResponse({
            "message": "File uploaded successfully!",
            "file_url": file_url,
            "filename": file.name  
        })

    
    except Exception as e:
        logger.error(f"S3 Upload Error: {e}")  # Log the error
        return JsonResponse({"error": "File upload failed"}, status=500)


def list_sprint_files(sprint_id):
    try:
        sprint = Sprint.objects.get(id=sprint_id)
        s3_folder = sprint.s3_folder  

        if not s3_folder:
            return {"error": "No S3 folder defined for this sprint"}

        if not s3_folder.endswith("/"):
            s3_folder += "/"

        response = s3_client.list_objects_v2(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME, 
            Prefix=s3_folder
        )

        if "Contents" not in response:
            return {"message": "No files found in this folder"}

        files = [
            {
                "filename": obj["Key"].split("/")[-1],  # Extract filename
                "file_url": s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": obj["Key"]},
                    ExpiresIn=3600  # URL valid for 1 hour
                )
            }
            for obj in response["Contents"]
        ]

        return {"files": files}

    except Sprint.DoesNotExist:
        return {"error": "Sprint not found"}
    except Exception as e:
        return {"error": str(e)}

def remove_file_s3(request):
    body = json.loads(request.body)
    sprint_id = body.get('sprint_id')
    file_name = body.get('file_name')
    
    sprint = Sprint.objects.get(id=sprint_id)
    
    s3_folder = sprint.s3_folder
    
    s3_client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                             region_name=settings.AWS_S3_REGION_NAME)
    
    s3_key = f"{s3_folder}/{file_name}"
    
    try:
        s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=s3_key)
        return JsonResponse({'success': 'true', 'message': f'Arquivo {file_name} removido com sucesso.'}, status=200)
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

