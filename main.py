#!/usr/bin/env python
import sys
import traceback
import socket
import csv
import datetime
from os.path import basename
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from smtplib import SMTP

def send_email(subject, message_body, png_name):

  msg = MIMEMultipart()
  destination = "foenpeng@uw.edu,shiwei@pdx.edu"
  msg['Subject'] = subject
  msg['From'] = 'victor@jcui.info'
  msg['To'] = destination
  body = MIMEText(message_body, 'html')
  msg.attach(body)
  f = "_".join(png_name) + '.png'
  with open(f, 'rb') as fil:
    msg.attach(MIMEApplication(fil.read(),
                Content_Disposition='attachment; filename="%s"' % basename(f),
                Name=basename(f)))

  s = SMTP('localhost')
  s.sendmail('victor@jcui.info', destination.split(","), msg.as_string())
  s.quit()



def find_one_dollar_fare(data, browser):
  print("checking bus fare")
  #wr = csv.writer(open(report_file, 'at'))
  #rd = csv.reader(open(report_file, 'rt'), delimiter=',')

  report_file = '''./report.csv'''

  with open(report_file, 'a') as csvfile_w, open(report_file) as csvfile_r:

    rd = csv.reader(csvfile_r, delimiter=',')
    wr = csv.writer(csvfile_w)

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
   # MonthList = ["January, 2017", "February, 2017","March, 2017","April, 2017","May, 2017","June, 2017",
    #        "July, 2017","August, 2017","September, 2017","October, 2017","November, 2017","December, 2017"]

    MonthList = ["January", "February","March","April","May","June",
            "July","August","September","October","November","December"]
    TargetMonth = int(data[1])
    WebDriverWait(browser, 30).until(EC.invisibility_of_element_located((By.ID, "pleaseWaitEE_backgroundElement")))
    browser.find_element_by_id("ctl00_cphM_forwardRouteUC_imageE").click()
    month = browser.find_element_by_xpath("//td[@class = 'title']")
    monthstr = month.text.rpartition(',')[0]
    CurrentMonth = MonthList.index(monthstr) + 1

    while (TargetMonth != CurrentMonth):
      print(CurrentMonth)
      if (CurrentMonth < TargetMonth) or (CurrentMonth ==12):
        browser.find_element_by_xpath("//table/tbody/tr[2]/td/div[2]/table/tbody/tr/td[2]/div/div/table/thead/tr[2]/td[4]/div").click()
      else:
        browser.find_element_by_xpath("//table/tbody/tr[2]/td/div[2]/table/tbody/tr/td[2]/div/div/table/thead/tr[2]/td[2]/div").click()

      month = browser.find_element_by_xpath("//td[@class = 'title']")
      monthstr = month.text.rpartition(',')[0]
      CurrentMonth = MonthList.index(monthstr) + 1

    dollar_date = data[2]
    browser.find_element_by_xpath('//table/tbody/tr[2]/td/div[2]/table/tbody/tr/td[2]/div/div/table/tbody//td[text() = "%s"]'%dollar_date).click()
    WebDriverWait(browser, 30).until(EC.invisibility_of_element_located((By.ID, "pleaseWaitEE_backgroundElement")))


    # check fares for 1 dollar
    now = datetime.datetime.now()
    currentTime = now.strftime("%Y-%m-%d %H:%M")

    try:
      browser.save_screenshot('_'.join(data) + '.png')
      one_dollar_elements = browser.find_elements_by_xpath("//td[@class = 'faresColumn0 faresColumnDollar']/..//td[@class = 'faresColumn1']")
      if len(one_dollar_elements) > 0:
        report = []
        for item in one_dollar_elements:
          report += [data[0], data[1], data[2], data[3], item.text]
        report = "_".join(report)
        wr.writerow([currentTime, "FOUND", report])
        count = 0
        for line in rd:
          if report in line:
            count += 1
        if count < 2:
          print([currentTime, "FOUND", report])
          send_email("Good News!", report, data)
      else:
        # send_email("No $1 ticket @" + currentTime, "Please be patient for trip " + '_'.join(data), data)
        wr.writerow([currentTime, '_'.join(data), "NOTFOUND"])
        print([currentTime, '_'.join(data), "NOTFOUND"])
    except Exception as e:
      wr.writerow(str(e))

if __name__ == "__main__":
  now = datetime.datetime.now()
  currentTime = now.strftime("%Y-%m-%d %H:%M")
  print("Running at " + currentTime)

  display = Display(visible=0, size=(1024, 768))
  display.start()

  browser = webdriver.Firefox()

  try:
    browser.get('https://www.boltbus.com')
    print("browser get www.boltbus.com success")

    browser.find_element_by_name("ctl00$cphM$forwardRouteUC$lstRegion$textBox").click()
    browser.find_element_by_id("ctl00_cphM_forwardRouteUC_lstRegion_repeater_ctl02_link").click()
    ticket_dates = csv.reader(open('./ticket_date.csv','rU'))
    trips = [item for item in ticket_dates]

    for trip in trips:
      print("Searching for $1 ticket of " + '_'.join(trip))
      find_one_dollar_fare(trip, browser)

  except:
    err = open('err.txt', 'at')
    err.write("%s : \n %s \n" % (currentTime, traceback.format_exc()))

  browser.quit()
  display.stop()
