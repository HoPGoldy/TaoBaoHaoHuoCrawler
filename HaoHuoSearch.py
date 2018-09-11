# -*- coding: utf-8 -*-
# @Time    : 2018/9/10 10:36
# @Author  : HoPGoldy

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time

CHROME_DRIVER_PATH = 'D:\SOFTWARE\Google\Chrome\Application\chromedriver.exe'


class HaoHuo:
    _search_url = 'https://market.m.taobao.com/apps/youhaohuo/index/tag.html?wh_weex=true&type=search&key='
    _item_loc = (By.XPATH, '/html/body/div/div/div[*]/div[*]')
    # title在列表页查找，所以下面的xpath是基于_item_loc的
    _item_title_loc = (By.XPATH, 'div[2]/span')
    # 下列内容均在详情页进行查找
    _highlight_locs = [
        (By.XPATH, '//*[@id="rx-block"]/div[5]/div/div[*]/span'),
        (By.XPATH, '//*[@id="rx-block"]/div[6]/div/div[2]/div[*]/span')
    ]
    _addition_locs = {
        'first': [
            (By.XPATH, '//*[@id="rx-block"]/div[7]/div/div[2]/span'),
            (By.XPATH, '//*[@id="rx-block"]/div[9]/div/div/div[1]/span'),
            (By.XPATH, '//*[@id="rx-block"]/div[8]/div/div/div[1]/span'),
            (By.XPATH, '//*[@id="rx-block"]/div[6]/div/div/span')
        ],
        'second': [
            (By.XPATH, '//*[@id="rx-block"]/div[8]/div/div[2]/span'),
            (By.XPATH, '//*[@id="rx-block"]/div[13]/div/div/div[1]/span')
        ],
        'third': [
            (By.XPATH, '//*[@id="rx-block"]/div[9]/div/div[2]/span'),
            (By.XPATH, '//*[@id="rx-block"]/div[17]/div/div/div[1]/span')
        ]
    }
    _addition_title_locs = {
        'first': [
            (By.XPATH, '//*[@id="rx-block"]/div[7]/div/div[1]/span'),
            (By.XPATH, '//*[@id="rx-block"]/div[6]/div/div/div[1]/span'),
            (By.XPATH, '//*[@id="rx-block"]/div[6]/div/div/div[1]/span')
        ],
        'second': [
            (By.XPATH, '//*[@id="rx-block"]/div[8]/div/div[1]/span'),
            (By.XPATH, '//*[@id="rx-block"]/div[10]/div/div/div[1]/span')
        ],
        'third': [
            (By.XPATH, '//*[@id="rx-block"]/div[9]/div/div[1]/span'),
            (By.XPATH, '//*[@id="rx-block"]/div[14]/div/div/div[1]/span')
        ]
    }

    items = []

    def __init__(self, selenium_driver):
        self._driver = selenium_driver

    def search(self, keyword):
        self._driver.get(self._search_url + keyword)
        items = self._find_elements(self._item_loc)

        self.items = items[:-1]
        return len(items[:-1])

    def set_num(self, num):
        items = self.items
        if num < len(items):
            self.items = items[:num]
        return len(self.items)

    def get_title(self):
        items = self.items
        if items is None:
            print('[名称] 商品列表为空，无法获取')
            return None

        titles = []
        for item in items:
            item.find_element(self._item_title_loc[0], self._item_title_loc[1])

            titles.append(item.text.split('\n')[0])
        return titles

    def search_material(self, keyword, num=1):
        materials = []

        self.search(keyword)
        items = self.items
        item_len = len(items)

        for index, item in enumerate(items):
            sys.stdout.write(f'\r[品牌故事] 正在检索第{index + 1}/{item_len}个条目')
            sys.stdout.flush()
            self.items = [item]
            items_additions = self.get_addition(log_mode=False)
            if len(items_additions) > 0:
                item_additions = items_additions[0]
            else:
                break

            for addition in item_additions:
                if '品牌' in addition[0]:
                    materials.append(addition[1])
            if len(materials) >= num:
                break
        sys.stdout.write('                        \r[品牌故事] 检索完成\n')
        sys.stdout.flush()

        return materials

    # 获取亮点
    def get_highlight(self, log_mode=True):
        items = self.items
        if items is None:
            print('[亮点] 商品列表为空，无法获取')
            return None

        return self._open_items(items, log_mode, self._get_highlight)

    def _get_highlight(self):
        for highlight_loc in self._highlight_locs:
            highlight_elements = self._find_elements(highlight_loc)
            if highlight_elements is not None:
                # print(f'[亮点] {[highlight.text for highlight in highlight_elements]}')
                return [highlight.text for highlight
                        in highlight_elements
                        if ('好在哪里' not in highlight.text)]
        # print('[亮点] 未成功解析出亮点')
        return []

    # 获取设计亮点
    def get_addition(self, log_mode=True):
        items = self.items
        if items is None:
            print('[设计亮点] 商品列表为空，无法获取')
            return None

        return self._open_items(items, log_mode, self._get_addition)

    def _get_addition(self):
        result = []
        # 依次取出第一、二、三个补充的locs
        for key in self._addition_locs:
            addition_locs = self._addition_locs[key]

            # 从对应补充里取出loc
            for index, addition_loc in enumerate(addition_locs):
                addition_element = self._find_element(addition_loc)

                # 如果是单品
                if addition_element is not None and key == 'first' and index == 3:
                    # print(f'[单品] {addition_element.text}')
                    result.append(('单品', addition_element.text))
                    break
                # 不是单品
                elif addition_element is not None:
                    # 获取其标题
                    title_element = self._find_element(self._addition_title_locs[key][index])
                    # print(f'[{title_element.text}] {addition_element.text}')
                    result.append((title_element.text, addition_element.text))
                    break

            # 如果是单品则不再找第二第三个补充
            if len(result) > 0 and result[0][0] == '单品':
                break

        return result

    def get_data(self, log_mode=True):
        items = self.items
        if items is None:
            print('[全部资料] 商品列表为空，无法获取')
            return None

        titles = self.get_title()
        items_data = [{
            'title': title,
            'highlight': [],
            'addition': []
        } for title in titles]
        contents = self._open_items(items, log_mode, self._get_highlight, self._get_addition)

        for i in range(len(items_data)):
            items_data[i]['highlight'] = contents[i][0]
            items_data[i]['addition'] = contents[i][1]

        return items_data

    def _open_items(self, items, log_mode=True, *get_info_funcs):
        result = []
        item_len = len(items)

        for index, item in enumerate(items):
            if log_mode:
                sys.stdout.write(f'\r[收集器] 正在收集第{index + 1}/{item_len}个条目')
                sys.stdout.flush()
            item.click()

            while True:
                handles = self._driver.window_handles
                if len(handles) > 1:
                    break
                else:
                    time.sleep(1)

            self._driver.switch_to.window(handles[1])

            if len(get_info_funcs) == 1:
                func = get_info_funcs[0]
                result.append(func())
            else:
                item_data = []
                for func in get_info_funcs:
                    item_data.append(func())
                result.append(item_data)

            self._driver.close()
            self._driver.switch_to.window(handles[0])
        if log_mode:
            sys.stdout.write('                        \r[收集器] 收集完成\n')
            sys.stdout.flush()
        return result

    # 查找元素
    def _find_element(self, loc, delay_time=0.5):
        try:
            element = WebDriverWait(self._driver, delay_time).until(
                EC.presence_of_element_located(loc)
            )
            return element
        except exceptions.TimeoutException:
            return None

    def _find_elements(self, loc, delay_time=0.5):
        try:
            elements = WebDriverWait(self._driver, delay_time).until(
                EC.presence_of_all_elements_located(loc)
            )
            return elements
        except exceptions.TimeoutException:
            return None

    # 切换框架
    def _switch_frame(self, loc):
        # print(f'将框架切换至{loc}')
        if loc == 'default_content':
            return self._driver.switch_to.default_content()
        else:
            return self._driver.switch_to.frame(loc)


# 启动chrome
def get_driver(headless=False, mobile=False):
    print('[系统] 正在启动chrome')
    start_option = webdriver.ChromeOptions()
    if headless:
        start_option.set_headless()
    if mobile:
        mobile_emulation = {'deviceName': 'Nexus 6P'}
        start_option.add_experimental_option('mobileEmulation', mobile_emulation)
    try:
        driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=start_option)
        print('[系统] 启动成功')
        return driver
    except exceptions.WebDriverException:
        print('[系统] 启动失败')


# 退出chrome
def quit_driver(driver):
    print('[系统] 正在关闭chrome')
    driver.quit()
    print('[系统] 关闭完成')