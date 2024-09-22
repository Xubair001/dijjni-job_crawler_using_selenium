from typing import List
import os
import uuid
import mysql.connector
from loguru import logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DatabaseConfig:
    """Class to handle database connections and operations."""

    def __init__(self):
        self.host = os.getenv('DB_HOST')
        self.port = int(os.getenv('DB_PORT'))
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.database = os.getenv('DB_NAME')

    def connect(self) -> mysql.connector.MySQLConnection:
        """Connect to the MySQL database."""
        conn = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
        logger.success("Connected to MySQL server")
        return conn

    def create_table(self, conn) -> None:
        """Create the jobs_data table with the correct schema."""
        curr = conn.cursor()
        curr.execute("DROP TABLE IF EXISTS jobs_data")  # Drop table if it already exists
        create_table = """
        CREATE TABLE jobs_data(
            id VARCHAR(36) PRIMARY KEY,  -- UUID for unique identification
            title VARCHAR(255),          -- Job title
            job_url VARCHAR(255),        -- Job url
            salary VARCHAR(255),         -- Salary
            country VARCHAR(255),        -- Country
            experience VARCHAR(255),     -- Experience level
            job_status VARCHAR(255),     -- Job status (active, inactive)
            publish_date VARCHAR(255),   -- Date when the job was published
            description TEXT             -- Job description
        )
        """
        curr.execute(create_table)
        conn.commit()
        curr.close()
        logger.success("Table 'jobs_data' created successfully")

    def store_data(self, conn, data: List[dict]) -> None:
        """
        Store data into the database. Each entry in 'data' should be a dictionary containing:
        'title','job_url', 'salary', 'country', 'experience', 'job_status', 'publish_date', 'description'.
        """
        curr = conn.cursor()

        insert_sql = """
        INSERT INTO jobs_data (id, title,job_url, salary, country, experience, job_status, publish_date, description) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)
        """

        insert_values = [
            (
                str(uuid.uuid4()),  # Generate a unique UUID for each entry
                job['title'],
                job['job_url'],
                job['salary'],
                job['country'],
                job['experience'],
                job['job_status'],
                job['publish_date'],  # Ensure the date is in the correct format (YYYY-MM-DD)
                job['description']
            )
            for job in data
        ]

        try:
            curr.executemany(insert_sql, insert_values)
            conn.commit()
            logger.success(f"Inserted {len(data)} records into the database.")
        except mysql.connector.Error as err:
            logger.error(f"Error storing data: {err}")
        finally:
            curr.close()
