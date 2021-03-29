from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.request import Request
from bs4 import BeautifulSoup as soup
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.ui as ui
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from .models import Messages
from . import db

login_url = 'https://www.instagram.com/accounts/login/'
url = 'https://www.instagram.com/'
DRIVER_PATH = 'chromedriver'
options = Options()
options.headless = False
options.add_argument("--window-size=1920,1200")

# credentials
username = 'tldr_future'
password = 'bo$J@$5865'


def get_page_information():
    # creating database instance for sqlite
    # conn = sqlite3.connect('InstagramChats.sqlite')
    # cur = conn.cursor()

    # cur.execute('CREATE TABLE Chats (username VARCHAR, messages VARCHAR)')
    # cur.execute('CREATE TABLE IF NOT EXISTS Chats (username VARCHAR, messages VARCHAR)')
    # conn.commit()

    try:
        # scrapping starts here
        driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
        driver.get(login_url)
        time.sleep(1)

        # click accept cookies
        try:
            # action chain for login button
            cookie_button = ActionChains(driver)
            cookie_button.click(
                driver.find_element_by_xpath('/html/body/div[2]/div/div/div/div[2]/button[1]')).perform()
            time.sleep(2)
        except:
            print("cookie not exists")

        # action chain for login button
        login_btn = ActionChains(driver)
        # enter username
        driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[1]/div/label/input').send_keys(username)
        # enter password
        driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[2]/div/label/input').send_keys(password)
        # click login button
        login_btn.click(driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[3]/button')).perform()

        # driver.get(url)
        time.sleep(3)
        # save info button click
        try:
            save_info = ActionChains(driver)
            save_info.click(
                driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/div/div/button')).perform()
            time.sleep(3)
        except:
            print('continue')
        # notification button click
        try:
            notification_btn = ActionChains(driver)
            notification_btn.click(
                driver.find_element_by_xpath('/html/body/div[4]/div/div/div/div[3]/button[2]')).perform()
        except:
            print("continue")
        # message button click
        notification_btn = ActionChains(driver)
        notification_btn.click(
            driver.find_element_by_xpath(
                '//*[@id="react-root"]/section/nav/div[2]/div/div/div[3]/div/div[2]/a')).perform()

        time.sleep(5)
        html = driver.page_source
        data_soup = soup(html, 'html.parser')
        # print(data_soup)
        # print('\n\n\n')
        # number of conversations in total
        chats = data_soup.find('div', {'class': 'N9abW'})
        chat_thread_length = len(chats.findAll('div', {'class': 'DPiy6 Igw0E IwRSH eGOV_ _4EzTm'}))

        print(str(chat_thread_length))
        for chat in range(1, chat_thread_length + 1):
            print(chat)

            # click on each message thread
            message_click = ActionChains(driver)
            message_click.click(driver.find_element_by_xpath(
                '//*[@id="react-root"]/section/div/div[2]/div/div/div[1]/div[3]/div/div/div/div/div[' + str(
                    chat) + ']')).perform()
            time.sleep(3)

            html = driver.page_source
            data_soup = soup(html, 'html.parser')
            # print(data_soup)

            messages_thread = data_soup.find('div', {'class': 'VUU41'})
            # length of messages inside message thread
            message_thread_length = len(messages_thread.findAll('div', {'class': 'Igw0E Xf6Yq eGOV_ ybXk5 _4EzTm'}))
            print(str(message_thread_length))

            # scroll message thread till top to get all messages
            # Wait until chat is loaded
            WebDriverWait(driver, 15).until(ec.presence_of_element_located((By.CLASS_NAME, 'VUU41')))

            # Set initial scroll y
            scroll_y = __scroll_position(driver)

            # Scroll until beginning
            while scroll_y != 0:
                __scroll_to_top(driver)
                # Wait for loader to show and hide
                loader_xpath = '//div[@style="height: 72px;"]'
                WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.XPATH, loader_xpath)))
                while True:
                    try:
                        WebDriverWait(driver, 5).until_not(ec.presence_of_element_located((By.XPATH, loader_xpath)))
                    except:
                        break
                # Set new scroll y
                scroll_y = __scroll_position(driver)
                # print('to reach top: ', scroll_y)

            # if reached to top
            time.sleep(4)
            html = driver.page_source
            data_soup_ = soup(html, 'html.parser')
            # name of chatting profile
            chat_name = driver.find_element_by_xpath(
                '//*[@id="react-root"]/section/div/div[2]/div/div/div[2]/div[1]/div/div/div[2]/div/div[2]/button/div/div/div').text
            print("name: " + chat_name)
            # print(data_soup)

            messages_thread_ = data_soup_.find('div', {'class': 'VUU41'})
            # length of messages inside message thread
            new_length = len(messages_thread_.findAll('div', {'class': 'Igw0E Xf6Yq eGOV_ ybXk5 _4EzTm'}))
            print(str(new_length))

            # print(message_boxes)

            # getting all messages from thread
            for message in messages_thread_.findAll('div', {'class': 'Igw0E Xf6Yq eGOV_ ybXk5 _4EzTm'}):
                # message = message.find('div', {'class': 'DMBLb'})
                # print(message.text)
                params = (chat_name, message.text)
                new_messages = Messages(username=params[0], content=params[1])
                db.session.add(new_messages)
                db.session.commit()
            print('\n\n\n')
        conn.close()
    except:
        print('exception in thread.. trying again')
        get_page_information()

    # here if you want to run after 5 minutes.. un comment following code and it will run
    # time.sleep(300)
    # get_page_information()


def __scroll_position(driver):
    return driver.execute_script('''return document.querySelector('div[class="JiVIq _0NM_B"]')
    .firstChild.firstChild.scrollTop''')


def __scroll_to_top(driver):
    driver.execute_script('''document.querySelector('div[class="JiVIq _0NM_B"]')
    .firstChild.firstChild.scrollTo(0,0)''')

# if __name__ == '__main__':

# get_page_information()
