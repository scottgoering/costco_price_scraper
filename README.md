# Costco Price Adjustment Checker

This project automates the process of checking for price adjustments on your recent Costco purchases. It’s a simple way to help you save money by making sure you’re notified if the price of something you bought recently has dropped. Costco’s price adjustment policy allows you to get a refund if the price decreases within 30 days of purchase, and this tool takes the hassle out of checking for those adjustments manually.

## Features

- **Automated Price Checks**: Automatically compares your recent purchases against current Costco sale prices.
- **Web Scraping**: Periodically scrapes Costco’s website to gather sale info using Selenium.
- **Email Alerts**: Sends you an email notification when a price adjustment is found, including the details on how to get a refund.
- **API Access**: Exposes sale information via an API to avoid unnecessary scraping.
- **Task Scheduling**: Uses Cron to run the scraper and notify you on a regular basis.

## Technologies Used

- **Python** (Backend)
- **Flask** (Web Framework)
- **Selenium** (Web Scraping)
- **SQLite** (Database)
- **Cron** (Task Scheduling)
- **Git** (Version Control)
