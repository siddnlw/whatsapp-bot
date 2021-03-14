import json
import tkinter as tk
from io import BytesIO
from time import sleep
import chromedriver_autoinstaller
from bs4 import BeautifulSoup
from PIL import Image, ImageTk
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class WhatsappDB:
    def __init__(self):
        self.message_list = []
        self.init_driver()
        self.openWA()
        self.getQR()
        self.searchChat()
        self.scrollChatTop()
        self.getSS()
        self.parseChat()
        self.closeWA()

    def init_driver(self):
        chromedriver_autoinstaller.install()
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        op.add_argument("test-type")
        op.add_argument("disable-gpu")
        op.add_argument("no-first-run")
        op.add_argument("no-default-browser-check")
        op.add_argument("ignore-certificate-errors")
        op.add_argument("start-maximized")
        op.add_argument("allow-running-insecure-content")
        op.add_argument(
            "user-agent=User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36")
        self.driver = webdriver.Chrome(options=op)

    def getSS(self):
        ss = self.driver.get_screenshot_as_png()
        im = Image.open(BytesIO(ss))
        im.save("screenshot.png")

    def openWA(self):
        self.driver.get("https://web.whatsapp.com")
        print("Opening", self.driver.title)

    def getQR(self):
        print("Reading QR")
        while True:
            try:
                sleep(1)
                element = self.driver.find_element_by_tag_name('canvas')
                break
            except:
                pass
        location = element.location
        size = element.size
        png = self.driver.get_screenshot_as_png()
        im = Image.open(BytesIO(png))
        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
        im = im.crop((left, top, right, bottom))
        image_window = tk.Tk()
        img = ImageTk.PhotoImage(im)
        panel = tk.Label(image_window, image=img)
        panel.pack(side="bottom", fill="both", expand="yes")

        def closeQR():
            try:
                self.driver.find_element_by_tag_name('canvas')
                image_window.after(1000, closeQR)
            except:
                print("QR Code scanned")
                image_window.destroy()

        image_window.after(1000, closeQR)
        image_window.mainloop()

    def searchChat(self):
        group = input("Enter group name: ")
        print("Reading", group, "chat")
        while True:
            try:
                sleep(1)
                element = self.driver.find_element_by_tag_name('label')
                break
            except:
                pass
        element.click()
        actions = ActionChains(self.driver)
        actions.send_keys(group)
        actions.send_keys(Keys.RETURN)
        actions.perform()
        sleep(5)

    def scrollChatTop(self):
        print("Scrolling to top of chat")
        html = self.driver.find_element_by_tag_name('html')
        messages = self.driver.find_elements_by_class_name("GDTQm")
        self.driver.find_element_by_class_name("GDTQm").click()
        sleep(1)
        last_length = len(messages)
        index = 0
        while True:
            index += 1
            html.send_keys(Keys.UP)
            if index % 100 == 0:
                sleep(5)
                new_length = len(
                    self.driver.find_elements_by_class_name("GDTQm"))
                if new_length == last_length:
                    break
                else:
                    last_length = new_length

    def listen_to_chat(self):
        print("Listening to new messages every 1 minute")
        while True:
            sleep(60)
            self.parseChat()

    def parseChat(self):
        print("Parsing Chat")
        messages = self.driver.find_elements_by_class_name("GDTQm")
        last_date = ""
        for msg in messages:
            message = BeautifulSoup(
                msg.get_attribute("outerHTML"), "html.parser")
            # Date
            if len(message.select("._2kR4B > span")) > 0:
                last_date = message.select(
                    "._2kR4B > span")[0].decode_contents()

            # Message
            if len(message.select(".ZJv7X")) > 0:
                mid = msg.get_attribute("data-id").split("@")[-1]
                number = message.select(".ZJv7X")[0].decode_contents()
                name = message.select("._2F1Ns")[0].decode_contents()
                if(name.startswith("<img")):
                    name = message.select("._2F1Ns > img")[0]["alt"]
                if len(message.select(".selectable-text")) > 0:
                    text = message.select(".selectable-text")[0].text
                else:
                    text = "[GIF]"
                text = " ".join(text.split())
                time = message.select("._17Osw")[0].decode_contents()

                self.message_list.append({
                    "id": mid,
                    "number": number,
                    "name": name,
                    "text": text,
                    "date": last_date,
                    "time": time
                })
        self.write_to_file()
        self.listen_to_chat()

    def write_to_file(self):
        with open('chat-data.json', 'w', encoding='utf-8') as f:
            json.dump(self.message_list, f, ensure_ascii=False, indent=4)

    def closeWA(self):
        self.driver.close()


wadb = WhatsappDB()
