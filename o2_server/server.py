import json
import os
from threading import Lock
from typing import TypedDict

from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import FileResponse

from o2_server.optimos_service import OptimosService
from o2_server.types import ProcessingRequest

app = FastAPI(
    title="Process Optimization Tool API",
    version="1.0",
    description="A simple API for process optimization",
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


class CancelResponse(TypedDict):
    message: str


@app.post("/start_optimization", status_code=202)
async def start_optimization(data: ProcessingRequest) -> OptimizationResponse:
    """Start an optimization process.

    Return a JSON file containing the optimization results.
    """
    optimos_service = OptimosService()
    save_mapping(optimos_service.id, optimos_service.output_path)

    await optimos_service.process(data)

    json_url = f"/get_json/{optimos_service.id}"
    return {"message": "Optimization started", "json_url": json_url}


@app.get(
    "/get_report/{hash}",
    responses={
        200: {"description": "Report file retrieved"},
        404: {"description": "File not found"},
    },
)
async def get_report_file(
    id: str = Path(..., description="The identifier of the zip file"),
) -> FileResponse:
    """Return a JSON file from the file system based on the given id."""
    zip = get_mapping(id)
    if zip is None:
        raise HTTPException(status_code=404, detail="File not found")

    if not os.path.exists(zip):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=zip, media_type="application/zip")


@app.post("/cancel_optimization")
async def cancel_optimization() -> CancelResponse:
    """Cancel an ongoing optimization process."""
    # Placeholder: Add logic to cancel the optimization
    return {"message": "Optimization canceled"}


def save_mapping(id: str, path: str) -> None:
    """Save the mappings to a file with thread safety."""
    with file_lock, open(MAPPING_FILE, "w+") as f:
        current = json.load(f)
        current[id] = path
        f.seek(0)
        json.dump(current, f)


def get_mapping(id: str) -> str:
    """Retrieve the path from the mappings."""
    with file_lock, open(MAPPING_FILE) as f:
        current = json.load(f)
        return current.get(id, None)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
