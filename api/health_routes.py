from fastapi import APIRouter


router = APIRouter(
    prefix="/health",
    tags=["Health"]
)


# =========================================================
# Health Check Endpoint
# =========================================================
@router.get("/")
async def health_check():

    return {
        "success": True,
        "status": "healthy",
        "service": "InsightHost API",
        "version": "1.0.0"
    }