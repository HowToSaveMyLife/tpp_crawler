# -*-coding:utf-8 -*-
import selenium.webdriver as webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import json
from config import *
from bs4 import BeautifulSoup

def test_elements_judge(xpath):
    try:
        # use explicit wait to check element
        element = WebDriverWait(wd, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        print("元素存在:", element)
        return True
    except:
        print("元素不存在")
        return False

def get_city_info(city_element):
    """get city info"""
    try:
        city_name = city_element.text
        # get other possible attributes
        city_id = city_element.get_attribute('data-id')
        return {
            'name': city_name,
            'id': city_id
        }
    except Exception as e:
        print(f"获取城市信息失败: {str(e)}")
        return None

def save_cinemas_data(cinemas, city_name):
    """save cinema data to file, even if no cinema"""
    try:
        # create data directory
        os.makedirs('data', exist_ok=True)
        
        # process filename
        filename = "".join(x for x in city_name if x.isalnum() or x in (' ', '-', '_'))
        filepath = os.path.join('data', f'{filename}.json')
        
        # save as json format
        data = {
            "city_name": city_name,
            "cinema_count": len(cinemas),
            "cinemas": cinemas
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"成功保存城市 {city_name} 的影院数据到 {filepath}")
        return True
    except Exception as e:
        print(f"保存城市 {city_name} 数据失败: {str(e)}")
        return False

def calculate_statistics():
    """calculate statistics"""
    try:
        total_cinemas = 0
        cities_with_cinemas = 0
        cities_without_cinemas = 0
        
        # iterate all json files in data directory
        for filename in os.listdir('data'):
            if filename.endswith('.json'):
                filepath = os.path.join('data', filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cinema_count = data.get('cinema_count', 0)
                    total_cinemas += cinema_count
                    if cinema_count > 0:
                        cities_with_cinemas += 1
                    else:
                        cities_without_cinemas += 1
        
        print("\n=== 统计信息 ===")
        print(f"总影院数: {total_cinemas}")
        print(f"有影院的城市数: {cities_with_cinemas}")
        print(f"无影院的城市数: {cities_without_cinemas}")
        print(f"总城市数: {cities_with_cinemas + cities_without_cinemas}")
        print("==============")
        
    except Exception as e:
        print(f"计算统计信息失败: {str(e)}")

def parse_cinema_list(page_content):
    """parse cinema list data"""
    cinemas = []
    try:
        soup = BeautifulSoup(page_content, 'html.parser')
        cinema_list = soup.find('ul', id='cinemaListUl')
        
        if cinema_list:
            for item in cinema_list.find_all('li', class_='list-item'):
                cinema_info = {}
                
                # get cinema name
                title_span = item.find('span', class_='list-title')
                if title_span:
                    cinema_info['name'] = title_span.text.strip()
                    cinema_info['id'] = title_span.get('exp', '')
                
                # get address
                address_div = item.find('div', class_='list-location')
                if address_div:
                    cinema_info['address'] = address_div.text.strip()
                
                # get data-id
                item_in = item.find('div', class_='list-item-in')
                if item_in:
                    cinema_info['data_id'] = item_in.get('data-id', '')
                
                cinemas.append(cinema_info)
                
        return cinemas
    except Exception as e:
        print(f"解析影院列表失败: {str(e)}")
        return []

# create webdriver
# change to your own webdriver path
wd = webdriver.Edge(r'e:/webdriver/msedgedriver')

try:
    # taopiaopiao
    url_target = 'https://m.taopiaopiao.com/'
    wd.get(url_target)
    
    input("等待页面加载完成后按回车继续...")
    
    # check city list first element
    first_city_xpath = '//*[@id="A"]/ul/li[1]'
    if test_elements_judge(first_city_xpath):
        print("查找城市列表，开始遍历...")
        
        # iterate all cities
        cities_data = []
        for letter in range(ord('A'), ord('Z') + 1):
            letter_char = chr(letter)
            index = 1
            
            while True:
                city_xpath = f'//*[@id="{letter_char}"]/ul/li[{index}]'
                try:
                    # use explicit wait to find element
                    city_element = WebDriverWait(wd, 3).until(
                        EC.presence_of_element_located((By.XPATH, city_xpath))
                    )
                    
                    print(f"找到城市: {city_xpath}")
                    
                    # get city info
                    city_info = get_city_info(city_element)
                    if city_info:
                        cities_data.append(city_info)
                    
                    # click city
                    try:
                        # use javascript to click, more reliable
                        wd.execute_script("arguments[0].click();", city_element)
                        print(f"click city: {city_info['name'] if city_info else city_xpath}")
                        time.sleep(2)
                        
                        # check cinema list
                        try:
                            # use short wait time to check cinema list
                            cinema_list = WebDriverWait(wd, 3).until(
                                EC.presence_of_element_located((By.ID, "cinemaListUl"))
                            )
                            page_content = cinema_list.get_attribute("outerHTML")
                            
                            # parse and save cinema data
                            if city_info and 'name' in city_info:
                                cinemas = parse_cinema_list(page_content)
                                save_cinemas_data(cinemas, city_info['name'])  # save even if no cinema
                                if not cinemas:
                                    print(f"城市 {city_info['name']} 没有找到影院数据")
                        except:
                            print(f"城市 {city_info['name'] if city_info else city_xpath} 没有影院列表")
                            if city_info and 'name' in city_info:
                                save_cinemas_data([], city_info['name'])  # save empty cinema list
                        
                        # back to previous page
                        try:
                            city_selector = WebDriverWait(wd, 10).until(
                                EC.presence_of_element_located((By.XPATH, '//*[@id="J_citySelector"]'))
                            )
                            wd.execute_script("arguments[0].click();", city_selector)
                            print("点击城市选择器返回")
                            time.sleep(2)
                        except Exception as e:
                            print(f"点击城市选择器失败: {str(e)}")
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
    try:
        calculate_statistics()
    except Exception as e:
        print(f"统计失败: {str(e)}")
    wd.quit()
