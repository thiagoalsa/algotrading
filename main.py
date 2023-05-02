from fastapi import FastAPI
from ping.view import router as ping_router
from machine_learning.view import router as machine_learning_router


app = FastAPI()

app.include_router(ping_router)
app.include_router(machine_learning_router)