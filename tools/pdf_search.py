from tools.web_search import web_search


def pdf_search(query: str, max_results: int = 5):
    search_query = f"{query} filetype:pdf"

    result = web_search(search_query, max_results=max_results)

    pdf_results = []

    for item in result.get("results", []):
        url = item.get("url", "")

        if ".pdf" in url.lower():
            pdf_results.append({
                "title": item.get("title"),
                "url": url,
                "content": item.get("content"),
                "score": item.get("score")
            })

    return {
        "query": query,
        "results": pdf_results
    }