# xiafan.py - 抖音评论爬虫工具

## 项目简介

`xiafan.py` 是一个基于 DrissionPage 框架的抖音评论爬虫工具，能够自动抓取抖音视频或用户主页的评论数据，并导出为CSV格式文件。

## 功能特点

### 核心功能
- ✅ **自动爬取评论**：自动抓取抖音视频/主页的评论数据
- ✅ **多页采集**：支持设置爬取页数（默认3页）
- ✅ **网络监听**：使用DrissionPage监听网络请求
- ✅ **双格式导出**：同时生成UTF-8和GBK两种编码的CSV文件
- ✅ **特殊字符处理**：自动清理GBK不支持的emoji等特殊字符
- ✅ **数据保存**：自动保存到 `data.csv` 和 `抖音.csv`
- ✅ **错误处理**：完善的异常处理机制，出错时保存已采集的数据

### 数据字段
采集的评论数据包含以下字段：
- **时间**：评论发布时间（时间戳转换后的格式化时间）
- **名字**：评论者昵称
- **地区**：IP归属地（如果有的话，否则显示"未知"）
- **内容**：评论文本内容

## 环境要求

### Python版本
- Python 3.6 或更高版本

### 依赖库
```bash
pip install DrissionPage
pip install pandas
```

**依赖库说明：**
- `DrissionPage`：浏览器自动化框架，用于模拟浏览器操作和网络监听
- `pandas`：数据处理库（当前版本中引入但未使用，如需Excel导出可启用）
- `datetime`：时间格式化（Python标准库）
- `csv`：CSV文件读写（Python标准库）
- `time`：时间控制（Python标准库）
- `os`：文件操作（Python标准库）

## 使用方法

### 基本使用

1. **修改目标链接**
   
   打开 `xiafan.py` 文件，修改第14行的URL：
   ```python
   dy.get('https://www.douyin.com/user/self?from_tab_name=main&modal_id=7574396223752520866&showTab=like')
   ```
   
   改为你想要爬取的抖音页面链接。

2. **设置爬取页数**
   
   修改第19行的页数参数：
   ```python
   for page in range(1, 4):  # 爬取3页
   ```
   
   如果要爬取更多页面，修改为：
   ```python
   for page in range(1, 11):  # 爬取10页
   ```

3. **运行程序**
   ```bash
   python xiafan.py
   ```

### 链接格式说明

支持以下类型的抖音链接：

1. **用户点赞页面**
   ```
   https://www.douyin.com/user/self?from_tab_name=main&modal_id=视频ID&showTab=like
   ```

2. **视频详情页**
   ```
   https://www.douyin.com/video/视频ID
   ```

3. **用户主页**
   ```
   https://www.douyin.com/user/用户ID
   ```

4. **用户作品页**
   ```
   https://www.douyin.com/user/用户ID?from_tab_name=main
   ```

## 输出文件

程序运行完成后，会在当前目录生成两个CSV文件：

### 1. data.csv（UTF-8格式）
- **编码**：UTF-8
- **特点**：保留完整原始数据，包括emoji等特殊字符
- **适用场景**：程序读取、数据分析、Python处理

**示例内容：**
```csv
时间,名字,地区,内容
2024-01-15 14:30:25,用户123,北京,这个视频太棒了！👍
2024-01-15 14:25:18,小红,上海,说得很有道理，学习了
```

### 2. 抖音.csv（GBK格式）
- **编码**：GBK
- **特点**：已清理特殊字符，兼容Excel直接打开
- **适用场景**：Excel打开、WPS表格、日常查看

**示例内容：**
```csv
时间,名字,地区,内容
2024-01-15 14:30:25,用户123,北京,这个视频太棒了
2024-01-15 14:25:18,小红,上海,说得很有道理，学习了
```

## 代码结构

```python
# 导入依赖库
from DrissionPage import Chromium, ChromiumPage
from datetime import datetime
import csv
import time
import os
import pandas as pd

# 数据收集列表
all_data = []

# 初始化浏览器
dy = Chromium().latest_tab
dy.listen.start("/comment/list")
dy.get('目标链接')

try:
    # 循环爬取多页数据
    for page in range(1, 4):
        # 等待网络请求
        data = dy.listen.wait()
        js_data = data.response.body
        comments = js_data["comments"]
        
        # 提取每条评论
        for index in comments:
            # 获取时间和IP
            shijian = index["create_time"]
            if "ip_label" in index:
                ip_label = index["ip_label"]
            else:
                ip_label = "未知"
            
            # 构建数据字典
            dit = {
                "时间": str(datetime.fromtimestamp(shijian)),
                "名字": index["user"]["nickname"],
                "地区": ip_label,
                "内容": index["text"]
            }
            all_data.append(dit)
            print(dit)
            
            # 滚动页面加载更多
            tmp = dy.ele('css:.ETuXBjRi')
            dy.scroll.to_see(tmp)
        
        time.sleep(1)
    
    # 保存UTF-8格式CSV
    with open('data.csv', mode='w', encoding='utf-8', newline='') as f:
        csv_data = csv.DictWriter(f, fieldnames=['时间', '名字', '地区', '内容'])
        csv_data.writeheader()
        csv_data.writerows(all_data)
    
    # 保存GBK格式CSV（清理特殊字符）
    def clean_text_for_gbk(text):
        """清理文本，移除GBK不支持的特殊字符"""
        if not isinstance(text, str):
            return text
        cleaned = ''.join(char for char in text if ord(char) < 0x10000 and char not in ['➖', '➕', '✨', '🔥', '❤️', '💕', '👍', '🎉', '🎊', '💯'])
        return cleaned
    
    cleaned_data = []
    for item in all_data:
        cleaned_item = {
            "时间": item["时间"],
            "名字": clean_text_for_gbk(item["名字"]),
            "地区": clean_text_for_gbk(item["地区"]),
            "内容": clean_text_for_gbk(item["内容"])
        }
        cleaned_data.append(cleaned_item)
    
    with open('抖音.csv', mode='w', encoding='gbk', newline='') as f_gbk:
        csv_data_gbk = csv.DictWriter(f_gbk, fieldnames=['时间', '名字', '地区', '内容'])
        csv_data_gbk.writeheader()
        csv_data_gbk.writerows(cleaned_data)
    
    print(f"数据采集完成！共采集 {len(all_data)} 条评论")
    print("已保存为 data.csv (UTF-8格式)")
    print("已保存为 抖音.csv (GBK格式)")

except Exception as e:
    print(f"程序出错: {e}")
    # 如果出错，将已采集的数据保存
    if all_data:
        with open('data.csv', mode='w', encoding='utf-8', newline='') as f:
            csv_data = csv.DictWriter(f, fieldnames=['时间', '名字', '地区', '内容'])
            csv_data.writeheader()
            csv_data.writerows(all_data)
        print(f"已保存部分数据到 data.csv，共 {len(all_data)} 条")

finally:
    time.sleep(10)
    # 关闭浏览器
    dy.close()
    print("已关闭浏览器")
```

