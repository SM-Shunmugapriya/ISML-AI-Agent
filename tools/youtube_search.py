from youtubesearchpython import VideosSearch


def youtube_search(query: str, max_results: int = 5):
    search = VideosSearch(query, limit=max_results)
    result = search.result()

    videos = []

    for video in result.get("result", []):
        videos.append({
            "title": video.get("title"),
            "url": video.get("link"),
            "channel": video.get("channel", {}).get("name"),
            "duration": video.get("duration"),
            "views": video.get("viewCount", {}).get("text"),
            "thumbnail": video.get("thumbnails", [{}])[0].get("url")
        })

    return {
        "query": query,
        "results": videos
    }