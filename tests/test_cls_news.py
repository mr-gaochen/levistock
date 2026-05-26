import hashlib
import requests
import datetime

def cls_sign(params: dict) -> str:
    s = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    sha1 = hashlib.sha1(s.encode()).hexdigest()
    return hashlib.md5(sha1.encode()).hexdigest()

BASE = {
    "app": "cailianpress", "sv": "8.7.4", "os": "android",
    "mb": "Xiaomi-2206123SC", "ov": "32", "channel": "8",
    "motif": "0", "net": "", "province_code": "3205",
    "token": "", "uid": "",
}

def fetch_page(last_time="0", category=""):
    p = dict(BASE, refresh_type="1", last_time=last_time, rn="20")
    if category:
        p["category"] = category
    p["sign"] = cls_sign(p)
    resp = requests.get(
        "https://api3.cls.cn/v1/roll/get_roll_list",
        headers={"User-Agent": "okhttp/4.9.0", "Host": "api3.cls.cn"},
        params=p
    )
    return resp.json()

def fetch_by_date(date_str=None, category=""):
    """
    date_str: "2026-05-08" 格式，不传则查今天
    category: "" 全部 / "red" 加红 / "announcement" 公司
    """
    if date_str:
        day = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    else:
        day = datetime.datetime.now()

    day_start = int(datetime.datetime(day.year, day.month, day.day, 0, 0, 0).timestamp())
    day_end = int(datetime.datetime(day.year, day.month, day.day, 23, 59, 59).timestamp())

    all_items = []
    last_time = str(day_end)

    while True:
        data = fetch_page(last_time, category)
        roll_data = data["data"]["roll_data"]

        if not roll_data:
            break

        for item in roll_data:
            if item["ctime"] < day_start:
                return all_items
            if item["ctime"] <= day_end:
                all_items.append(item)

        last_time = str(roll_data[-1]["sort_score"])

    return all_items


if __name__ == "__main__":
    # 查今天公司公告
    items = fetch_by_date(date_str="2026-05-07", category="announcement")
    print(f"2026-05-07 公司公告共 {len(items)} 条")
    for item in items:
        t = datetime.datetime.fromtimestamp(item["ctime"])
        print(f"{t} | {item['title'][:50]}")