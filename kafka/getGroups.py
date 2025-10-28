import requests
import json
import re

# 定义请求的URL和请求头
url = 'http://35.46.5.44:19090/api/v1/rules?type=alert'
headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Connection': 'keep-alive',
    'Referer': 'http://35.46.5.44:19090/alerts?search=',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0'
}
cookies = {
    'grafana_session': '66e4eda050bd00d3ae584607cc0281a1'
}

try:
    # 发送请求，忽略SSL验证
    response = requests.get(url, headers=headers, cookies=cookies, verify=False)
    response.raise_for_status()  # 检查请求是否成功

    # 解析响应的JSON数据
    data = response.json()
    pattern = r"消费者组\s+(\S+)"
    # 提取指定路径的数据
    summary_value = data['data']['groups'][6]['rules'][1]['alerts']
    # 定义一个[]列表，用于存储匹配到的内容 topic=ihs_data_v2x_traffic_participants
    result = []
    for item in summary_value:
        if item['labels']['topic'] == 'ihs_data_v2x_traffic_participants':
            match = re.search(pattern, item['annotations']['description'])
            # 定义一个空字符串来存储结果
            result.append(match.group(1))
           

    # 打印结果
    print(result)
    # 去除result中重复的元素
    result = list(set(result))
    print(result)
    resultStr = ""
    for item in result:
       # 存储匹配到的内容
        resultStr += f"kafka-consumer-groups.sh --bootstrap-server bigdata02:9092 --delete --group {item} \n"
        print(resultStr)
        with open('clean.sh', 'a') as f:
            f.write(resultStr)

except requests.RequestException as e:
    print(f"请求出错: {e}")
except (KeyError, IndexError) as e:
    print(f"数据解析出错: {e}")
except json.JSONDecodeError as e:
    print(f"JSON解析出错: {e}")
