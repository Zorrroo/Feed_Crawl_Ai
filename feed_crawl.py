from fastmcp import FastMCP
import feedparser
from prefect import flow  # <-- 1. Added Prefect import

mcp = FastMCP(name="Feed Parser MCP")

@mcp.tool()
def fcc_news_search(query: str, max_results: int = 5):
    """Search for news articles using the FCC News API. 
    IMPORTANT: Provide only single-word keywords (e.g., 'python', 'react') for best results. Do not use multi-word phrases."""
   
    feed = feedparser.parse("https://www.freecodecamp.org/news/rss/")
    results = []
    query_words = query.lower().split()
    
    for entry in feed.entries:
        title = entry.get("title", "").lower()
        description = entry.get("description", "").lower()
        
        if any(word in title or word in description for word in query_words):
            results.append({
                "title": entry.get("title", ""),
                "url": entry.get("link", "")
            })
            
        if len(results) >= max_results:
            break 

    return results or [{"message": f"No results found for '{query}'."}]

@mcp.tool()
def fcc_youtube_search(query: str, max_results: int = 5):
    """Search FreeCodeCamp YouTube videos related to the given query using the FCC YouTube channel RSS feed by title."""
    feed = feedparser.parse("https://www.youtube.com/feeds/videos.xml?channel_id=UC8butISFwT-Wl7EV0hUK0BQ")
    results = []
    query_lower = query.lower()
    for entry in feed.entries:
        title = entry.get("title", "")
        if query_lower in title.lower():
            results.append({
                "title": title,
                "url": entry.get("link", "")
            })
        if len(results) >= max_results:
            break 

    return results or [{"message": "No results found."}]

# <-- 2. Created the Prefect Flow -->
@flow(name="Feed Parser MCP Deployment", log_prints=True)
def main():
    print("Starting the MCP Server via Prefect...")
    # Switched transport to "sse" as FastMCP doesn't natively use "http"
    mcp.run(transport="sse", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
