from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from userInfo import username, password, order_page, index_page
import os
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.section import WD_ORIENT
import wget
from PIL import Image
from htmldocx import HtmlToDocx

class GetOrderInfo:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.index_page = index_page
        self.order_page = order_page
        self.chrome_options = webdriver.ChromeOptions()
        # self.chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.implicitly_wait(15)
        self.infoButtonsLinks = []
        self.orderIDs = []

    def LogIn(self):
        self.driver.get(self.index_page)
        # time.sleep(1)
        usernameInput = self.driver.find_element(By.XPATH, "/html/body/div/div[2]/div/form/div/div[3]/input")
        passwordInput = self.driver.find_element(By.XPATH, "/html/body/div/div[2]/div/form/div/div[4]/input")
        usernameInput.send_keys(self.username)
        passwordInput.send_keys(self.password)
        self.driver.find_element(By.XPATH, "/html/body/div/div[2]/div/form/div/button").click()
        time.sleep(1)
        
    def GetEnvelopeButtonLinks(self):
        self.driver.get(self.order_page)
        table = self.driver.find_element(By.XPATH, "//*[@id='datatable-default']")
        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows[1:]:
            infoButton = row.find_element(By.CSS_SELECTOR, "td:nth-child(7) > a.btn.btn-xs.btn-success")
            columns = row.find_elements(By.TAG_NAME, "td")
            row_data = columns[0].text
            self.orderIDs.append(row_data)
            self.infoButtonsLinks.append(infoButton.get_attribute('href'))

    def GetEnvelopeTexts(self, infoButtonLink, i):
        parent_dir = "C:\Mektuplar"

        document = Document()
        new_parser = HtmlToDocx()

        # Ayarla
        sections = document.sections
        for section in sections:
            section.page_height = Cm(29.7)
            section.page_width = Cm(21.0)
            section.top_margin = Cm(2.5)
            section.bottom_margin = Cm(2.5)
            section.left_margin = Cm(2.5)
            section.right_margin = Cm(2.5)
            section.orientation = WD_ORIENT.PORTRAIT  # Yatay (landscape) yönlü olarak ayarla

        style = document.styles['Normal']
        font = style.font
        font.name = 'Times New Roman'
        font.size = Pt(13)

        self.driver.get(infoButtonLink)
        # time.sleep(1)

        folder_name = str(self.orderIDs[i]) + " - "  + self.driver.find_element(By.CSS_SELECTOR, "#home > div:nth-child(3) > div > input").get_attribute("value")
        path = os.path.join(parent_dir, folder_name)

        os.mkdir(path)
        time.sleep(1)
        self.driver.find_element(By.XPATH, "/html/body/section/div/section/div/div/form/div/ul/li[2]/a").click()
        time.sleep(1)

        iframe = self.driver.find_element(By.XPATH, "/html/body/section/div/section/div/div/form/div/div/div[2]/div[1]/div/div/div/div/iframe")
        self.driver.switch_to.frame(iframe)

        try:
            body_element = self.driver.find_element(By.XPATH, "/html/body")
            # p_element = self.driver.find_element(By.XPATH, "/html/body/p[1]")
            span = body_element.find_element(By.TAG_NAME, "span")
            spanStyleText = span.get_attribute("style")
            spanStyleTexts = spanStyleText.split(":")
            spanStyleTexts = spanStyleTexts[1].split(",")
            if '"' in spanStyleTexts[0]:
                spanStyleTexts = spanStyleTexts[0].replace('"', "")
                font.name = spanStyleTexts
            else:
                font.name = spanStyleTexts[0]
        except:
            pass
            
        self.driver.switch_to.default_content()

        os.chdir(f'C:\Mektuplar\{folder_name}')
        envelopeTextHTML = self.driver.find_element(By.ID, "lettermessage").get_attribute("value")
        new_parser.add_html_to_document(envelopeTextHTML, document)
        document.save(f"{folder_name}.docx")
    
    def GetEnvelopeExtras(self, infoButtonLink, i):
        cardpostals = []
        image_number = 1

        self.driver.get(infoButtonLink)
        # time.sleep(1)
        folder_name = str(self.orderIDs[i]) + " - "  + self.driver.find_element(By.CSS_SELECTOR, "#home > div:nth-child(3) > div > input").get_attribute("value")
        os.chdir(f'C:\Mektuplar\{folder_name}')
        time.sleep(1)
        self.driver.get(self.driver.find_element(By.XPATH, "//*[@id='home']/div[1]/a").get_attribute('href'))
        self.driver.set_window_size(684, 494)
        screenshot = self.driver.get_screenshot_as_png()
        im = Image.open(BytesIO(screenshot))
        im.save("Zarf.png")
        time.sleep(1)
        self.driver.get(infoButtonLink)
        self.driver.find_element(By.XPATH, "/html/body/section/div/section/div/div/form/div/ul/li[2]/a").click()
        time.sleep(1)
        try:
            wget.download(self.driver.find_element(By.CSS_SELECTOR, "#icerik > div:nth-child(2) > div > a").get_attribute('href'), "Fotoğraf.jpg")
        except:
            print("Fotoğraf Bulunmadı.")

        try:
            cardpostals = self.driver.find_elements(By.CLASS_NAME, "img-fluid")
            for cardpostal in cardpostals:
                cardpostalLink = cardpostal.get_attribute("src")
                wget.download(cardpostalLink, f"Kartpostal {str(image_number)}.png")
                image_number += 1
        except:
            print("Kartpostal Bulunmadı.")

    def GetOrderInformation(self, infoButtonLink, i):
        self.driver.get(infoButtonLink)
        # time.sleep(1)
        folder_name = str(self.orderIDs[i]) + " - "  + self.driver.find_element(By.CSS_SELECTOR, "#home > div:nth-child(3) > div > input").get_attribute("value")
        time.sleep(1)
        os.chdir(f'C:\Mektuplar\{folder_name}')
        f = open(f"{folder_name}.txt", "w+", encoding="utf-8")
        f.write("Sipariş Tarihi: " + str(self.driver.find_element(By.CSS_SELECTOR, "#created_at").get_attribute("value")) +
                "\nSipariş Numarası: " + str(self.driver.find_element(By.CSS_SELECTOR, "#merchant_oid").get_attribute("value")) +
                "\nÜye Adı: " + str(self.driver.find_element(By.CSS_SELECTOR, "#home > div:nth-child(3) > div > input").get_attribute("value")) +
                "\nSipariş Tutarı: " + str(self.driver.find_element(By.CSS_SELECTOR, "#order_amount").get_attribute("value")) +
                "\nDurum: " + str(self.driver.find_element(By.CSS_SELECTOR, "#home > div:nth-child(5) > div > input").get_attribute("value")) +
                "\n\n" + str(self.driver.find_element(By.XPATH, "//*[@id='home']/div[6]/div/div").text) +
                "\n" + str(self.driver.find_element(By.XPATH, "//*[@id='home']/div[7]/div/div").text) +
                "\n" + str(self.driver.find_element(By.XPATH, "//*[@id='home']/div[8]/div/div").text) 
                )
            
    def runProgram(self):
        getText.GetEnvelopeButtonLinks()
        for i, infoButtonLink in enumerate(self.infoButtonsLinks):
            os.chdir("C:\\Mektuplar")
            self.driver.get(infoButtonLink)
            # time.sleep(1)
            folder_name = str(self.orderIDs[i]) + " - "  + self.driver.find_element(By.CSS_SELECTOR, "#home > div:nth-child(3) > div > input").get_attribute("value")
            print(folder_name)
            if not os.path.exists(f'C:\\Mektuplar\\{folder_name}'):
                print("Mektup Yazıları Alınıyor.")
                self.GetEnvelopeTexts(infoButtonLink, i)
                print("Mektup Ekstraları(Fotoğraf, Kartpostal) Alınıyor.")
                self.GetEnvelopeExtras(infoButtonLink, i)
                print("\nSipariş Detayları(İsim soyisim, Ücret, Tarih, Kağıt Rengi, Zarf Rengi) Alınıyor.")
                self.GetOrderInformation(infoButtonLink, i)
                os.chdir("C:\\Mektuplar")
        t = time.localtime()
        print(time.strftime("%H:%M:%S", t) + " Kontrol Tamamlandı Başa Dönülüyor.")
        self.orderIDs.clear()
        self.infoButtonsLinks.clear()
        self.runProgram()

if __name__ == "__main__":
    getText = GetOrderInfo(username, password)
    getText.LogIn()
    getText.runProgram()


