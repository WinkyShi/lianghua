#!/usr/bin/env python3
"""通过Tushare REST API直接获取中芯国际日线数据"""
import os
import json
import requests

# 保持代理设置（Tushare API需要通过代理访问）

TUSHARE_TOKEN = "0f9780a7f2c3294a1f1d0297d1e0735cbe23752f1c2d5936bba115a8"
TUSHARE_API = "https://api.tushare.pro/api"

def call_tushare(api_name, params, fields=None):
    payload = {
        "api_name": api_name,
        "token": TUSHARE_TOKEN,
        "params": params
    }
    if fields:
        payload["fields"] = fields
    r = requests.post(TUSHARE_API, json=payload, timeout=30)
    result = r.json()
    if result.get("code") != 0:
        print(f"API错误: {result}")
        return None
    return result

# 测试1: 获取股票基本信息（确认token有效性）
print("=== 测试1: 获取中芯国际基本信息 ===")
result = call_tushare("stock_basic", {"ts_code": "688981.SH"})
if result:
    print(json.dumps(result, indent=2, ensure_ascii=False))
else:
    print("stock_basic 接口无权限")

# 测试2: 尝试日线数据
print("\n=== 测试2: 获取日线数据 ===")
result = call_tushare("daily", {
    "ts_code": "688981.SH",
    "start_date": "20250704",
    "end_date": "20260704"
})
if result:
    print(f"获取到 {len(result.get('data', {}).get('items', []))} 条记录")
    print(json.dumps(result, indent=2, ensure_ascii=False)[:2000])
else:
    print("daily 接口无权限")

# 测试3: 尝试通用行情接口 pro_bar
print("\n=== 测试3: 尝试pro_bar接口 ===")
result = call_tushare("pro_bar", {
    "ts_code": "688981.SH",
    "start_date": "20250704",
    "end_date": "20260704",
    "freq": "D",
    "adj": "qfq"
})
if result:
    print(f"获取到 {len(result.get('data', {}).get('items', []))} 条记录")
    print(json.dumps(result, indent=2, ensure_ascii=False)[:2000])
else:
    print("pro_bar 接口无权限")
