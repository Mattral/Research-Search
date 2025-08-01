from fastapi import FastAPI
from recommendation.engine import recommend_papers

app = FastAPI()

@app.get("/recommendations/{user_id}")
def get_recommendations(user_id: int):
    data = recommend_papers(user_id)
    if not data.get("recommendations"):
        data = {"message": "No recommendations found"}
    return data
