# -*-coding:utf-8 -*-
import selenium.webdriver as webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_elements_judge(xpath):
    try:
        # 使用显式等待检查元素是否存在
        element = WebDriverWait(wd, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        print("元素存在:", element)
        return True
    except:
        print("元素不存在")
        return False

def get_city_info(city_element):
    """获取城市信息"""
    try:
        city_name = city_element.text
        # 获取其他可能的属性
        city_id = city_element.get_attribute('data-id')
        return {
            'name': city_name,
            'id': city_id
        }
    except Exception as e:
        print(f"获取城市信息失败: {str(e)}")
        return None

# 创建浏览器实例
wd = webdriver.Edge(r'e:/webdriver/msedgedriver')

try:
    # 访问淘票票
    url_target = 'https://m.taopiaopiao.com/'
    wd.get(url_target)
    
    input("等待页面加载完成后按回车继续...")
    
    # 检查城市列表第一个元素是否存在
    first_city_xpath = '//*[@id="A"]/ul/li[1]'
    if test_elements_judge(first_city_xpath):
        print("找到城市列表，开始遍历...")
        
        # 遍历所有城市
        cities_data = []
        for letter in range(ord('A'), ord('Z') + 1):
            letter_char = chr(letter)
            index = 1
            
            while True:
                city_xpath = f'//*[@id="{letter_char}"]/ul/li[{index}]'
                try:
                    # 使用显式等待查找元素
                    city_element = WebDriverWait(wd, 3).until(
                        EC.presence_of_element_located((By.XPATH, city_xpath))
                    )
                    
                    print(f"找到城市: {city_xpath}")
                    
                    # 获取城市信息
                    city_info = get_city_info(city_element)
                    if city_info:
                        cities_data.append(city_info)
                    
                    # 点击城市
                    try:
                        # 使用JavaScript点击，更可靠
                        wd.execute_script("arguments[0].click();", city_element)
                        print(f"点击城市: {city_info['name'] if city_info else city_xpath}")
                        time.sleep(2)
                        
                        # 获取当前页面内容
                        page_content = wd.find_element(By.XPATH, "//*").get_attribute("outerHTML")
                        print(f"当前页面内容长度: {len(page_content)}")
                        
                        # 这里可以添加解析页面内容的代码
                        
                        # 使用城市选择器按钮返回
                        try:
                            city_selector = WebDriverWait(wd, 10).until(
                                EC.presence_of_element_located((By.XPATH, '//*[@id="J_citySelector"]'))
                            )
                            wd.execute_script("arguments[0].click();", city_selector)
                            print("点击城市选择器返回")
                            time.sleep(2)
                        except Exception as e:
                            print(f"点击城市选择器失败: {str(e)}")
                            # 如果点击失败，使用浏览器的后退按钮
                            wd.back()
                            print("使用浏览器后退按钮")
                            time.sleep(2)
                        
                    except Exception as e:
                        print(f"点击城市失败: {str(e)}")
                    
                    index += 1
                    
                except:
                    print(f"没有找到更多{letter_char}开头的城市")
                    break
        
        print(f"共找到 {len(cities_data)} 个城市")
        
    else:
        print("未找到城市列表")
    
    input("按回车结束程序...")
    
except Exception as e:
    print(f"程序发生错误: {str(e)}")
    
finally:
    wd.quit()
