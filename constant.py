"""Class having the Xpath for all the items"""
from enum import Enum

class XPath(Enum):
    """XPath for the crawler"""
    # XPath for the "Search" button
    CARD='//div[@class="page-content"]//div[@class="card-body"]'
    TITLE='.//a[@class="profile"]'
    SALARY='//div[@class="page-content"]//h2[contains(text()," $")]'
    COUNTRY='.//p/span[1]'
    EXPERIENCE='.//p/span[3]'
    JOB_STATUS='.//p/span[5]'
    PUBLISHED_DATE='.//p//span[7]'
    DESCRIPTION='.//div[contains(@class,"text-card")]'
    BADGE='.//span[contains(@class,"badge")]'
    PARENT_NXT_BTN='//div[@class="page-content"]//a[@tabindex="-1"]//span[contains(@class,"chevron-right")]'
    NEXT_BTN='//div[@class="page-content"]//span[contains(@class,"chevron-right")]'
    CATEGORIES="//b[text()='Розробка']/following-sibling::ul[1]/li/a"