from fastapi import APIRouter



router = APIRouter("/camera")


@router.get("/feed")
def get_camera_feed():
    return {"message": "Camera feed"}