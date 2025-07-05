"""
FastAPI backend for Powerlifting Meet Scraper
Provides REST API endpoints for meet analysis and data management
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from typing import List, Optional, Dict, Any
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
import pandas as pd

# Import existing modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#Existing modules from my command line powerlifting meet scraper. 
from data_manager import OpenPowerliftingDataManager
from lifter_processor import LifterProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
data_manager: Optional[OpenPowerliftingDataManager] = None
lifter_processor: Optional[LifterProcessor] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    global data_manager, lifter_processor
    
    # Startup
    logger.info("Initializing Powerlifting Scraper API...")
    try:
        data_manager = OpenPowerliftingDataManager()
        data_manager.update_if_needed()
        # Ensure data is loaded into memory
        data_manager.load_data()
        logger.info("Data manager initialized successfully")
        
        lifter_processor = LifterProcessor(data_manager)
        lifter_processor.setup_driver()
        logger.info("Lifter processor initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield # ← Server runs here, accepting requests. Once you are done with the server, it will run the code below. 
    
    # SHUTDOWN: Runs when ANY of the above triggers occur
    if lifter_processor:
        lifter_processor.cleanup()
        logger.info("Cleaned up lifter processor")

# Create FastAPI app
app = FastAPI(
    title="Powerlifting Meet Scraper API",
    description="API for analyzing powerlifting meets using LiftingCast and OpenPowerlifting data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
from pydantic import BaseModel, HttpUrl

class MeetAnalysisRequest(BaseModel):
    meet_url: HttpUrl
    max_workers: Optional[int] = 3

class LifterInfo(BaseModel):
    name: str
    squat_kg: float
    squat_lbs: float
    bench_kg: float
    bench_lbs: float
    deadlift_kg: float
    deadlift_lbs: float
    dotscore: float
    total: float
    division: str
    weight_class: str
    profile_url: Optional[str] = None

class MeetAnalysisResponse(BaseModel):
    meet_name: str
    date: str
    total_lifters: int
    successful_lookups: int
    failed_lookups: int
    average_squat: float
    average_bench: float
    average_deadlift: float
    average_total: float
    top_performers: List[Dict[str, Any]]
    analysis_time: float
    timestamp: datetime

class DataStatusResponse(BaseModel):
    data_loaded: bool
    total_records: int
    last_update: Optional[str]
    cache_size_mb: float

# API ENDPOINTS

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Powerlifting Meet Scraper API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    global data_manager, lifter_processor
    
    return {
        "status": "healthy",
        "data_manager_ready": data_manager is not None,
        "lifter_processor_ready": lifter_processor is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/data/status", response_model=DataStatusResponse)
async def get_data_status():
    """Get status of OpenPowerlifting data"""
    global data_manager
    
    if not data_manager:
        raise HTTPException(status_code=503, detail="Data manager not initialized")
    
    try:
        # Get data info
        data_loaded = data_manager._data is not None
        total_records = len(data_manager._data) if data_loaded else 0
        
        # Get cache file size
        cache_size_mb = 0
        if os.path.exists(data_manager.data_file):
            cache_size_mb = os.path.getsize(data_manager.data_file) / (1024 * 1024)
        
        # Get last update time
        metadata = data_manager._load_metadata()
        last_update = metadata.get('last_update')
        
        return DataStatusResponse(
            data_loaded=data_loaded,
            total_records=total_records,
            last_update=last_update,
            cache_size_mb=round(cache_size_mb, 2)
        )
        
    except Exception as e:
        logger.error(f"Error getting data status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting data status: {str(e)}")



@app.post("/meet/analyze", response_model=MeetAnalysisResponse)
#Pass in the request and background tasks which is the meet url and max workers. 
async def analyze_meet(request: MeetAnalysisRequest, background_tasks: BackgroundTasks):
    """Analyze a powerlifting meet from LiftingCast URL"""
    global data_manager, lifter_processor
    
    # Check if data manager and lifter processor are initialized and exist. 
    if not data_manager or not lifter_processor:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    start_time = datetime.now()
    
    try:
        logger.info(f"Starting meet analysis for: {request.meet_url}")
        
        # Extract lifters from the meet page
        lifter_data_list = lifter_processor.extract_lifters_with_divisions(str(request.meet_url))
        
        if not lifter_data_list:
            raise HTTPException(status_code=404, detail="No lifters found on the meet page")
        
        # Process all lifters
        competitors = lifter_processor.process_lifters(lifter_data_list, request.max_workers)
        
        if not competitors:
            raise HTTPException(status_code=500, detail="Failed to process any lifters")
        
        # Calculate statistics - handle string to float conversion
        successful_lookups = len(competitors)
        failed_lookups = len(lifter_data_list) - successful_lookups
        
        # Calculate averages - convert strings to floats safely
        def safe_float(value):
            """Safely convert value to float, return 0 if conversion fails"""
            if not value:
                return 0
            try:
                return float(value)
            except (ValueError, TypeError):
                return 0
        
        # Get valid lift data (non-zero values)
        squats = [safe_float(c.squat_kg) for c in competitors if c.squat_kg]
        benches = [safe_float(c.bench_kg) for c in competitors if c.bench_kg]
        deadlifts = [safe_float(c.deadlift_kg) for c in competitors if c.deadlift_kg]
        totals = [safe_float(c.total) for c in competitors if c.total]
        
        # Filter out zero values
        squats = [s for s in squats if s > 0]
        benches = [b for b in benches if b > 0]
        deadlifts = [d for d in deadlifts if d > 0]
        totals = [t for t in totals if t > 0]
        
        # Set defaults for missing attributes
        average_squat = sum(squats) / len(squats) if squats else 0
        average_bench = sum(benches) / len(benches) if benches else 0
        average_deadlift = sum(deadlifts) / len(deadlifts) if deadlifts else 0
        average_total = sum(totals) / len(totals) if totals else 0
        
        # Get top performers (by dot score) - include detailed stats
        top_performers = []
        sorted_competitors = sorted(
            competitors, 
            key=lambda x: safe_float(x.dotscore), 
            reverse=True
        )
        for competitor in sorted_competitors[:10]:  # Top 10
            top_performers.append({
                "name": competitor.name,
                "total": safe_float(competitor.total),
                "squat_kg": safe_float(competitor.squat_kg),
                "bench_kg": safe_float(competitor.bench_kg),
                "deadlift_kg": safe_float(competitor.deadlift_kg),
                "dotscore": safe_float(competitor.dotscore),
                "weight_class": competitor.weight_class,
                "age": 0,  # Age not available
                "division": competitor.division
            })
        
        analysis_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Meet analysis completed: {len(competitors)} lifters processed in {analysis_time:.2f}s")
        
        return MeetAnalysisResponse(
            meet_name="Powerlifting Meet",  # We'll extract this from the URL later
            date=datetime.now().strftime("%Y-%m-%d"),
            total_lifters=len(lifter_data_list),
            successful_lookups=successful_lookups,
            failed_lookups=failed_lookups,
            average_squat=average_squat,
            average_bench=average_bench,
            average_deadlift=average_deadlift,
            average_total=average_total,
            top_performers=top_performers,
            analysis_time=analysis_time,
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing meet: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing meet: {str(e)}")

@app.get("/lifter/search")
async def search_lifters(name: str, limit: int = 20, offset: int = 0):
    """Search for lifters by name in OpenPowerlifting data"""
    global data_manager
    
    if not data_manager:
        raise HTTPException(status_code=503, detail="Data manager not initialized")
    
    if not name or len(name.strip()) < 2:
        raise HTTPException(status_code=400, detail="Name must be at least 2 characters long")
    
    try:
        logger.info(f"Searching for lifters with name: {name}")
        
        # Use the efficient index-based search
        if data_manager._name_index is None:
            logger.error("Name index is None - data not loaded properly")
            raise HTTPException(status_code=503, detail="Data not loaded")
        
        logger.info(f"Using indexed search. Total indexed names: {len(data_manager._name_index)}")
        
        # Search using the pre-built index
        matching_lifters = []
        search_term = name.strip().lower()
        normalized_search = search_term.replace(' ', '').replace(',', '')
        
        # Find all matching names in the index
        matching_names = []
        for indexed_name in data_manager._name_index.keys():
            if normalized_search in indexed_name or indexed_name.startswith(normalized_search):
                matching_names.append(indexed_name)
        
        logger.info(f"Found {len(matching_names)} matching names in index")
        
        # Get all records for matching names
        for indexed_name in matching_names:
            records = data_manager._name_index[indexed_name]
            for record in records:
                # Create lifter object from indexed record
                lifter = {
                    "name": record['original_name'],
                    "total": record['total'],
                    "squat_kg": record['squat'],
                    "bench_kg": record['bench'],
                    "deadlift_kg": record['deadlift'],
                    "dotscore": record['dotscore'],
                    "weight_class": str(record['weight_class']),
                    "age": record['age'],
                    "division": record['division'],
                    "meet_name": record['meet_name'],
                    "date": record['date']
                }
                matching_lifters.append(lifter)
        
        # Sort by dot score (best performance first)
        matching_lifters.sort(key=lambda x: x['dotscore'], reverse=True)
        
        # Apply pagination and limit total results to prevent overwhelming response
        total_count = len(matching_lifters)
        max_results = min(limit, 100)  # Cap at 100 results max
        paginated_lifters = matching_lifters[offset:offset + max_results]
        
        logger.info(f"Found {total_count} lifters matching '{name}', returning {len(paginated_lifters)} results")
        
        return {
            "lifters": paginated_lifters,
            "total_count": total_count,
            "search_term": name,
            "limit": limit,
            "offset": offset,
            "search_timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching for lifters with name '{name}': {e}")
        raise HTTPException(status_code=500, detail=f"Error searching for lifters: {str(e)}")

@app.post("/data/update")
async def update_data():
    """Manually trigger data update"""
    global data_manager
    
    if not data_manager:
        raise HTTPException(status_code=503, detail="Data manager not initialized")
    
    try:
        logger.info("Manual data update requested")
        success = data_manager.update_if_needed()
        
        return {
            "success": success,
            "message": "Data update completed" if success else "Data update failed",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error updating data: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating data: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 