# -*- coding: utf-8 -*-
"""
Simple Linkedin crawler to collect user's  profile data.

@author: idwaker

To use this you need linkedin account, all search is done through your account

Requirements:
    python-selenium
    python-click
    python-keyring

Tested on Python 3 not sure how Python 2 behaves
"""

import sys
import csv
import time
import click
import getpass
import keyring
from selenium import webdriver
from selenium.common.exceptions import (WebDriverException,
                                        NoSuchElementException)


LINKEDIN_URL = 'https://www.linkedin.com'


class UnknownUserException(Exception):
    pass


class UnknownBrowserException(Exception):
    pass


class WebBus:
    """
    context manager to handle webdriver part
    """

    def __init__(self, browser):
        self.browser = browser
        self.driver = None

    def __enter__(self):
        # XXX: This is not so elegant
        # should be written in better way
        if self.browser.lower() == 'firefox':
            self.driver = webdriver.Firefox()
        elif self.browser.lower() == 'chrome':
            self.driver = webdriver.Chrome("D:\\Study\\3rd\\688\\team\\chromedriver_win32\\chromedriver.exe")
        elif self.browser.lower() == 'phantomjs':
            self.driver = webdriver.PhantomJS()
        else:
            raise UnknownBrowserException("Unknown Browser")

        return self

    def __exit__(self, _type, value, traceback):
        if _type is OSError or _type is WebDriverException:
            click.echo("Please make sure you have this browser")
            return False
        if _type is UnknownBrowserException:
            click.echo("Please use either Firefox, PhantomJS or Chrome")
            return False

        self.driver.close()


def get_password(username):
    """
    get password from stored keychain service
    """
    password = keyring.get_password('linkedinpy', username)
    if not password:
        raise UnknownUserException("""You need to store password for this user
                                        first.""")

    return password


def login_into_linkedin(driver, username):
    """
    Just login to linkedin if it is not already loggedin
    """
    userfield = driver.find_element_by_id('login-email')
    passfield = driver.find_element_by_id('login-password')

    submit_form = driver.find_element_by_class_name('login-form')

    password = get_password(username)

    # If we have login page we get these fields
    # I know it's a hack but it works
    if userfield and passfield:
        userfield.send_keys(username)
        passfield.send_keys(password)
        submit_form.submit()
        click.echo("Logging in")


def collect_names(filepath):
    """
    collect names from the file given
    """
    names = []
    with open(filepath, 'r') as _file:
        names = [line.strip() for line in _file.readlines()]
    return names


@click.group()
def cli():
    """
    First store password

    $ python linkedin store username@example.com
    Password: **

    Then crawl linkedin for users

    $ python linkedin crawl username@example.com with_names output.csv --browser=firefox
    """
    pass


@click.command()
@click.option('--browser', default='phantomjs', help='Browser to run with')
@click.argument('username')
@click.argument('infile')
@click.argument('outfile')
def crawl(browser, username, infile, outfile):
    """
    Run this crawler with specified username
    """

    # first check and read the input file
    all_names = collect_names(infile)
    fieldnames = ['fullname', 'locality', 'industry', 'current summary',
                  'past summary', 'education','skills','endorsements','positions']
    # then check we can write the output file
    # we don't want to complete process and show error about not
    # able to write outputs
    with open(outfile, 'w') as csvfile:
        # just write headers now
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    link_title = './/a[@class="title main-headline"]'

    # now open the browser
    with WebBus(browser) as bus:
        bus.driver.get(LINKEDIN_URL)

        login_into_linkedin(bus.driver, username)
        iteration = 0;
        idx = 0;
        while iteration < 20000:
                name = all_names[idx]
                if name in all_names[:idx]:
                    idx += 1
                    continue
                iteration += 1
                idx += 1
                click.echo("Getting ...")
