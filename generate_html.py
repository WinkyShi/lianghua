#!/usr/bin/env python3
"""生成中芯国际K线图+成交量图HTML面板"""
import json
import os

# 读取JSON数据
json_path = "/Users/shiwenjie/Desktop/量化交易/中芯国际_688981_日线行情.json"
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 构建ECharts所需数据格式
dates = []
kline_data = []  # [open, close, low, high]
vol_data = []    # [volume, is_up]
amount_data = []
pct_data = []

for item in data:
    dates.append(item["日期"])
    kline_data.append([item["开盘"], item["收盘"], item["最低"], item["最高"]])
    is_up = item["收盘"] >= item["开盘"]
    vol_data.append({"value": item["成交量"], "is_up": is_up})
    amount_data.append(round(item["成交额"] / 10000, 2))  # 转为万元
    pct_data.append(item["涨跌幅"])

# 计算统计信息
first_close = data[0]["收盘"]
last_close = data[-1]["收盘"]
year_high = max(d["最高"] for d in data)
year_low = min(d["最低"] for d in data)
year_change_pct = round((last_close - first_close) / first_close * 100, 2)
avg_vol = round(sum(d["成交量"] for d in data) / len(data))
max_vol = max(d["成交量"] for d in data)
total_amount = round(sum(d["成交额"] for d in data) / 100000000, 2)  # 亿元

# MA计算函数
def calc_ma(kline, n):
    result = [None] * len(kline)
    for i in range(n - 1, len(kline)):
        total = sum(kline[j][1] for j in range(i - n + 1, i + 1))
        result[i] = round(total / n, 2)
    return result

ma5 = calc_ma(kline_data, 5)
ma10 = calc_ma(kline_data, 10)
ma20 = calc_ma(kline_data, 20)
ma60 = calc_ma(kline_data, 60)

# 生成HTML
html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>中芯国际(688981) K线行情面板</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
    background: #f5f6fa;
    color: #333;
    padding: 20px;
  }}
  .header {{
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  }}
  .header-left .stock-name {{
    font-size: 28px;
    font-weight: 700;
    color: #fff;
  }}
  .header-left .stock-code {{
    font-size: 14px;
    color: #8899aa;
    margin-top: 4px;
  }}
  .header-right {{
    text-align: right;
  }}
  .header-right .price {{
    font-size: 32px;
    font-weight: 700;
    color: {'#e74c3c' if year_change_pct >= 0 else '#2ecc71'};
  }}
  .header-right .change {{
    font-size: 14px;
    color: {'#e74c3c' if year_change_pct >= 0 else '#2ecc71'};
    margin-top: 4px;
  }}
  .stats-grid {{
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 16px;
    margin-bottom: 20px;
  }}
  .stat-card {{
    background: #fff;
    border-radius: 10px;
    padding: 16px 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }}
  .stat-card .label {{
    font-size: 12px;
    color: #8899aa;
    margin-bottom: 6px;
  }}
  .stat-card .value {{
    font-size: 20px;
    font-weight: 600;
    color: #1a1a2e;
  }}
  .stat-card .sub {{
    font-size: 11px;
    color: #aaa;
    margin-top: 2px;
  }}
  .chart-container {{
    background: #fff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-bottom: 20px;
  }}
  .chart-title {{
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 12px;
    color: #1a1a2e;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .chart-title::before {{
    content: '';
    display: inline-block;
    width: 4px;
    height: 16px;
    background: #e74c3c;
    border-radius: 2px;
  }}
  #kline-chart {{
    width: 100%;
    height: 500px;
  }}
  .footer {{
    text-align: center;
    font-size: 12px;
    color: #aaa;
    padding: 12px 0;
  }}
  @media (max-width: 768px) {{
    .stats-grid {{ grid-template-columns: repeat(3, 1fr); }}
    .header {{ flex-direction: column; gap: 12px; text-align: center; }}
    .header-right {{ text-align: center; }}
  }}
</style>
</head>
<body>

