:: Initialize Conda (ensure this path is correct for your setup)
CALL conda activate DF

:: Change directory to backend
cd backend

:: Run the FastAPI application using uvicorn with reload
uvicorn main:app --reload --log-level info
