from playwright.sync_api import sync_playwright
from selectolax.parser import HTMLParser
from sys import exit
import time
import requests
import subprocess
import os
import string
from RAP_email import EmailVerificator, create_login, get_domains
import random
import argparse


def generate_password():
    valid_chars = string.ascii_letters + string.digits + string.punctuation.replace(':','')
    return ''.join(random.choice(valid_chars) for _ in range(12))



def export_audio(audio_url):
    res = requests.get(audio_url)
    return res.content

def convert_speech_to_text(whisper_path, audio_file, transcribe_path):
    subprocess.getoutput(f"{whisper_path} {audio_file} --output_dir {transcribe_path} --output_format txt")


class AccountCreator():

    def __init__(self, path:str, email_ver:bool, api:bool, proxies:str, delay:int, nsfw:bool, *args, **kwargs) -> None:
        self.username = ''
        self.password = generate_password()
        self.login = create_login()
        self.domain = random.choice(get_domains())
        self.email = f'{self.login}@{self.domain}'
        self.path = path
        self.email_ver = email_ver
        self.api = api
        self.proxies = proxies
        self.delay = delay
        self.nsfw = nsfw
        self.verificator = EmailVerificator(login=self.login, domain=self.domain)

    def run(self):
        while True:
            with sync_playwright() as playwright:
                loops = 1
                proxy_context = None
                proxy_browser = None
                if self.proxies != '':
                    with open(f'{self.proxies}', encoding='utf-8') as pfile:
                        proxy_list = [proxy.strip() for proxy in pfile.readlines()]
                    loops = len(proxy_list)
                    proxy_browser = {"server": "per-context"}
                for loop in range(loops):
                    if self.proxies != '':
                        server = ':'.join(proxy_list[loop].split(':')[:2])
                        proxy_username = proxy_list[loop].split(':')[2]
                        proxy_password = proxy_list[loop].split(':')[3]
                        proxy_context = {
                            "server": server,
                            "username": proxy_username,
                            "password": proxy_password
                        }
                    print('Running browser.', flush=True)
                    browser = playwright.chromium.launch(headless=True, proxy=proxy_browser)
                    context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 OPR/97.0.0.0',
                        proxy=proxy_context)
                    page = context.new_page()
                    page.goto('https://www.reddit.com/account/register/')
                    page.fill('input[id="regEmail"]', value=self.email)
                    time.sleep(1.23)
                    page.click('button[type="submit"]')
                    page.wait_for_load_state()
                    self.username = page.locator('a[class="Onboarding__usernameSuggestion"]').first.get_attribute('data-username')
                    page.fill('input[id="regUsername"]', value=self.username)
                    page.fill('input[id="regPassword"]', value=self.password)
                    time.sleep(0.25)
                    page.wait_for_selector('fieldset[id="g-recaptcha"]')
                    time.sleep(2)
                    page.click('iframe[title="reCAPTCHA"]')
                    time.sleep(2.49)
                    page.frames[-1].click('button[id="recaptcha-audio-button"]')
                    captcha_url = page.frames[-1].locator('div[class="rc-audiochallenge-tdownload"]').locator('a').get_attribute('href')
                    audio_content = export_audio(audio_url=captcha_url)
                    with open('captcha_audio.mp3', 'wb') as audio_file:
                        audio_file.write(audio_content)
                    print('Solving Captcha...', flush=True)
                    convert_speech_to_text(r"D:\jakub\machine_learnining\Scripts\whisper.exe", 'captcha_audio.mp3', '.')
                    with open('captcha_audio.txt', 'r') as rfile:
                        captcha_res = rfile.read()
                    os.remove('captcha_audio.txt')
                    os.remove('captcha_audio.mp3')
                    page.frames[-1].fill('input[id="audio-response"]', value=captcha_res)
                    page.frames[-1].click('button[id="recaptcha-verify-button"]')
                    page.click('button[data-step="username-and-password"]')
                    time.sleep(3)
                    key = ''
                    secret = ''
                    if self.api == True:
                        page.goto('https://www.reddit.com/prefs/apps')
                        page.wait_for_load_state()
                        page.click('button[id="create-app-button"]')
                        time.sleep(2.3)
                        page.fill('input[name="name"]', value='Personal script')
                        time.sleep(0.93)
                        page.click('input[id="app_type_script"]')
                        page.fill('textarea[name="description"]', value='giga koks')
                        page.fill('input[name="about_url"]', value='http://www.example.com/')
                        time.sleep(0.43)
                        page.fill('input[name="redirect_uri"]',value='http://www.example.com/')
                        page.locator('div[class="edit-app-form"]').locator('button[type="submit"]').click()
                        time.sleep(1.25)
                        tree = HTMLParser(page.content())
                        key = tree.css_first('div[id="developed-apps"]').css('h3')[-1].text()
                        secret = tree.css_first('div[id="developed-apps"]').css_first('td[class="prefright"]').text()
                    if self.nsfw == True:
                        page.goto('https://www.reddit.com/settings/feed')
                        page.locator('div[id="AppRouter-main-content"]').locator('div[class="_2f63as5b5FASHMqGd5P1o0 "]').locator(
                            'div[class="_1kylDjSQ2hay_ez0zF7BEP"]'
                        ).locator('button').nth(0).click()
                        time.sleep(5)
                    if self.email_ver == True:
                        time.sleep(5)
                        page.goto(self.verificator.get_verify_account_link())
                    with open(f'{self.path.split(" ")[0]}.txt', 'a') as file:
                        file.write(f'\n{self.username}:{self.password}:{self.email}:{key}:{secret}:email_verified={self.email_ver}:allowed_nsfw_content={self.nsfw}')
                    context.close()
                    print('Account created', flush=True)
                    print(f'Sleeping for {self.delay/60} minutes')
                    browser.close()
                    time.sleep(self.delay)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='RAP account creator',
        description='Reddit account creator for Reddit Automated Package.'
    )
    parser.add_argument('filename', metavar='filename', type=str,
                         help='Nazwa pliku (lub ścieżka z nazwą na końcu), w którym zostaną umieszone dane')
    parser.add_argument('-v', required=False, default=False, action='store_true', help='Email verify created accounts.')
    parser.add_argument('-a', required=False, default=False, action='store_true', help='Give created accounts access to Reddit api.')
    parser.add_argument('-p', required=False, default='',type=str, help='Give created accounts access to Reddit api.')
    parser.add_argument('-d', required=False, default=5, type=int, help='Delay between account creation in minutes.')
    parser.add_argument('-n', required=False, default=False, action='store_true', help='Delay between account creation in minutes.')
    bot_params = vars(parser.parse_args())
    bot_params['d'] = bot_params['d'] * 60
    bot = AccountCreator(*bot_params.values())
    try:
        bot.run()
    except KeyboardInterrupt:
        exit()


#path:str, email_ver:bool, api:bool, proxies:str, delay:int, nsfw:bool