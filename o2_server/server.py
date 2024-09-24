import asyncio
import json
import os
import zipfile
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing_extensions import TypedDict

from o2.models.json_report import JSONReport
from o2_server.optimos_service import OptimosService
from o2_server.types import ProcessingRequest

tags_metadata = [
    {
        "name": "reports",
        "description": "Operations with reports.",
    },
    {
        "name": "optimization",
        "description": "Operations with optimization.",
    },
]

app = FastAPI(
    title="Process Optimization Tool API",
    version="1.0",
    description="A simple API for process optimization",
    tags_metadata=tags_metadata,
    separate_input_output_schemas=False,
)

origins = [
    "http://pix-w1.cloud.ut.ee",
    "https://pix-w1.cloud.ut.ee",
    "http://localhost",
    "http://localhost:1234",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory for storing temporary JSON files
TMP_DIR = "tmp"
os.makedirs(TMP_DIR, exist_ok=True)

# File for persisting the hash to path and timestamp mapping
MAPPING_FILE = "mapping.json"

# Lock for making file operations thread-safe
file_lock = Lock()


class OptimizationResponse(TypedDict):
    message: str
    json_url: str
    id: str


class CancelResponse(TypedDict):
    message: str


services: dict[str, OptimosService] = {}

executor = ThreadPoolExecutor(max_workers=5)


@app.post("/start_optimization", status_code=202, tags=["optimization"])
async def start_optimization(data: "ProcessingRequest") -> OptimizationResponse:
    """Start an optimization process.

    Return a JSON file containing the optimization results.
    """
    try:
        optimos_service = OptimosService()
        save_mapping(optimos_service.id, optimos_service.output_path)
        services[optimos_service.id] = optimos_service

        executor.submit(asyncio.run, optimos_service.process(data))

        # Wait a bit for the optimization to start
        await asyncio.sleep(1)

        json_url = f"/get_json/{optimos_service.id}"
        return {
            "message": "Optimization started",
            "json_url": json_url,
            "id": optimos_service.id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get(
    "/get_report_zip/{id}",
    responses={
        200: {"description": "Report zip file retrieved"},
        404: {"description": "File not found"},
    },
    tags=["reports"],
)
async def get_report_zip_file(
    id: str = Path(..., description="The identifier of the zip file"),
) -> FileResponse:
    """Return a JSON file from the file system based on the given id."""
    zip = get_mapping(id)
    if zip is None:
        raise HTTPException(status_code=404, detail="File not found")

    if not os.path.exists(zip):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=zip, media_type="application/zip")


@app.get(
    "/get_report/{id}",
    responses={
        200: {"description": "Report zip file retrieved"},
        404: {"description": "File not found"},
    },
    tags=["reports"],
)
async def get_report_file(
    id: str = Path(..., description="The identifier of the zip file"),
) -> JSONReport:
    """Return a JSON file from the file system based on the given id."""
    zip = get_mapping(id)
    if zip is None:
        raise HTTPException(status_code=404, detail="File not found")

    if not os.path.exists(zip):
        raise HTTPException(status_code=404, detail="File not found")

    # Unzip into memory, return first (only) file content
    with zipfile.ZipFile(zip) as z, z.open(z.namelist()[0]) as f:
        report = JSONReport.from_json(f.read())
        if not isinstance(report, JSONReport):
            raise HTTPException(status_code=500, detail="Invalid JSON file")
        return report


@app.post("/cancel_optimization/{id}", status_code=202, tags=["optimization"])
async def cancel_optimization(id: str) -> CancelResponse:
    """Cancel an ongoing optimization process."""
    if id not in services:
        raise HTTPException(status_code=404, detail="Optimization not found")

    services[id].cancelled = True

    return {"message": "Optimization cancelled"}


@app.get("/status/{id}", tags=["optimization"])
async def get_status(id: str) -> str:
    """Return the status of the optimization process."""
    if id not in services:
        mapping = get_mapping(id)
        if mapping is None:
            raise HTTPException(status_code=404, detail="Optimization not found")
        else:
            return "completed"

    if services[id].running:
        return "running"
    elif services[id].cancelled:
        return "cancelled"
    return "completed"


def save_mapping(id: str, path: str) -> None:
    """Save the mappings to a file with thread safety."""
    with file_lock, open(MAPPING_FILE, "w+") as f:
        content = f.read()

        # Check if the content is empty or only contains whitespace
        current = json.load(f) if content.strip() else {}
        current[id] = path
        f.seek(0)
        json.dump(current, f)


def get_mapping(id: str) -> str:
    """Retrieve the path from the mappings."""
    with file_lock, open(MAPPING_FILE) as f:
        current = json.load(f)
        return current.get(id, None)


def start() -> None:
    """Start the server in production mode."""
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
