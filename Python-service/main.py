from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.concurrency import run_in_threadpool
from contextlib import asynccontextmanager
import logging

from config import settings
from api_client import fetch_student_sync
from report_generator import generate_pdf
from schemas import StudentProfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Python PDF Service starting on port {settings.port}")
    yield
    logger.info("Python PDF Service shutting down")


app = FastAPI(
    title="Student Report Service",
    description="Microservice to generate PDF reports for students by consuming the Node.js backend API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "Student Report Service"}


@app.get(
    "/api/v1/students/{student_id}/report",
    tags=["Reports"],
    summary="Generate PDF report for a student",
    response_description="PDF file download",
)
async def get_student_report(student_id: int):
    """
    Fetches student data from the Node.js backend and generates
    a downloadable PDF report.
    """
    try:
        raw = await run_in_threadpool(fetch_student_sync, student_id)
        student = StudentProfile.from_api(raw)
        pdf_path = await run_in_threadpool(generate_pdf, student)

        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=f"student_report_{student_id}.pdf",
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        import traceback
        logger.error(f"Report generation failed: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)