from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from dateutil import parser
import spacy
import re
from geopy.geocoders import Nominatim
from sentinelhub import BBox, CRS, DataCollection, MimeType, SentinelHubRequest, SHConfig, bbox_to_dimensions

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)
logging.captureWarnings(True)

class QueryModel(BaseModel):
    latitude: float
    longitude: float


@app.put("/pipeline")
async def process_pipeline(request_data: PipelineRequestModel):
    name = request_data.name
    data_sources = request_data.data_sources

    # You can process the data_sources as needed here
    results = []

    for source in data_sources:
        source_name = source.source
        query = source.q
        latitude = query.latitude
        longitude = query.longitude

        # Append results for each source to the results list
        results.append({"source": source_name, "latitude": latitude, "longitude": longitude})

    response_data = {"message": "Pipeline processing completed for " + name, "results": results}
    return JSONResponse(content=response_data)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
