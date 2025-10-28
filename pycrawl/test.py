from firecrawl.firecrawl import FirecrawlApp
from pydantic import BaseModel, Field

app = FirecrawlApp(api_key="fc-4a1f5c926ffd4e26a1ff128040a7f669")

class ArticleSchema(BaseModel):
    title: str
    points: int
    by: str
    commentsURL: str

class TopArticlesSchema(BaseModel):
    top: List[ArticleSchema] = Field(..., max_items=5, description="Top 5 stories")

data = app.scrape_url('https://quote.eastmoney.com/stock/171.CN30Y.html', {
    'formats': ['json'],
    'extract': {
        'schema': TopArticlesSchema.model_json_schema()
    }
})
print(data["extract"])
