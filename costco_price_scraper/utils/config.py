import configparser

config_path = '/home/jacky/Code/costco_price_scraper/config.ini'

def read_config(section, option):
    config = configparser.ConfigParser()
    config.read(config_path)
    return config.get(section, option)

def read_sender_email_config():
    return read_config("Credentials", "GMAIL_USERNAME"), read_config("Credentials", "GMAIL_PASSWORD")

def read_login_config():
    return read_config("Credentials", "USERNAME"), read_config("Credentials", "PASSWORD")

def read_username_config():
    return read_config("Credentials", "USERNAME")