"""IT Dashboard challenge By Automatorr."""

# Importing Necessary Libraries and Packages
import os
from time import sleep
from datetime import timedelta
from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from RPA.PDF import PDF

OUTPUT_DIR = "output"

# Making the Directory in case it doesn't exists
if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)


# Creating Class property for ITDashboard and methods and functions
class ItDashboardGov:
    agencies = []
    headers = []

    def __init__(self):
        self.browser = Selenium()
        self.files = Files()
        self.browser.set_download_directory(os.path.join(os.getcwd(), f"{OUTPUT_DIR}"))
        self.browser.open_available_browser("https://itdashboard.gov/")
        self.pdf = PDF()

    def scrape_agencies(self):
        # Making sure the Page contains the necessary element which is the Dive-IN button
        self.browser.wait_until_page_contains_element('//*[@id="node-23"]/div/div/div/div/div/div/div/a')
        self.browser.find_element('//*[@id="node-23"]/div/div/div/div/div/div/div/a').click()
        # Giving the Site some time to load properly
        sleep(5)
        # Fetching the amount spent on investment by each agency
        self.agencies = self.browser.find_elements(
            '//div[@id="agency-tiles-widget"]//div[@class="col-sm-4 text-center noUnderline"]')
        companies = ['companies', ]
        investments = ['investments', ]
        for item in self.agencies:
            agency_data = item.text.split('\n')
            companies.append(agency_data[0])
            investments.append(agency_data[2])
        entries = {"companies": companies, "investments": investments}
        # Saving data to Excelsheet
        sv = self.files.create_workbook("output/Agencies.xlsx")
        sv.append_worksheet("Sheet", entries)
        sv.save()

    def get_headers(self):
        # Getting Headers
        while True:
            try:
                all_header = self.browser.find_element(
                    '//table[@class="datasource-table usa-table-borderless dataTable no-footer"]'
                ).find_element_by_tag_name(
                    "thead").find_elements_by_tag_name("tr")[1].find_elements_by_tag_name("th")
                if all_header:
                    break
            except:
                sleep(1)
        for item in all_header:
            self.headers.append(item.text)

    def match_pdf(self, uii, name):
        self.pdf.extract_pages_from_pdf(
            source_path=f"output/{uii}.pdf",
            output_path=f"output/page{uii}.pdf",
            pages=1
        )
        text = self.pdf.get_text_from_pdf(f"output/page{uii}.pdf")
        for i in text:
            if name and uii in text[i]:
                os.remove(f"output/page{uii}.pdf")
                return True
        os.remove(f"output/page{uii}.pdf")
        return False

    def scrape_agency(self, agency_to_scrape):
        agency = self.agencies[agency_to_scrape]
        # Waiting unitl the Page contains the necessary element
        self.browser.wait_until_page_contains_element(agency)
        # Fetching URL
        url = self.browser.find_element(agency).find_element_by_tag_name("a").get_attribute("href")
        self.browser.go_to(url)
        self.browser.wait_until_page_contains_element('//*[@id="investments-table-object_info"]',
                                                      timeout=timedelta(seconds=60))
        raw_total = self.browser.find_element('//*[@id="investments-table-object_info"]')
        data = raw_total.text.split(" ")
        total_entries = int(data[-2])
        self.browser.wait_until_page_contains_element('//*[@id="investments-table-object_length"]/label/select')
        self.browser.find_element('//*[@id="investments-table-object_length"]/label/select').click()
        self.browser.find_element('//*[@id="investments-table-object_length"]/label/select/option[4]').click()
        self.browser.wait_until_page_contains_element(
            f'//*[@id="investments-table-object"]/tbody/tr[{total_entries}]/td[1]', timeout=timedelta(seconds=25))
        self.get_headers()
        uii_ids = [self.headers[0]]
        bureau = [self.headers[1]]
        investment_title = [self.headers[2]]
        total_FY2021 = [self.headers[3]]
        type_agency = [self.headers[4]]
        CIO_rating = [self.headers[5]]
        num_of_project = [self.headers[6]]
        pdf_match = ["PDF MATCH", ]
        for i in range(1, total_entries + 1):
            self.browser.wait_until_page_contains_element(
                f'//*[@id="investments-table-object"]/tbody/tr[{total_entries}]/td[1]', timeout=timedelta(seconds=20))
            item = self.browser.find_element(f'//*[@id="investments-table-object"]/tbody/tr[{i}]/td[1]')
            bureau_current = self.browser.find_element(
                f'//*[@id="investments-table-object"]/tbody/tr[{i}]/td[2]').text
            investment_title_current = self.browser.find_element(
                f'//*[@id="investments-table-object"]/tbody/tr[{i}]/td[3]').text
            total_FY2021_current = self.browser.find_element(
                f'//*[@id="investments-table-object"]/tbody/tr[{i}]/td[4]').text
            type_agency_current = self.browser.find_element(
                f'//*[@id="investments-table-object"]/tbody/tr[{i}]/td[5]').text
            CIO_rating_current = self.browser.find_element(
                f'//*[@id="investments-table-object"]/tbody/tr[{i}]/td[6]').text
            num_of_project_current = self.browser.find_element(
                f'//*[@id="investments-table-object"]/tbody/tr[{i}]/td[7]').text
            bureau.append(bureau_current)
            investment_title.append(investment_title_current)
            total_FY2021.append(total_FY2021_current)
            type_agency.append(type_agency_current)
            CIO_rating.append(CIO_rating_current)
            num_of_project.append(num_of_project_current)
            uii_ids.append(item.text)
            try:
                link = self.browser.find_element(
                    f'//*[@id="investments-table-object"]/tbody/tr[{i}]/td[1]').find_element_by_tag_name(
                    "a").get_attribute("href")
            except:
                link = ''
            if link:
                self.browser.go_to(link)
                self.browser.wait_until_page_contains_element('//div[@id="business-case-pdf"]')
                self.browser.find_element('//div[@id="business-case-pdf"]').click()
                sleep(5)
                self.browser.go_to(url)
                self.browser.wait_until_page_contains_element('//*[@id="investments-table-object_length"]/label/select',
                                                              timeout=timedelta(seconds=20))
                self.browser.wait_until_page_contains_element('//*[@id="investments-table-object_length"]/label/select')
                self.browser.find_element('//*[@id="investments-table-object_length"]/label/select').click()
                self.browser.find_element('//*[@id="investments-table-object_length"]/label/select/option[4]').click()
            if link:
                check = self.match_pdf(uii_ids[i], investment_title[i])
                if check:
                    match = "pdf match"
                else:
                    match = "pdf not match"
            else:
                match = "--"
            pdf_match.append(match)
        data = {"uii": uii_ids,
                "bureau": bureau,
                "company": investment_title,
                "FY2021": total_FY2021,
                "agency_type": type_agency,
                "CIO rating": CIO_rating,
                "# of project": num_of_project,
                "PDF Match": pdf_match,
                }
        sv = self.files.create_workbook("output/uii table.xlsx")
        sv.append_worksheet("Sheet", data)
        sv.save()


if __name__ == "__main__":
    rob = ItDashboardGov()
    rob.scrape_agencies()
    rob.scrape_agency(-3)


