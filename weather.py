import time
import requests

_head = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3423.2 Safari/537.36"
}

_api = "https://www.sojson.com/open/api/weather/json.shtml?city=%s"


class Weather():

    def __init__(self, address):
        self.address = address
        self.weather = self.format_weather()

    def link_api(self, address):
        count = 0
        while True:
            res = requests.get(_api % address, headers=_head, timeout=10)
            count += 1
            if res.status_code == 200:
                return res.json()
            if count > 5:
                return None
            time.sleep(4)

    def format_weather(self):
        source = self.link_api(self.address)
        if source is None:
            return None
        weather_dict = {
            "今日天气": source["data"]["forecast"][0]["type"],
            "平均温度": source["data"]["wendu"],
            "最高温度": source["data"]["forecast"][0]["high"],
            "最低温度": source["data"]["forecast"][0]["low"],
            "湿度": source["data"]["shidu"],
            "PM2.5": source["data"]["pm25"],
            "空气质量": source["data"]["quality"],
            "风力": source["data"]["forecast"][0]["fl"],
            "风向": source["data"]["forecast"][0]["fx"]
        }
        return weather_dict

    def get_weather(self):
        return self.weather


if __name__ == "__main__":

    """以下是实验"""

    data = Weather("成都")
    print(data.weather)

    dictionary = {'city': '成都', 'date': '20180526', 
    'data': 
    {'ganmao': '儿童、老年人及心脏、呼吸系统疾病患者人群应减少长时间或高强度户外锻炼', 'pm25': 33.0, 'wendu': '24', 'quality': '轻度污染', 'pm10': 63.0, 
    'yesterday': 
    {'aqi': 118.0,'notice': '阴晴之间，谨防紫外线侵扰', 'date': '25日星期五', 'low': '低温 18.0℃', 'sunset': '19:57', 'fx': '无持续风向', 'type': '多云', 'fl': '<3级', 'sunrise': '06:05', 'high': '高温 29.0℃'}, 
    'forecast': 
    [
        {'aqi': 54.0, 'notice': '雨虽小，注意保暖别感冒', 'date': '26日星期六', 'low': '低温 17.0℃', 'sunset': '19:57', 'fx': '无持续风向', 'type': '小雨', 'fl': '<3级', 'sunrise': '06:04', 'high': '高温 26.0℃'}, 
        {'aqi': 58.0, 'notice': '阴晴之间，谨防紫外线侵扰', 'date': '27日星期日', 'low': '低温 16.0℃', 'sunset': '19:58', 'fx': '无持续风向', 'type': '多云', 'fl': '<3级', 'sunrise': '06:04', 'high': '高温 29.0℃'}, 
        {'aqi': 66.0, 'notice': '阴晴之间，谨防紫外线侵扰', 'date': '28日星期一', 'low': '低温 17.0℃', 'sunset': '19:59', 'fx': '无持续风向', 'type': '多云', 'fl': '<3级', 'sunrise': '06:04', 'high': '高温 28.0℃'}, 
        {'aqi': 71.0, 'notice': '阴晴之间，谨防紫外线侵扰', 'date': '29日星期二', 'low': '低温 17.0℃', 'sunset': '19:59', 'fx': '无持续风向', 'type': '多云', 'fl': '<3级', 'sunrise': '06:03', 'high': '高温 27.0℃'}, 
        {'aqi': 68.0, 'notice': '阴晴之间，谨防紫外线侵扰', 'date': '30日星期三', 'low': '低温 18.0℃', 'sunset': '20:00', 'fx': '无持续风向', 'type': '多云', 'fl': '<3级', 'sunrise': '06:03', 'high': '高温 25.0℃'}
        ],
    'shidu': '78%'}, 'status': 200, 'message': 'Success !', 'count': 1102}


