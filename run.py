# -*- coding: utf-8 -*-
# @Time    : 2018/9/10 11:42
# @Author  : HoPGoldy

from HaoHuoSearch import HaoHuo, get_driver, quit_driver


if __name__ == '__main__':
    driver = get_driver(mobile=True)

    haohuo = HaoHuo(driver)
    haohuo.search('卫衣')
    items_datas = haohuo.get_data()

    for index, item_data in enumerate(items_datas):
        print(f'\n[条目] 第{index + 1}条商品')
        print(f'[标题] {item_data["title"]}')
        for highlight in item_data['highlight']:
            print(f'[亮点] {highlight}')
        for addition in item_data['addition']:
            print(f'[{addition[0]}] {addition[1]}')

    quit_driver(driver)