## 核心技术点

### 1. DrissionPage框架
```python
# 获取最新标签页
dy = Chromium().latest_tab

# 启动网络监听
dy.listen.start("/comment/list")

# 访问目标页面
dy.get('URL')

# 等待网络请求
data = dy.listen.wait()

# 获取响应体
js_data = data.response.body

# 查找元素
tmp = dy.ele('css:.ETuXBjRi')

# 滚动到元素
dy.scroll.to_see(tmp)
```

### 2. 时间戳转换
```python
from datetime import datetime

# 将时间戳转换为可读格式
datetime.fromtimestamp(1705323025).strftime('%Y-%m-%d %H:%M:%S')
```

### 3. CSV文件读写
```python
import csv

# 写入CSV
with open('file.csv', mode='w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['字段1', '字段2'])
    writer.writeheader()
    writer.writerows(data_list)
```

### 4. 特殊字符清理
```python
def clean_text_for_gbk(text):
    """清理文本，移除GBK不支持的特殊字符"""
    if not isinstance(text, str):
        return text
    # 移除emoji和其他特殊字符
    cleaned = ''.join(char for char in text if ord(char) < 0x10000)
    return cleaned
```

## 常见问题

### Q1: 程序运行失败，提示找不到Chromium？
**A:** DrissionPage需要Chromium浏览器驱动。首次运行时会自动下载，或者手动下载Chromium并配置路径。

### Q2: 爬取不到评论数据？
**A:** 可能的原因：
- 链接格式不正确
- 需要登录才能查看评论
- 网络监听接口发生变化（抖音可能更新了接口）
- 页面加载超时

### Q3: 数据量很少，每页只有几条评论？
**A:** 这与抖音的评论显示机制有关。可以尝试：
- 增加爬取页数
- 调整 `time.sleep(1)` 的等待时间
- 等待页面完全加载后再采集

### Q4: 打开CSV文件中文乱码？
**A:** 使用 `抖音.csv`（GBK格式），或在Excel中选择UTF-8编码打开 `data.csv`。

### Q5: 如何导出为Excel文件？
**A:** 可以使用pandas库：
```python
import pandas as pd

# 读取CSV
df = pd.read_csv('data.csv', encoding='utf-8')

# 导出为Excel
df.to_excel('data.xlsx', index=False, encoding='utf-8')
```

### Q6: 程序运行很慢？
**A:** 可以优化：
- 减少页数
- 调整等待时间
- 使用更快的网络环境
- 关闭不必要的浏览器扩展

## 高级功能扩展

### 1. 添加用户输入功能
```python
# 让用户输入链接和页数
url = input("请输入抖音链接: ")
pages = int(input("请输入爬取页数: "))

dy.get(url)
for page in range(1, pages + 1):
    # ...
```

### 2. 添加代理支持
```python
# 配置浏览器使用代理
co = ChromiumOptions()
co.add_argument('--proxy-server=http://代理地址:端口')
dy = Chromium(co=co).latest_tab
```

### 3. 添加数据去重
```python
# 在保存前去重
unique_data = []
seen = set()
for item in all_data:
    key = (item['名字'], item['内容'])
    if key not in seen:
        seen.add(key)
        unique_data.append(item)
```

### 4. 添加数据统计
```python
# 统计信息
print(f"总评论数: {len(all_data)}")
print(f"独立用户数: {len(set(item['名字'] for item in all_data))}")
print(f"IP覆盖地区数: {len(set(item['地区'] for item in all_data))}")
```

## 注意事项

1. **合法使用**：请遵守抖音的用户协议和相关法律法规
2. **频率控制**：避免短时间内大量请求，以免被限制
3. **数据用途**：采集的数据仅用于个人学习和研究
4. **隐私保护**：不要泄露用户的个人信息
5. **代码维护**：抖音页面可能更新，需要及时调整代码

## 技术支持

如有问题或建议，欢迎交流反馈。

## 版本历史

- **v1.0** (当前版本)
  - 基础评论爬取功能
  - UTF-8和GBK双格式导出
  - 特殊字符清理
  - 错误处理机制

## 许可证

本项目仅供学习和研究使用，请勿用于商业用途。

---

**祝使用愉快！** 🎉
