import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

load_dotenv()

# The SCOPES for the YouTube Data API
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    """
    Handles OAuth2 flow for YouTube.
    Requires 'client_secrets.json' in the root directory.
    """
    client_secrets_file = "client_secrets.json"
    
    if not os.path.exists(client_secrets_file):
        raise FileNotFoundError("client_secrets.json not found. Please download it from Google Cloud Console.")

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, SCOPES)
    credentials = flow.run_local_server(port=0)
    
    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

def upload_video(youtube, file_path, title, description, category_id="27", tags=None, privacy_status="private"):
    """
    Uploads a video to YouTube.
    category_id "27" is Education, "22" is People & Blogs.
    """
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy_status
        }
    }

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
    )

    response = None
    while response is None:
        status, response = insert_request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")
            
    return response

if __name__ == "__main__":
    # Example usage (commented out to avoid accidental execution)
    # youtube = get_authenticated_service()
    # upload_video(youtube, "outputs/videos/test.mp4", "Test Video", "This is a test.")
    pass