<div class="header">
  <div class="header-left">
    <div class="stock-name">中芯国际</div>
    <div class="stock-code">688981.SH · 科创板 · 半导体</div>
  </div>
  <div class="header-right">
    <div class="price">¥{last_close:.2f}</div>
    <div class="change">近一年涨跌: {year_change_pct:+.2f}% ({first_close:.2f} → {last_close:.2f})</div>
  </div>
</div>

<div class="stats-grid">
  <div class="stat-card">
    <div class="label">年内最高价</div>
    <div class="value" style="color:#e74c3c">¥{year_high:.2f}</div>
    <div class="sub">前复权</div>
  </div>
  <div class="stat-card">
    <div class="label">年内最低价</div>
    <div class="value" style="color:#2ecc71">¥{year_low:.2f}</div>
    <div class="sub">前复权</div>
  </div>
  <div class="stat-card">
    <div class="label">日均成交量</div>
    <div class="value">{avg_vol:,.0f}</div>
    <div class="sub">手</div>
  </div>
  <div class="stat-card">
    <div class="label">单日最大量</div>
    <div class="value">{max_vol:,.0f}</div>
    <div class="sub">手</div>
  </div>
  <div class="stat-card">
    <div class="label">年度总成交额</div>
    <div class="value">{total_amount:,.1f}</div>
    <div class="sub">亿元</div>
  </div>
  <div class="stat-card">
    <div class="label">交易日数</div>
    <div class="value">{len(data)}</div>
    <div class="sub">天</div>
  </div>
</div>

<div class="chart-container">
  <div class="chart-title">K线图 & 成交量</div>
  <div id="kline-chart"></div>
</div>

<div class="footer">
  数据来源: 东方财富 · 前复权日线 · 更新时间: {data[-1]['日期']} · 仅供参考，不构成投资建议
</div>

<script>
var dates = {json.dumps(dates)};
var klineData = {json.dumps(kline_data)};
var volData = {json.dumps([v["value"] for v in vol_data])};
var ma5Data = {json.dumps(ma5)};
var ma10Data = {json.dumps(ma10)};
var ma20Data = {json.dumps(ma20)};
var ma60Data = {json.dumps(ma60)};

// 成交量颜色: 涨红跌绿(中国惯例)
var volColors = {json.dumps([('#e74c3c' if v["is_up"] else '#2ecc71') for v in vol_data])};

var chart = echarts.init(document.getElementById('kline-chart'));

