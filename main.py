from typing import List
import uiautomator2 as u2
from uiautomator2.xpath import XPathElementNotFoundError
from uiautomator2 import Device
from uiautomator2.xpath import DeviceXMLElement
import logging
import time
from random import random,choice
import threading
import json

messagesXPATH ="""//*[@content-desc="Message"]"""
homePATH='//*[@resource-id="com.instagram.android:id/feed_tab"]'
dPATH = '//*[@resource-id="com.instagram.android:id/inbox_refreshable_thread_list_recyclerview"]/*[@resource-id="com.instagram.android:id/row_inbox_container"]'
uNameRelative = '*/*[@resource-id="com.instagram.android:id/row_inbox_username"]'
dParentPATH = '//*[@resource-id="com.instagram.android:id/inbox_refreshable_thread_list_recyclerview"]'
editTXTPATH ='//android.widget.EditText'
sendBTNXPATH='//*[@resource-id="com.instagram.android:id/row_thread_composer_send_button_container"]'
homeSWAPXPATH='//*[@resource-id="com.instagram.android:id/layout_container_swipeable"]'
likeXPATH='//*[@resource-id="com.instagram.android:id/row_feed_button_like"]'


optFILE = open("opt.json","r")
options = json.load(optFILE)
optFILE.close()

WRITE_SLEEP_MIN = options["write_sleep_min"]
WRITE_SLEEP_MAX= options["write_sleep_max"]
BTN_SLEEP_MIN = options["btn_sleep_min"] 
BTN_SLEEP_MAX = options["btn_sleep_max"] 
PAGE_SLEEP_MIN= options["page_sleep_min"]
PAGE_SLEEP_MAX= options["page_sleep_max"]
HOME_CHANCE= options["home_chance"]
HOME_SWAP_MIN =options["home_swap_min"] 
HOME_SWAP_MAX =options["home_swap_max"]
HOME_VIEW_SEC_MIN= options["home_view_sec_min"]
HOME_VIEW_SEC_MAX= options["home_view_sec_max"]
LIKE_CHANCE = options["like_chanse"]


# sendXPATH
f = open("InputMsg.txt","r",encoding="UTF-8")
INPUT = f.read()
f.close()
u2m = {line.split(":")[1]:line.split(":")[0]  for line in INPUT.split("\n")}
u2el ={}
userRemaining:List[str] = []
        
allusers = []

def sendDirect(d:Device,msg:str,logger:logging.Logger):
    editElem=None
    sendElem=None
    try:
        editElem = d.xpath(editTXTPATH)
        sendElem = d.xpath(sendBTNXPATH)
    except XPathElementNotFoundError:
        logger.fatal("TextBox|send Icon not found")
        return
    editElem.set_text(msg)
        # time.sleep(
        #         random()*(WRITE_SLEEP_MAX-WRITE_SLEEP_MIN)+WRITE_SLEEP_MIN
        #     )
    sendElem.click()

def handleInstagram(serialNumber):
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename=f'INSTAGRAM_{serialNumber.split(":")[0]}.log', encoding='utf-8', level=logging.DEBUG)
    d = u2.connect(serial=serialNumber)
    d.app_start("com.instagram.android")
    homeXOBJ =  d.xpath(messagesXPATH)
    homeXOBJ.wait()
    if not homeXOBJ.exists:
        logger.fatal("HOME Icon not found")
    msgXOBJ =  d.xpath(messagesXPATH)
    if not msgXOBJ.exists:
        logger.fatal("Message Icon not found")
    homeSWAPSel = d.xpath(homeSWAPXPATH)
    if not msgXOBJ.exists:
        logger.fatal("Home Swapping not found")
    homeELM = homeXOBJ.get()
    msgELM = msgXOBJ.get()
    homeSWAPELM = homeSWAPSel.get()
    def goHome():
        homeELM = d.xpath(homePATH).get()
        homeELM.click()
        time.sleep(int(random()*(PAGE_SLEEP_MAX-PAGE_SLEEP_MIN)+PAGE_SLEEP_MIN))
    def goDirect():
        msgELM.click()
        d.xpath(dParentPATH).wait()
        time.sleep(int(random()*(PAGE_SLEEP_MAX-PAGE_SLEEP_MIN)+PAGE_SLEEP_MIN))

    goDirect()
    directSel  = d.xpath(dPATH)
    directs = directSel.all()
    if not directs:
        logger.info("No Contant Found")
    unameEls = directSel.child(uNameRelative).all()
    for i,unameEl in enumerate(unameEls):
        u2el[unameEl.text] = directs[i]
        userRemaining.append(unameEl.text)
    allusers = userRemaining.copy()
    while (userRemaining):
        if random()<HOME_CHANCE:
            goHome()
            for _ in range(int(random()*(HOME_SWAP_MAX-HOME_SWAP_MIN)+HOME_SWAP_MIN)):
                homeSWAPELM.swipe("up")
                time.sleep(random()*(HOME_VIEW_SEC_MAX-HOME_VIEW_SEC_MIN)+HOME_VIEW_SEC_MIN)
                if random()<LIKE_CHANCE:
                    likeSel =d.xpath(likeXPATH)
                    if not  likeSel.wait(timeout=1):
                        homeSWAPELM.swipe("up")
                        likeSel.wait(timeout=1000)
                    likeSel.click()

        else:
            goDirect()
            uname = choice(list(userRemaining))
            unameEls = directSel.child(uNameRelative).all()
            direct = None
            for i,unameEl in enumerate(unameEls):
                if unameEl.text==uname:
                    direct = unameEl
                    break
            if uname in u2m:
                direct.click()
                time.sleep(random()*(PAGE_SLEEP_MAX-PAGE_SLEEP_MIN)+PAGE_SLEEP_MIN)
                sendDirect(d,u2m[uname],logger)
                time.sleep(random()*(PAGE_SLEEP_MAX-PAGE_SLEEP_MIN)+PAGE_SLEEP_MIN)
            d.press("back")
            userRemaining.remove(uname)


def main():
    threads:List[threading.Thread] = []
    with open("serials.txt","r") as f:
        while True:
            line =f.readline()
            if not line:
                break
            t = threading.Thread(target=handleInstagram, args=(line,))
            threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()



if __name__ == "__main__":
    main()



