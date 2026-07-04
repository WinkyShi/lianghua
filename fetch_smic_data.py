#!/usr/bin/env python3
"""通过东方财富API获取中芯国际(688981)近一年日线数据"""
import os
# 保持系统代理（沙箱环境需要代理访问外网）
import requests
import json
import csv
from datetime import datetime, timedelta

# 中芯国际 A股代码: 688981 (上交所)
# 东方财富的secid格式: 1.688981 (1=上交所, 0=深交所)
secid = "1.688981"

# 计算近一年日期范围
end_date = datetime.now()
start_date = end_date - timedelta(days=365)
start_str = start_date.strftime("%Y%m%d")
end_str = end_date.strftime("%Y%m%d")

print(f"获取中芯国际(688981) {start_str} ~ {end_str} 日线行情数据...")

# 东方财富日K线API
url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
params = {
    "fields1": "f1,f2,f3,f4,f5,f6",
    "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
    "ut": "7eea3edcaed734bea9cbfc24409ed989",
    "klt": "101",   # 101=日线
    "fqt": "1",     # 1=前复权
    "secid": secid,
    "beg": start_str,
    "end": end_str,
}

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://quote.eastmoney.com/",
}

try:
    resp = requests.get(url, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    
    klines = data.get("data", {}).get("klines", [])
    if not klines:
        print("未获取到数据，完整返回:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"成功获取 {len(klines)} 条日线数据")
        print(f"股票名称: {data['data'].get('name')}")
        print(f"股票代码: {data['data'].get('code')}")
        
        # 解析数据
        # 格式: 日期,开盘,收盘,最高,最低,成交量,成交额,振幅,涨跌幅,涨跌额,换手率
        records = []
        for line in klines:
            parts = line.split(",")
            record = {
                "日期": parts[0],
                "开盘": float(parts[1]),
                "收盘": float(parts[2]),
                "最高": float(parts[3]),
                "最低": float(parts[4]),
                "成交量": float(parts[5]),      # 手
                "成交额": float(parts[6]),      # 元
                "振幅": float(parts[7]),
                "涨跌幅": float(parts[8]),
                "涨跌额": float(parts[9]),
                "换手率": float(parts[10]),
            }
            records.append(record)
        
        # 打印前5条和后5条
        print("\n前5条数据:")
        for r in records[:5]:
            print(f"  {r['日期']} 开:{r['开盘']:.2f} 高:{r['最高']:.2f} 低:{r['最低']:.2f} 收:{r['收盘']:.2f} 量:{r['成交量']:.0f}手 涨跌幅:{r['涨跌幅']:.2f}%")
        print("...")
        print("后5条数据:")
        for r in records[-5:]:
            print(f"  {r['日期']} 开:{r['开盘']:.2f} 高:{r['最高']:.2f} 低:{r['最低']:.2f} 收:{r['收盘']:.2f} 量:{r['成交量']:.0f}手 涨跌幅:{r['涨跌幅']:.2f}%")
        
        # 保存CSV
        csv_path = "/Users/shiwenjie/Desktop/量化交易/中芯国际_688981_日线行情.csv"
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)
        print(f"\nCSV已保存至: {csv_path}")
        
        # 保存JSON
        json_path = "/Users/shiwenjie/Desktop/量化交易/中芯国际_688981_日线行情.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        print(f"JSON已保存至: {json_path}")
        
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
