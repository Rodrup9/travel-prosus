from fastapi import APIRouter;
from supabase import create_client, Client;

router = APIRouter(prefix="/users", tags=["users"]);

SUPABASE_URL='https://ovxyeoqyqdvqwpkcgsqd.supabase.co'
SUPABASE_KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im92eHllb3F5cWR2cXdwa2Nnc3FkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE2ODM4NjUsImV4cCI6MjA2NzI1OTg2NX0.9tAM4qLWlZxAJDcmk7E-6ZVLH8PlzmzgC1jA6v3kRPo'

@router.get("/")
async def getUsers():
    return [];


    #LcyUBsviY0AI00Td   