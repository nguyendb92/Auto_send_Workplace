import time
import logging
from sys import exit
import pandas as pd
import datetime, calendar
import argparse
import os
import pathlib

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from collections import defaultdict, deque
from itertools import zip_longest


# Account
USER = os.environ.get('USER_WORKPLACE')
PASSWORD = os.environ.get('PASS_WORKPLACE')
URL_LOGIN_WP = ''
URL_CHAT_GROUP = ""

if not USER or not PASSWORD or not URL_LOGIN_WP or not URL_CHAT_GROUP:
    raise ValueError('You need add USER, PASSWORD, URL_LOGIN_WP, URL_CHAT_GROUP')
# Config driver Selenium
# Đường dẫn cài Firefox
BINARY = r"C:\Program Files\Mozilla Firefox\firefox.exe"
EXECUTABLE = 'geckodriver.exe'

parser = argparse.ArgumentParser()
parser.add_argument("-n", "-N", "--name_worker", action="store",
                    help="the name of worker need to register on workplace")
args = parser.parse_args()

list_worker = ["huydx6", "nguyennc8", "hiepnh21", "anhlt59", "gianglmc"]
if args.name_worker and not args.name_worker.lower() in list_worker:
    raise NameError("Name of worker is invalid, please check again!")


def get_logging():

    # create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
    return logger


def webdriver_setup():
    """Setup driver Selenium."""
    options = Options()
    # options.add_argument('--headless')
    binary = FirefoxBinary(BINARY)
    driver = webdriver.Firefox(firefox_binary=binary,
                               executable_path=EXECUTABLE,
                               options=options)
    logger.debug("Setup driver finished !")
    return driver


def login(driver, logger):
    """Login ticket."""
    try:
        driver.get(URL_LOGIN)
        driver.find_element_by_id("User").send_keys(USER)
        driver.find_element_by_id("Pass").send_keys(PASSWORD)
        driver.find_element_by_id("btnLogIn").click()
        logger.debug("Login success!")
        return driver
    except Exception as e:
        logger.error('login: {}'.format(e))


def send_message(msg, dr):
    dr.get(URL_LOGIN_WP)
    dr.find_element_by_id("userNameInput").send_keys(USER)
    dr.find_element_by_id("passwordInput").send_keys(PASSWORD)
    dr.find_element_by_id("submitButton").click()
    dr.get(URL_CHAT_GROUP)
    action = ActionChains(dr)
    logger.debug("msg: %s", msg)
    for s in msg:
        action.send_keys(s).key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT)

    action.send_keys(Keys.ENTER).perform()
    logger.debug("sent message")
    time.sleep(10)


def data_to_dict(items):
    d = defaultdict(list)
    for item in items:
        date_time = datetime.datetime.strptime(item[1], '%d-%m-%Y')
        work_day = date_time.day
        if date_time.month != datetime.datetime.now().month:
            raise ValueError(f"Check your file excel invalid with: {item[1]}")
        d[work_day].append(item)
    return d


def clean_msg(msg):
    return [message.strip() for message in msg.split(',')]


def get_duty(user_name, data_user):

    data_of_one = [ele for ele in data_user if user_name.lower() in ele[-1].lower()]
    logger.debug('data_of_one: %s', data_of_one)
    return data_of_one


def get_message_user(name, data_users, msg, replacer={}, except_day=[]):
    """ name of worker,
        data_users: generator of (hour, date, name of dutiers)
        replacer = {"name": 'huydx6', 'date': '12-07-2019'}
        msg: input text to send
    """
    today = datetime.datetime.now()
    day, month, hour = today.day, today.month, today.hour
    if not isinstance(replacer, dict):
        raise ValueError(f"replacer is dict but got: {replacer}")
    if not isinstance(except_day, list):
        raise ValueError(f"replacer is list but got: {except_day}")

    today_wokers = data_users[day]
    logger.debug('today_work: %s', today_wokers)
    logger.debug('date: %s, day: %s', int(replacer['date'].split('-')[0]), day)
    if int(replacer['date'].split('-')[0]) == day:
        logger.debug('into replacer name')
        name1 = replacer["name"]
        has_duty = get_duty(name1, today_wokers)
    else:
        logger.debug('into name')
        name1 = name.lower()
        has_duty = get_duty(name1, today_wokers)
    messages = deque(msg)

    # has_duty = get_duty(name, today_wokers)
    if not has_duty:
        return None
    else:
        for item in has_duty:
            if int(item[1].split('-')[0]) in except_day:
                logger.debug('excepted: %s', item)
                continue
            logger.debug('item: %s', item)
            hour_duty = int(item[0].split(':')[0])
            logger.debug("hour_duty: %s", hour_duty)
            if hour_duty == 8 and 0 < hour < 12:
                messages.appendleft(f'Ngày: {item[1]}')
                messages.appendleft('#1')
                logger.debug(messages)
                return messages
            elif hour_duty == 17 and 14 < hour < 24:
                messages.appendleft(f'Ngày: {item[1]}')
                messages.appendleft('#2')
                logger.debug(messages)
                return messages
        return None


if __name__ == "__main__":
    logger = get_logging()
    logger.debug('Setup logger success!')
    # read file excel get duty
    df = pd.read_excel('lichtruc_team_tool_72019.xlsx', encoding='utf-8')
    name_worker = args.name_worker if args.name_worker else "NguyenNC8"
    dict_obj = data_to_dict(zip_longest(df[1], df[2], df[5]))
    input_message = "line 1, line 2, line 3"
    message = deque(clean_msg(input_message))
    x = get_message_user(name_worker, dict_obj, message, replacer={}, except_day=[])
    logger.debug('X: %s', x)
    if x:
        driver = webdriver_setup()
        logger.debug('user: %s', x)
        send_message(x, driver)
        driver.quit()
    else:
        print("Hom nay ban khong phai truc ticket !")

