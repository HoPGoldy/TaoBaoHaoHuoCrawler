# -*- coding: utf-8 -*-
# @Time    : 2018/9/10 11:42
# @Author  : HoPGoldy

from HaoHuoSearch import HaoHuo, get_driver, quit_driver


if __name__ == '__main__':
    driver = get_driver(mobile=True)

    haohuo = HaoHuo(driver)
    materials = haohuo.search_material('糖力')

    for material in materials:
        print(material)

    quit_driver(driver)
