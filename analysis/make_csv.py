# Author: Acer Zhang
# Datetime: 2022/2/8
# Copyright belongs to the author.
# Please indicate the source for reprinting.

import os
import glob
import json
import csv
import datetime
import time

from gtoken import get_info_4_url

END_TIME = datetime.datetime.now()
START_TIME = END_TIME - datetime.timedelta(days=365)
print("统计时间线:", START_TIME, " - ", END_TIME)

ori_headers = ["时间", "星期", "排名", "所有者", "URL", "描述", "主要语言"]
analysis_headers = ["URL", "Star", "连续上榜天数", "近1月上榜次数", "区间内上榜次数", "描述", "主要语言", "创建时间"]

ROOT = os.path.dirname(os.path.dirname(__file__))

json_file_paths = glob.glob(os.path.join(ROOT, "data/*.json"))

# 增加多日Trending数据、最大Trending月均、分时
# 1. 看看能不能拿到Trending规律 2. 拿到热门项目列表
ori_data = list()
continuity_trending = dict()
month_trending = dict()
all_trending = dict()

for json_id, json_file_path in enumerate(json_file_paths):
    file_name = os.path.basename(json_file_path)
    date = os.path.splitext(file_name)[0]
    date_o = datetime.datetime(*[int(_) for _ in date.split("-")])
    # 时间段过滤
    if date_o < START_TIME:
        continue

    with open(json_file_path, "r", encoding="utf-8") as f:
        js_data = json.load(f)

    include_repo = list()
    for j_id, j_data in enumerate(js_data):
        pack = dict().fromkeys(ori_headers, "None")
        pack["时间"] = date
        pack["星期"] = str(date_o.weekday())
        pack["排名"] = str(j_id + 1)
        pack["所有者"] = j_data["title"]
        pack["URL"] = j_data["url"]
        # 用get避免None的情况
        pack["描述"] = j_data.get("desc")
        pack["主要语言"] = j_data.get("lang")
        ori_data.append(pack)

        # 总Trending次数
        if pack["URL"] in all_trending:
            all_trending[pack["URL"]] += 1
        else:
            all_trending[pack["URL"]] = 1

        # 月度Trending次数
        if date_o >= END_TIME - datetime.timedelta(days=30):
            if pack["URL"] in month_trending:
                month_trending[pack["URL"]] += 1
            else:
                month_trending[pack["URL"]] = 1

        # MAX持续Trending - 记录
        if pack["URL"] in continuity_trending:
            if continuity_trending[pack["URL"]][2] is True:
                continuity_trending[pack["URL"]][0] = 1

            continuity_trending[pack["URL"]][0] += 1
            continuity_trending[pack["URL"]][2] = False
            if continuity_trending[pack["URL"]][0] > continuity_trending[pack["URL"]][1]:
                continuity_trending[pack["URL"]][1] = continuity_trending[pack["URL"]][0]
        else:
            # 当前连续, 最大连续, 是否终止
            continuity_trending[pack["URL"]] = [1, 1, False]
        include_repo.append(pack["URL"])
    # 对未连续上榜的项目给予终止位 - 也可做个cache来提升速度
    for _key in continuity_trending:
        if _key not in include_repo:
            continuity_trending[_key][2] = True

# 合并分析数据
ana_data = list()
for _url_id, _url in enumerate(continuity_trending):
    time.sleep(0.1)
    print(f"\r正在处理\t{_url_id + 1}/{len(continuity_trending)}数据", end="", flush=True)
    pack = dict().fromkeys(analysis_headers, "None")
    pack["URL"] = _url
    pack["Star"], pack["主要语言"], pack["描述"], pack["创建时间"] = get_info_4_url(_url)
    pack["连续上榜天数"] = str(continuity_trending[_url][1])
    pack["近1月上榜次数"] = str(month_trending.get(_url, 0))
    pack["区间内上榜次数"] = str(all_trending.get(_url, 0))
    ana_data.append(pack)

with open(os.path.join(ROOT, "Analysis.csv"), "w", encoding="utf-8-sig") as f:
    dw = csv.DictWriter(f, fieldnames=analysis_headers)
    dw.writeheader()
    dw.writerows(ana_data)

with open(os.path.join(ROOT, "Ori.csv"), "w", encoding="utf-8-sig") as f:
    dw = csv.DictWriter(f, fieldnames=ori_headers)
    dw.writeheader()
    dw.writerows(ori_data)
