"""JARVIS Research Skill - Web research."""

import requests
from bs4 import BeautifulSoup
from jarvis_core.logger import get_logger
logger = get_logger()

def search_web(query: str, engine: str = "google", num_results: int = 5) -> dict:
    """Search the web."""
    engines = {
        "google": f"https://www.google.com/search?q={query}&num={num_results}",
    }
    url = engines.get(engine, engines["google"])
    
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        results = []
        for item in soup.select("div.g")[:num_results]:
            title = item.select_one("h3")
            link = item.select_one("a")
            if title and link:
                results.append({
                    "title": title.text,
                    "url": link.get("href", "")
                })
        return {"success": True, "results": results}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_page_content(url: str) -> dict:
    """Get page content."""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        return {"success": True, "content": text[:5000]}
    except Exception as e:
        return {"success": False, "error": str(e)}

def summarize_url(url: str) -> dict:
    """Summarize a URL."""
    content = get_page_content(url)
    if content.get("success"):
        text = content.get("content", "")[:1000]
        return {"success": True, "summary": f"Page contains {len(text)} characters: {text[:200]}..."}
    return content