from fastapi import FastAPI;
from routers import users;
from supabase import create_client, Client;


app = FastAPI();

app.include_router(users.router);

SUPABASE_URL='https://ovxyeoqyqdvqwpkcgsqd.supabase.co'
SUPABASE_KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im92eHllb3F5cWR2cXdwa2Nnc3FkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE2ODM4NjUsImV4cCI6MjA2NzI1OTg2NX0.9tAM4qLWlZxAJDcmk7E-6ZVLH8PlzmzgC1jA6v3kRPo'

#group_members
#hotels
#itinerarios
#flights
#groups
#trips
#ia_chat
#votes
#group_chat