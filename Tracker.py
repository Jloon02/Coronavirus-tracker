import yaml
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def parse_yml():
    """
    Parses config file as dict
    :return: config file as dict
    """
    with open('config.yml') as file:
        try:
            config = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(exc)
    return config


def init_driver():
    """
    Initializes chromedriver
    :return: chromedriver
    """
    options = webdriver.ChromeOptions()
    #options.add_argument("headless")
    driver = webdriver.Chrome(options=options, executable_path="chromedriver.exe")
    return driver


def plot_graph(myDict):
    """
    Plots the given data in a bar graph and displays it
    :param myDict: dictionary with date:cases
    :return: function that takes in x and returns an estimate for y
    """
    # Create graph from dict
    plt.plot(*zip(*myDict.items()), '-b', label="Death Count")

    # Label graph
    plt.xlabel("Date")
    plt.ylabel("Total Deaths")
    plt.title("Total deaths due to COVID-19")

    # Create x and y list with graph info and print linear regression info
    x_list = list(range(0, len(myDict)))
    y_list = list(myDict.values())
    regress_list = linregress(x_list, y_list)
    print(regress_list)

    # Write x-axis labels every 90 days
    plt.xticks(range(min(x_list), max(x_list) + 1, 90))

    # Plot linear regression line
    coef = np.polyfit(x_list, y_list, 1)
    poly1d_fn = np.poly1d(coef)
    plt.plot(x_list, y_list, poly1d_fn(x_list), '--k')
    plt.legend(loc='upper left')

    # Show the graph
    plt.show()

    # Return a function of linear regression from graph
    return poly1d_fn


def get_table(driver):
    """
    Finds the table information for past cases
    :param driver: chromedriver
    :return: a dict with dates:cases for that day
    """

    table_dict = dict()
    # Go to graph page
    link = driver.find_element(By.LINK_TEXT, 'Graphs')
    link.click()

    try:
        # Get info of table
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'table-responsive'))
        )
        # get all rows in the table
        tbody = table.find_element(By.TAG_NAME, 'tbody')
        rows = tbody.find_elements(By.TAG_NAME, 'tr')
        for row in reversed(rows):
            # Create dict with Date: Total Deaths
            date = row.find_elements(By.TAG_NAME, 'td')[0]
            deaths = row.find_elements(By.TAG_NAME, 'td')[1]
            deaths_num = int(deaths.text.replace(',', ''))
            table_dict[date.text.rstrip()] = deaths_num
    finally:
        driver.back()

    return table_dict


def main():
    config = parse_yml()
    driver = init_driver()

    # Opens the website with chrome's webdriver
    driver.get("https://www.worldometers.info/coronavirus/")

    # Grab the current total Coronavirus cases information
    counter = driver.find_element(By.CLASS_NAME, 'maincounter-number')
    cases = int(counter.text.replace(',', ''))

    # Get dict of total deaths for each day
    table_dict = get_table(driver)

    # Plot the graph and return a linear regression list
    regression = plot_graph(table_dict)
    print("There will be an estimate of:", regression(len(table_dict)+30), "Deaths by next month, and",
          regression(len(table_dict)+365), "Deaths by next year")

    # Close driver and end program
    driver.quit()
    print("Successfully finished")


if __name__ == '__main__':
    main()
