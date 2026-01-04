import json
import os
import time
from datetime import datetime
from src.uploader import get_authenticated_service, upload_video

QUEUE_FILE = "outputs/queue.json"

def get_queue():
    if not os.path.exists(QUEUE_FILE):
        return []
    with open(QUEUE_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return []

def save_queue(queue):
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=4)

def add_to_queue(video_path, title, description, schedule_time):
    """
    schedule_time should be a datetime object or ISO string.
    """
    if isinstance(schedule_time, datetime):
        schedule_time = schedule_time.isoformat()
    
    queue = get_queue()
    queue.append({
        "video_path": video_path,
        "title": title,
        "description": description,
        "schedule_time": schedule_time,
        "status": "queued"
    })
    save_queue(queue)

def process_queue():
    """
    Checks the queue and uploads videos that are past their schedule time.
    """
    queue = get_queue()
    now = datetime.now()
    updated = False
    
    for item in queue:
        if item["status"] == "queued":
            sched_time = datetime.fromisoformat(item["schedule_time"])
            if now >= sched_time:
                print(f"Uploading scheduled video: {item['title']}")
                try:
                    youtube = get_authenticated_service()
                    upload_video(youtube, item["video_path"], item["title"], item["description"])
                    item["status"] = "uploaded"
                    updated = True
                except Exception as e:
                    print(f"Error uploading {item['title']}: {e}")
                    item["status"] = f"failed: {str(e)}"
                    updated = True
    
    if updated:
        save_queue(queue)

if __name__ == "__main__":
    # Test
    process_queue()