#==============================================================================
#                 try:
#                     search_input = bus.driver.find_element_by_id('main-search-box')
#                 except NoSuchElementException:
#                     continue
#                 search_input.send_keys(name)
# 
#                 search_form = bus.driver.find_element_by_id('global-search')
#                 search_form.submit()
#     #            search_button = bus.driver.find_element_by_xpath(search_btn)
#     #            search_button.click()
# 
#                 
# 
#                 # collect all the profile links
#                 results = None
#                 try:
#                     results = bus.driver.find_element_by_id('results-container')
#                 except NoSuchElementException:
#                     continue
#                 links = results.find_elements_by_xpath(link_title)
#==============================================================================
                profiles = []                
                search_name = name.replace(" ","")
                link = LINKEDIN_URL + "/in/" + search_name
                # get all the links before going through each page
                #links = [link.get_attribute('href') for link in links]
                #for link in links:
                    # XXX: This whole section should be separated from this method
                    # XXX: move try-except to context managers
                bus.driver.get(link)

                overview = None
                overview_xpath = '//div[@class="profile-overview-content"]'
                try:
                    overview = bus.driver.find_element_by_xpath(overview_xpath)
                except NoSuchElementException:
                    click.echo("No overview section skipping this user")
                    continue

                # every xpath below here are relative
                fullname = None
                fullname_xpath = './/span[@class="full-name"]'
                try:
                    fullname = overview.find_element_by_xpath(fullname_xpath)
                except NoSuchElementException:
                    # we store empty fullname : notsure for this
                    fullname = ''
                    pass
                else:
                    fullname = fullname.text.strip()

                locality = None
                try:
                    locality = overview.find_element_by_class_name('locality')
                except NoSuchElementException:
                    locality = ''
                    pass
                else:
                    locality = locality.text.strip()
                # print "loc",locality

                industry = None
                try:
                    industry = overview.find_element_by_class_name('industry')
                except NoSuchElementException:
                    industry = ''
                    pass
                else:
                    industry = industry.text.strip()

                current_summary = None
                csummary_xpath = './/tr[@id="overview-summary-current"]/td'
                try:
                    current_summary = overview.find_element_by_xpath(csummary_xpath)
                except NoSuchElementException:
                    current_summary = ''
                else:
                    current_summary = current_summary.text.strip()

                past_summary = None
                psummary_xpath = './/tr[@id="overview-summary-past"]/td'
                try:
                    past_summary = overview.find_element_by_xpath(psummary_xpath)
                except NoSuchElementException:
                    past_summary = ''
                    pass
                else:
                    past_summary = past_summary.text.strip()

                education = None
                education_xpath = './/tr[@id="overview-summary-education"]/td'
                try:
                    education = overview.find_element_by_xpath(education_xpath)
                except NoSuchElementException:
                    education = ''
                else:
                    education = education.text.strip()

                skills = ''
                skills_xpath =  '//a[@class="endorse-item-name-text"]'
                try:
                    skills_summary = overview.find_elements_by_xpath(skills_xpath)
                except NoSuchElementException:
                    skills = ''
                else:
                    try:
                        skills_list = [skill.text for skill in skills_summary]
                        for i in skills_list:
                            skills += str(i)+','
                    except Exception, e:
                        pass



                endorsements = ''
                endorsements_xpath =  '//span[@class="num-endorsements"]'
                try:
                    endorsements_summary = overview.find_elements_by_xpath(endorsements_xpath)
                except NoSuchElementException:
                    endorsements = ''
                else:
                    try:
                        endorsements_list = [endorsement.text for endorsement in endorsements_summary]
                        for i in endorsements_list:
                            if i=="":
                                i = 0
                            endorsements += str(i)+','
                    except Exception, e:
                        pass


                positions = ''
                positions_xpath =  '//a[@title="Learn more about this title"]'
                try:
                    positions_summary = overview.find_elements_by_xpath(positions_xpath)
                except NoSuchElementException:
                    positions = ''
                else:
                    try:
                        positions_list = [position.text for position in positions_summary]
                        for i in positions_list:
                            positions += str(i)+','
                    except Exception, e:
                        pass


                name_elements = None
                name_list = []
                name_xpath = '//a[contains(@href,"trk=prof-sb-browse_map-name")]'
                try:
                    name_elements = overview.find_elements_by_xpath(name_xpath)
                except NoSuchElementException:
                    name_list = ''
                    print "失败了卧槽!"
                else:
                    for element in name_elements:
                        try:
                            if str(element.text.strip().lower()) != '' and (str(element.text.strip().lower()) not in name_list) and (str(element.text.strip().lower()) not in all_names):
                                name_list.append(str(element.text.strip().lower()))
                        except Exception:
                            continue
                    if len(name_list) != 0:
                        with open("list_of_names.csv","a+") as f:
                            wr = csv.writer(f,delimiter="\n")
                            wr.writerow(name_list)
                    #print name_list
                all_names = collect_names(infile)

                data = {
                    'fullname': fullname,
                    'locality': locality,
                    'industry': industry,
                    'current summary': current_summary,
                    'past summary': past_summary,
                    'education': education,
                    'skills':skills,
                    'endorsements':endorsements,
                    'positions': positions
                }
                profiles.append(data)
                #print len(profiles)
                #print profiles

                with open(outfile, 'a+') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    for profile in profiles:
                        try:
                            writer.writerow(profile)
                        except Exception:
                            continue

                click.echo("Obtained ..." + name)



@click.command()
@click.argument('username')
def store(username):
    """
    Store given password for this username to keystore
    """
    passwd = getpass.getpass()
    keyring.set_password('linkedinpy', username, passwd)
    click.echo("Password updated successfully")


cli.add_command(crawl)
cli.add_command(store)


if __name__ == '__main__':
    cli()
