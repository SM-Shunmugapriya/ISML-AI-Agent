import requests


def audio_search(query: str, max_results: int = 5):
    try:
        url = "https://archive.org/advancedsearch.php"

        params = {
            "q": f"{query} AND mediatype:audio",
            "fl[]": ["identifier", "title", "description"],
            "rows": max_results,
            "page": 1,
            "output": "json"
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        audios = []

        for doc in data.get("response", {}).get("docs", []):
            identifier = doc.get("identifier")

            if not identifier:
                continue

            audios.append({
                "title": doc.get("title"),
                "url": f"https://archive.org/details/{identifier}",
                "description": doc.get("description"),
                "resource_type": "audio"
            })

        return {
            "query": query,
            "results": audios
        }

    except Exception as e:
        return {
            "query": query,
            "results": [],
            "error": str(e)
        }
