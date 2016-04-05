import sys
import traceback
import socket
import csv
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP

def send_email(subject, message_body):
  destination = "peng.foen@gmail.com,shi.wei8805@gmail.com,thucjw@gmail.com"
  msg = MIMEMultipart()
  msg['Subject'] = subject
  msg['From'] = 'victor@jcui.info'
  msg['To'] = destination
  body = MIMEText(message_body, 'html')
  msg.attach(body)
  s = SMTP('localhost')
  s.sendmail('victor@jcui.info', destination.split(","), msg.as_string())
  s.quit()

def find_one_dollar_fare(data):
  print("checking bus fare")
  #wr = csv.writer(open(report_file, 'at'))
  #rd = csv.reader(open(report_file, 'rt'), delimiter=',')

  report_file = '''/home/victor/foen/report.csv'''

  with open(report_file, 'a') as csvfile:
    rd = csv.reader(csvfile, delimiter=',')
    wr = csv.writer(csvfile)

    if data[0] == "S-P":
      WebDriverWait(browser, 30).until(EC.invisibility_of_element_located((By.ID, "pleaseWaitEE_backgroundElement")))
      browser.find_element_by_id('ctl00_cphM_forwardRouteUC_lstOrigin_imageE').click()
      browser.find_element_by_id("ctl00_cphM_forwardRouteUC_lstOrigin_repeater_ctl13_link").click()
      WebDriverWait(browser, 30).until(EC.invisibility_of_element_located((By.ID, "pleaseWaitEE_backgroundElement")))
      browser.find_element_by_id("ctl00_cphM_forwardRouteUC_lstDestination_imageE").click()
      browser.find_element_by_id("ctl00_cphM_forwardRouteUC_lstDestination_repeater_ctl03_link").click()
    else:
      WebDriverWait(browser, 30).until(EC.invisibility_of_element_located((By.ID, "pleaseWaitEE_backgroundElement")))
      browser.find_element_by_id('ctl00_cphM_forwardRouteUC_lstOrigin_imageE').click()
      browser.find_element_by_id("ctl00_cphM_forwardRouteUC_lstOrigin_repeater_ctl10_link").click()
      WebDriverWait(browser, 30).until(EC.invisibility_of_element_located((By.ID, "pleaseWaitEE_backgroundElement")))
      browser.find_element_by_id("ctl00_cphM_forwardRouteUC_lstDestination_imageE").click()
      browser.find_element_by_id("ctl00_cphM_forwardRouteUC_lstDestination_repeater_ctl03_link").click()

    # choose dates
    MonthList = ["January, 2016", "February, 2016","March, 2016","April, 2016","May, 2016","June, 2016",
            "July, 2016","August, 2016","September, 2016","October, 2016","November, 2016","December, 2016"]

    TargetMonth = int(data[1])
    WebDriverWait(browser, 30).until(EC.invisibility_of_element_located((By.ID, "pleaseWaitEE_backgroundElement")))
    browser.find_element_by_id("ctl00_cphM_forwardRouteUC_imageE").click()
    month = browser.find_element_by_xpath("//td[@class = 'title']")
    CurrentMonth = MonthList.index(month.text) + 1

    while (TargetMonth != CurrentMonth):
      if CurrentMonth < TargetMonth:
        browser.find_element_by_xpath("//table/tbody/tr[2]/td/div[2]/table/tbody/tr/td[2]/div/div/table/thead/tr[2]/td[4]/div").click()
      else:
        browser.find_element_by_xpath("//table/tbody/tr[2]/td/div[2]/table/tbody/tr/td[2]/div/div/table/thead/tr[2]/td[2]/div").click()

      month = browser.find_element_by_xpath("//td[@class = 'title']")
      CurrentMonth = MonthList.index(month.text) + 1

    dollar_date = data[2]
    browser.find_element_by_xpath('//table/tbody/tr[2]/td/div[2]/table/tbody/tr/td[2]/div/div/table/tbody//td[text() = "%s"]'%dollar_date).click()
    WebDriverWait(browser, 30).until(EC.invisibility_of_element_located((By.ID, "pleaseWaitEE_backgroundElement")))

    # check fares for 1 dollar
    now = datetime.datetime.now()
    currentTime = now.strftime("%Y-%m-%d %H:%M")

    try:
      one_dollar_elements = browser.find_elements_by_xpath("//td[@class = 'faresColumn0 faresColumnDollar']/..//td[@class = 'faresColumn1']")
      report = []
      for item in one_dollar_elements:
          report += [data[0], data[1], data[2], data[3], item.text]

      report = "_".join(report)

      count = 0
      for row in rd:
        if report == row[2]:
          count += 1

      if count < 3:
        wr.writerow([currentTime, "FOUND", report])
        send_email("Good News!", report)

    except Exception:
      send_email("No $1 ticket @" + currentTime, "Please be patient for trip " + '_'.join(data))
      wr.writerow([currentTime, "NOTFOUND"])
      print("no one dollar fare at this time")


if __name__ == "__main__":
  now = datetime.datetime.now()
  currentTime = now.strftime("%Y-%m-%d %H:%M")
  print("Running at " + currentTime)

  try:
    display = Display(visible=0, size=(1024, 768))
    display.start()

    browser = webdriver.Firefox()
    browser.get('https://www.boltbus.com')
    print("browser get boltbus success")

    browser.find_element_by_name("ctl00$cphM$forwardRouteUC$lstRegion$textBox").click()
    browser.find_element_by_id("ctl00_cphM_forwardRouteUC_lstRegion_repeater_ctl02_link").click()

    ticket_dates = csv.reader(open('/home/victor/foen/ticket_date.csv','rt'))
    trips = [item for item in ticket_dates]

    for trip in trips:
      print("Searching for $1 ticket of " + '_'.join(trip))
      find_one_dollar_fare(trip)

    browser.quit()
    display.stop()

  except:
    err = open('/home/victor/foen/err.txt', 'at')
    err.write("%s : \n %s \n" % (currentTime, traceback.format_exc()))

