"""automated crawler to get the job details"""
import time
import uuid  # Import the uuid module for generating unique job IDs
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from constant import XPath
from database_config import DatabaseConfig  # Import the database config class
from selenium.common.exceptions import NoSuchElementException

class SeleniumCrawler:
    """Initialize Chrome driver and the MySQL connection."""
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.db_config = DatabaseConfig()
        self.batch_data = []  # Store data in batches before writing to the database

    def safe_find_element(self, element, xpath, attr='text'):
        """Safely find element by XPath and return attribute value or None if not found"""
        try:
            el = element.find_element(By.XPATH, xpath)
            if attr == 'text':
                return el.text
            return el.get_attribute(attr)
        except Exception:
            return None

    def fetch_job_data(self, job):
        """Fetch individual job data"""
        data = {}
        data['title'] = self.safe_find_element(job, XPath.TITLE.value)
        data['job_url']= job.find_element(By.XPATH, XPath.TITLE.value).get_attribute('href')
        data['salary'] = self.safe_find_element(job, XPath.SALARY.value)
        data['country'] = self.safe_find_element(job, XPath.COUNTRY.value)
        data['experience'] = self.safe_find_element(job, XPath.EXPERIENCE.value)
        data['job_status'] = self.safe_find_element(job, XPath.JOB_STATUS.value)
        publish_date = self.safe_find_element(job, XPath.PUBLISHED_DATE.value)
        data['publish_date'] = publish_date.split('.').pop().strip() if publish_date else None
        print(data['publish_date'])
        data['description'] = self.safe_find_element(job, XPath.DESCRIPTION.value)

        # Fetch all badges
        badges = job.find_elements(By.XPATH, XPath.BADGE.value)
        data['badges'] = [badge.text for badge in badges] if badges else []

        return data

    def write_batch_to_db(self):
        """Write the accumulated batch data to the database and clear the batch."""
        if self.batch_data:
            try:
                conn = self.db_config.connect()  # Connect to the database
                self.db_config.store_data(conn, self.batch_data)  # Store the data into the DB
                self.batch_data = []  # Clear the batch after storing data
                conn.close()
            except Exception as e:
                logger.error(f"Error occurred while writing batch to database: {e}")

    def start(self):
        """Start the crawler"""
        urls=[]
        batch_size = 10  # Size of the batch to accumulate data
        self.driver.get('https://djinni.co/developers/?region=POL&base=active')
        time.sleep(5)
        for i in range(2):
            i=i+1
            categories = self.driver.find_elements(By.XPATH,f"//b[text()='Розробка']/following-sibling::ul[{i}]/li/a")
        # Get all category URLs
            for category in categories:
                urls.append(category.get_attribute('href'))
            logger.info(f"Found {len(urls)} categories.")

        for url in urls:
            page_count = 0
            self.driver.get(url)
            logger.info(f"Navigating to category: {url}")
            time.sleep(5)
            while True:
                try:
                    jobs_details = self.driver.find_elements(By.XPATH, XPath.CARD.value)
                except Exception as e:
                    logger.error(f'Error occurred while fetching job details: {e}')

                for job in jobs_details:
                    try:
                        job_data = self.fetch_job_data(job)
                        job_data['id'] = str(uuid.uuid4())  # Generate a unique UUID for each job
                        self.batch_data.append(job_data)  # Accumulate data in the batch

                        if len(self.batch_data) >= batch_size:  # If batch size is met, write to DB
                            self.write_batch_to_db()
                            logger.info("Writing to the database")
                    except Exception as e:
                        logger.error(f'Error occurred while processing job data: {e}')

                try:
                    # Check if the parent element has an attribute `disabled="True"`
                    parent_class = self.driver.find_element(By.XPATH, XPath.PARENT_NXT_BTN.value)
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", parent_class)
                    if parent_class:
                        break  # Exit the loop as there's no more pages
                except Exception as e:
                    page_count += 1
                    logger.info(f"Moving to next page {page_count}...")
                    try:
                        next_page = self.driver.find_element(By.XPATH, XPath.NEXT_BTN.value)
                        if next_page:
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", next_page)
                            next_page.click()
                            time.sleep(3)
                        else:
                            logger.info("No more pages to navigate.")
                            break  # Exit the loop as there's no more pages
                    except NoSuchElementException:
                        logger.info("no more pages to navigate.")
                        break

            # Write any remaining data in the batch to the database after exiting the loop
            self.write_batch_to_db()

        self.driver.quit()

if __name__ == '__main__':
    db_config = DatabaseConfig()
    conn = db_config.connect()
    db_config.create_table(conn)  # Create the table if it doesn't already exist
    conn.close()
    
    crawler = SeleniumCrawler()
    crawler.start()

