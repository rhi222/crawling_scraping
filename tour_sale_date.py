#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup  # bs4モジュールからBeautifulSoupクラスをimport
import re
import datetime
import slackweb


# summary
def get_salse_info(template):
    intl_html = get_html('https://www.jal.co.jp/tour/jalpak/index.html')
    intl_packages = scraping_pacakge_info(intl_html)
    attention_packages = pickup_package(intl_packages, template)
    dom_html = get_html('https://www.jal.co.jp/tour/jalpak/dom.html')
    dom_packages = scraping_pacakge_info(dom_html)
    attention_packages = pickup_package(dom_packages, attention_packages)
    return attention_packages


def get_html(url):
    r = requests.get(url)
    r.encoding = r.apparent_encoding
    return r.text


def scraping_pacakge_info(html):
    soup = BeautifulSoup(html, 'html.parser')
    package_details_html = (soup.find(class_='package_wrap Lbule')
                                .find_all(class_='package_detail'))
    package_array = []
    for p in package_details_html:
        package_detail = {'date': p.find(class_='date').text,
                          'time': p.find(class_='time').text,
                          'name': p.find(class_='tour_list').text.strip()}
        package_array.append(package_detail)
    return package_array


# attention_packages
def pickup_package(package_array, attention_packages):
    for p in package_array:
        if (difference_days(p['date']) == 22):
            attention_packages['7日後'].append(p)
        if (difference_days(p['date']) == 2):
            attention_packages['明日'].append(p)
        if (difference_days(p['date']) == 4):
            attention_packages['今日'].append(p)
    return attention_packages


# regexp
def regexp_date(date_text):
    pattern = re.compile(r'(\d{3,4})年(\d{1,2})月(\d{1,2})日')
    matchObj = pattern.search(date_text)
    year = matchObj.group(1)
    month = matchObj.group(2)
    date = matchObj.group(3)
    if len(year) == 3:  # jalco page上の誤植対応
        year = '2017'
    return datetime.date(int(year),
                         int(month),
                         int(date))


# date hikizan
def difference_days(date_text):
    day = regexp_date(date_text)
    today = datetime.date.today()
    return (day-today).days


# slack_contents
def create_contents(attention_packages):
    contents_list = ["*売り出し情報*"]
    for k, v in attention_packages.items():
        if (len(v) != 0):
            contents_list.append('■ ' + k + '発売')
            for pacakge in v:
                contents_list.append(pacakge['date'] + pacakge['time'])
                contents_list.append(pacakge['name'])
        contents_list.append('')

    contents_list.append("→→ <https://www.jal.co.jp/tour/jalpak/|more detail>")
    return "\n".join(contents_list)


def post_slack(slack_text):
    webhook_url = 'https://hooks.slack.com/services/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'  # noqa: E501
    slack = slackweb.Slack(url=webhook_url)
    slack.notify(channel="#zzz_nishiyama_test",
                 username="jal_bot",
                 text=slack_text,
                 icon_emoji=":ghost:")
    return


if __name__ == '__main__':
    template = {'7日後': [], '明日': [], '今日': []}
    attention_packages = get_salse_info(template)
    if (len(attention_packages['7日後']) == 0
            and len(attention_packages['明日']) == 0
            and len(attention_packages['今日']) == 0):
        print('there is no tour sales date')
    else:
        slack_text = create_contents(attention_packages)
        post_slack(slack_text)
