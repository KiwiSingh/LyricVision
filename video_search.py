# video_search.py

import os
import requests
import time
import re
from typing import List, Dict


class VideoSearch:

    def __init__(
        self,
        pexels_key=None,
        pixabay_key=None,
        resolution="1080p",
        rate_limit_delay=1.2,
        max_keywords=6,
        batch_size=3
    ):
        self.target_resolution = resolution
        self.target_width = 3840 if resolution == "4K" else 1920

        self.pexels_key = pexels_key
        self.pixabay_key = pixabay_key

        self.delay = rate_limit_delay
        self.max_keywords = max_keywords
        self.batch_size = batch_size

    # ======================================================
    # PUBLIC ENTRY
    # ======================================================

    def search(self, keywords: List[str], per_query: int = 2) -> List[Dict]:
        keywords = self._clean_keywords(keywords)
        keywords = keywords[:self.max_keywords]

        results = []

        if self.pexels_key:
            results += self._search_pexels(keywords, per_query)

        if self.pixabay_key:
            results += self._search_pixabay(keywords, per_query)

        return results

    # ======================================================
    # CLEAN KEYWORDS
    # ======================================================

    def _clean_keywords(self, keywords: List[str]) -> List[str]:
        cleaned = []

        for kw in keywords:
            if not kw:
                continue

            kw = str(kw).strip()
            kw = kw.replace("```json", "")
            kw = kw.replace("```", "")
            kw = kw.replace("[", "")
            kw = kw.replace("]", "")
            kw = kw.replace('"', "")
            kw = re.sub(r"\s+", " ", kw)

            if kw:
                cleaned.append(kw)

        return list(dict.fromkeys(cleaned))

    # ======================================================
    # PEXELS
    # ======================================================

    def _search_pexels(self, keywords: List[str], per_query: int) -> List[Dict]:
        url = "https://api.pexels.com/videos/search"
        headers = {"Authorization": self.pexels_key}
        results = []

        for keyword in keywords:
            time.sleep(self.delay)

            params = {
                "query": keyword,
                "per_page": per_query
            }

            try:
                response = requests.get(url, headers=headers, params=params, timeout=10)

                if response.status_code == 429:
                    print("[Pexels] Rate limit hit. Sleeping 5 seconds...")
                    time.sleep(5)
                    continue

                response.raise_for_status()
                data = response.json()

                for video in data.get("videos", []):

                    if self._is_ai_content(
                        video.get("user", {}).get("name", ""),
                        video.get("tags", []),
                    ):
                        continue

                    video_files = video.get("video_files", [])
                    if not video_files:
                        continue

                    video_files = sorted(
                        video_files,
                        key=lambda x: x.get("width", 0),
                        reverse=True
                    )

                    candidates = [
                        v for v in video_files
                        if v.get("width", 0) >= self.target_width
                    ]

                    if candidates:
                        best_file = sorted(candidates, key=lambda x: x["width"])[0]
                    else:
                        best_file = video_files[0]

                    results.append({
                        "source": "Pexels",
                        "keyword_query": keyword,
                        "url": best_file["link"],
                        "preview": video.get("image"),
                        "user": video.get("user", {}).get("name", "Unknown"),
                        "duration": video.get("duration"),
                        "width": best_file.get("width"),
                        "height": best_file.get("height"),
                    })

            except Exception as e:
                print(f"[Pexels Error] {e}")

        return results

    # ======================================================
    # PIXABAY
    # ======================================================

    def _search_pixabay(self, keywords: List[str], per_query: int) -> List[Dict]:
        url = "https://pixabay.com/api/videos/"
        results = []

        for keyword in keywords:
            time.sleep(self.delay)

            params = {
                "key": self.pixabay_key,
                "q": keyword,
                "per_page": per_query,
            }

            try:
                response = requests.get(url, params=params, timeout=10)

                if response.status_code == 429:
                    print("[Pixabay] Rate limit hit. Sleeping 5 seconds...")
                    time.sleep(5)
                    continue

                response.raise_for_status()
                data = response.json()

                for video in data.get("hits", []):

                    if self._is_ai_content(
                        video.get("user", ""),
                        video.get("tags", ""),
                    ):
                        continue

                    variants = list(video.get("videos", {}).values())
                    if not variants:
                        continue

                    variants = sorted(
                        variants,
                        key=lambda x: x.get("width", 0),
                        reverse=True
                    )

                    candidates = [
                        v for v in variants
                        if v.get("width", 0) >= self.target_width
                    ]

                    if candidates:
                        best_variant = sorted(candidates, key=lambda x: x["width"])[0]
                    else:
                        best_variant = variants[0]

                    results.append({
                        "source": "Pixabay",
                        "keyword_query": keyword,
                        "url": best_variant.get("url"),
                        "preview": video.get("picture_id"),
                        "user": video.get("user", "Unknown"),
                        "duration": video.get("duration"),
                        "width": best_variant.get("width"),
                        "height": best_variant.get("height"),
                    })

            except Exception as e:
                print(f"[Pixabay Error] {e}")

        return results

    # ======================================================
    # AI FILTER
    # ======================================================

    def _is_ai_content(self, user_name, tags) -> bool:
        if isinstance(tags, list):
            tags = " ".join(tags)

        combined = f"{user_name} {tags}".lower()

        ai_indicators = [
            "ai",
            "artificial",
            "generated",
            "midjourney",
            "stable diffusion",
            "dalle",
            "suno",
        ]

        return any(indicator in combined for indicator in ai_indicators)

    # ======================================================
    # VIDEO DOWNLOADER
    # ======================================================

    def download_videos(self, videos: List[Dict], download_dir: str) -> List[Dict]:
        os.makedirs(download_dir, exist_ok=True)

        downloaded = []

        for idx, video in enumerate(videos):
            try:
                url = video["url"]

                ext = url.split("?")[0].split(".")[-1]
                filename = f"clip_{idx+1:02d}.{ext}"
                filepath = os.path.join(download_dir, filename)

                print(f"Downloading {url}")

                r = requests.get(url, stream=True, timeout=30)
                r.raise_for_status()

                with open(filepath, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

                video["local_path"] = os.path.abspath(filepath)
                downloaded.append(video)

            except Exception as e:
                print(f"[Download Error] {e}")

        return downloaded