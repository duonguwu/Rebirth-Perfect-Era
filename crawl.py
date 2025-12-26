import requests
from bs4 import BeautifulSoup
import os
import time
import traceback
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://novelhi.com/s/Rebirth-in-a-Perfect-Era/{}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

OUTPUT_DIR = "en_sub"
LOG_FILE = "crawl_error.log"

MAX_WORKERS = 32        # số luồng (6–12 là đẹp)
REQUEST_TIMEOUT = 15


# ===================== LOG =====================

def log_error(chapter_num, error):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] Chapter {chapter_num}\n")
        f.write(str(error) + "\n")
        f.write(traceback.format_exc())
        f.write("\n" + "=" * 80 + "\n")


# ===================== CRAWL 1 CHAPTER =====================

def crawl_chapter(chapter_num):
    file_path = os.path.join(OUTPUT_DIR, f"chapter_{chapter_num}.txt")

    # 👉 RESUME: đã có file thì skip
    if os.path.exists(file_path):
        return f"⏭️  Skip chapter {chapter_num} (đã tồn tại)"

    url = BASE_URL.format(chapter_num)
    r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    title_tag = soup.select_one("div.book_title h1")
    title = title_tag.get_text(strip=True) if title_tag else f"Chapter {chapter_num}"

    content_div = soup.select_one("div.readBox")
    if not content_div:
        raise ValueError("Không tìm thấy div.readBox")

    sentences = content_div.find_all("sent")
    if not sentences:
        raise ValueError("Không tìm thấy thẻ <sent>")

    paragraphs = []
    for s in sentences:
        text = s.get_text(strip=True)
        if text:
            paragraphs.append(text)

    chapter_text = title + "\n\n" + "\n\n".join(paragraphs)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(chapter_text)

    return f"✅ Saved chapter {chapter_num}"


# ===================== MULTI THREAD =====================

def crawl_range_async(start_chapter, end_chapter):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"🚀 Crawl từ chương {start_chapter} → {end_chapter}")
    print(f"⚙️  Số luồng: {MAX_WORKERS}\n")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(crawl_chapter, ch): ch
            for ch in range(start_chapter, end_chapter + 1)
        }

        for future in as_completed(futures):
            ch = futures[future]
            try:
                result = future.result()
                print(result)
            except Exception as e:
                print(f"❌ Lỗi chương {ch}")
                log_error(ch, e)

    print("\n🎉 Crawl hoàn tất!")


# ===================== MAIN =====================

if __name__ == "__main__":
    try:
        start = int(input("Nhập chương bắt đầu: "))
        end = int(input("Nhập chương kết thúc: "))

        if start > end:
            raise ValueError("Chương bắt đầu phải <= chương kết thúc")

        crawl_range_async(start, end)

    except Exception as e:
        print("❌ Lỗi nhập liệu hoặc lỗi hệ thống")
        log_error("INIT", e)