var option = {{
  backgroundColor: '#fff',
  animation: false,
  tooltip: {{
    trigger: 'axis',
    axisPointer: {{
      type: 'cross',
      crossStyle: {{ color: '#999' }}
    }},
    formatter: function(params) {{
      var date = params[0].axisValue;
      var html = '<div style="font-size:13px;font-weight:600;margin-bottom:6px;">' + date + '</div>';
      params.forEach(function(p) {{
        var val = p.value;
        var color = '#333';
        if (p.seriesName === 'K线') {{
          var open = val[0], close = val[1], low = val[2], high = val[3];
          var pct = ((close - open) / open * 100).toFixed(2);
          color = close >= open ? '#e74c3c' : '#2ecc71';
          html += '<span style="color:' + color + '">●</span> ' + p.seriesName + '<br/>';
          html += '&nbsp;&nbsp;开盘: ' + open.toFixed(2) + '<br/>';
          html += '&nbsp;&nbsp;收盘: ' + close.toFixed(2) + '<br/>';
          html += '&nbsp;&nbsp;最高: ' + high.toFixed(2) + '<br/>';
          html += '&nbsp;&nbsp;最低: ' + low.toFixed(2) + '<br/>';
          html += '&nbsp;&nbsp;涨跌: <span style="color:' + color + '">' + pct + '%</span><br/>';
        }} else if (p.seriesName === '成交量') {{
          html += '<span style="color:#666">●</span> 成交量: ' + (val/10000).toFixed(1) + '万手<br/>';
        }} else if (val !== null && val !== undefined) {{
          color = p.seriesName === 'MA5' ? '#f39c12' : p.seriesName === 'MA10' ? '#3498db' : p.seriesName === 'MA20' ? '#9b59b6' : '#1abc9c';
          html += '<span style="color:' + color + '">●</span> ' + p.seriesName + ': ' + val.toFixed(2) + '<br/>';
        }}
      }});
      return html;
    }}
  }},
  axisPointer: {{
    link: {{ xAxisIndex: 'all' }}
  }},
  grid: [
    {{ left: '8%', right: '4%', top: '6%', height: '58%' }},
    {{ left: '8%', right: '4%', top: '70%', height: '22%' }}
  ],
  xAxis: [
    {{
      type: 'category',
      data: dates,
      scale: true,
      boundaryGap: false,
      splitLine: {{ show: false }},
      axisLabel: {{ color: '#888', fontSize: 11 }}
    }},
    {{
      type: 'category',
      gridIndex: 1,
      data: dates,
      scale: true,
      boundaryGap: false,
      splitLine: {{ show: false }},
      axisLabel: {{ show: false }}
    }}
  ],
  yAxis: [
    {{
      scale: true,
      splitLine: {{ lineStyle: {{ color: '#eee' }} }},
      axisLabel: {{ color: '#888', fontSize: 11, formatter: '¥{{value}}' }}
    }},
    {{
      gridIndex: 1,
      splitNumber: 2,
      axisLabel: {{ color: '#888', fontSize: 11, formatter: function(v) {{ return (v/10000).toFixed(0) + '万'; }} }},
      splitLine: {{ lineStyle: {{ color: '#eee' }} }}
    }}
  ],
  dataZoom: [
    {{
      type: 'inside',
      xAxisIndex: [0, 1],
      start: 0,
      end: 100
    }},
    {{
      type: 'slider',
      xAxisIndex: [0, 1],
      bottom: '2%',
      height: 20,
      start: 0,
      end: 100,
      borderColor: '#ddd',
      fillerColor: 'rgba(231,76,60,0.1)',
      handleStyle: {{ color: '#e74c3c' }}
    }}
  ],
  series: [
    {{
      name: 'K线',
      type: 'candlestick',
      data: klineData,
      itemStyle: {{
        color: '#e74c3c',        // 阳线(涨)红色
        color0: '#2ecc71',       // 阴线(跌)绿色
        borderColor: '#e74c3c',
        borderColor0: '#2ecc71'
      }}
    }},
    {{
      name: 'MA5',
      type: 'line',
      data: ma5Data,
      smooth: true,
      showSymbol: false,
      lineStyle: {{ width: 1, color: '#f39c12' }}
    }},
    {{
      name: 'MA10',
      type: 'line',
      data: ma10Data,
      smooth: true,
      showSymbol: false,
      lineStyle: {{ width: 1, color: '#3498db' }}
    }},
    {{
      name: 'MA20',
      type: 'line',
      data: ma20Data,
      smooth: true,
      showSymbol: false,
      lineStyle: {{ width: 1, color: '#9b59b6' }}
    }},
    {{
      name: 'MA60',
      type: 'line',
      data: ma60Data,
      smooth: true,
      showSymbol: false,
      lineStyle: {{ width: 1, color: '#1abc9c' }}
    }},
    {{
      name: '成交量',
      type: 'bar',
      xAxisIndex: 1,
      yAxisIndex: 1,
      data: volData.map(function(v, i) {{
        return {{
          value: v,
          itemStyle: {{ color: volColors[i] }}
        }};
      }})
    }}
  ]
}};

chart.setOption(option);
window.addEventListener('resize', function() {{ chart.resize(); }});
</script>

</body>
</html>
"""

output_path = "/Users/shiwenjie/Desktop/量化交易/中芯国际_K线面板.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"HTML面板已生成: {output_path}")
print(f"数据区间: {data[0]['日期']} ~ {data[-1]['日期']}")
print(f"交易日数: {len(data)}")
print(f"年度涨幅: {year_change_pct:+.2f}%")
print(f"年内最高: ¥{year_high:.2f}")
print(f"年内最低: ¥{year_low:.2f}")
