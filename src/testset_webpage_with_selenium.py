""" A set of Selenium/Requests test cases against the Dog API """

import sys
import logging
import json
import random
import unittest
import requests
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
#from selenium.webdriver import Chrome
#from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.common.by import By
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions
import utils.utils as utils

class TestSuiteDogAPIWebSelenium(unittest.TestCase):
    """
    A suite of test cases to test the Dog API
    """

    def setUp(self):
        """
        Always executed before test case is run. Provides required test case
        setup.
        """

        # set up logger for test cases, catch sys.stdout output
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            #level=logging.DEBUG,
            level=logging.INFO,
            datefmt='%Y-%m-%d,%H:%M:%S'
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        self.handler = logging.StreamHandler(sys.stdout)
        self.logger.addHandler(self.handler)
        self.home_page_https = 'https://dog.ceo/dog-api'
        self.home_page_http = 'http://dog.ceo/dog-api'
        opts = Options()
        opts.headless = True
        #opts.add_experimental_option('detach', True)
        #opts.add_argument('--disable-gpu')
        #self.browser = Firefox(
        #    executable_path=r"C:\WebDriver\bin\geckodriver.exe"#, options=opts
        #)
        #self.browser = Chrome(
        #    executable_path=r"C:\WebDriver\bin\chromedriver.exe", options=opts
        #)
        self.browser = Firefox(options=opts) # if webdrvr executable in PATH
        # DEBUG, no headless
        self.browser.implicitly_wait(5)
        #self.timeout = 10

    def tearDown(self):
        """
        Always executed after test case is finished, regardless of success or
        failure. Provides required test case cleanup/teardown.
        """

        # tear down test case and logger
        self.browser.quit()
        self.handler.close()
        self.logger.removeHandler(self.handler)

    def _go_to_documentation_page_from_home_page(self):
        """
        Provides a quick way to navigate to the documentation page from the
        home page, i.e.
        "https://dog.ceo/dog-api" -> "https://dog.ceo/dog-api/documentation"
        """

        link_text = 'Documentation'
        self.browser.get(self.home_page_https)
        doc_elem = self.browser.find_element_by_link_text(link_text)
        self.assertIsNotNone(doc_elem)
        self.assertEqual(doc_elem.text, link_text)
        doc_elem.click()
        self.assertEqual(
            self.browser.current_url.rstrip('/'),
            f'{self.home_page_https}/{link_text.lower()}'
        )

    def _get_ep_links_from_documentation_page(self):
        """
        Leverages selenium webdriver to retrieve a list of all API links from
        top of page, assert the returned values match the expected values,
        then returns them to the method caller

        :return: The retrieved list of links from documentation page
        :rtype: list
        """

        expect_ep_lnks_lst = [
            'https://dog.ceo/dog-api/documentation',
            'https://dog.ceo/dog-api/documentation/random',
            'https://dog.ceo/dog-api/documentation/breed',
            'https://dog.ceo/dog-api/documentation/sub-breed',
            'https://dog.ceo/dog-api/breeds-list'
        ]
        self._go_to_documentation_page_from_home_page()
        ep_doc_lst = self.browser.find_elements_by_xpath(
            '//ul[@class="endpoints-list"]/li/a'
        )
        self.assertIsNotNone(ep_doc_lst)
        ep_doc_lnks = [elem.get_attribute('href') for elem in ep_doc_lst]
        self.assertIsNotNone(ep_doc_lnks)
        self.assertEqual(ep_doc_lnks, expect_ep_lnks_lst)

        return ep_doc_lnks

    def _get_endpoint_from_page(self, url, expect_ep):
        """
        Retrieves the full API endpoint path that is shown on the page, i.e.
        https://dog.ceo/api/breeds/image/random, then asserts the returned
        value matches the expected value, before returning it to the method
        caller

        :param url: The url to go to in the browser
        :type url: str
        :param expect_ep: The expected endpoint to assert against, i.e.
                          "/breed/hound/list"
        :type expect_ep: str
        :return: The returned endpoint from the page
        :rtype: str
        """

        expect_home_page = \
            f'{self.home_page_https.replace("dog-api", "api")}/'\
            f'{expect_ep.lstrip("/").rstrip("/")}'
        self.browser.get(url)
        ep_elem = self.browser.find_element_by_xpath(
            '//span[@class="code"]'
        )
        self.assertIsNotNone(ep_elem)
        self.assertIsNotNone(ep_elem.text)
        self.assertEqual(ep_elem.text, expect_home_page)

        return ep_elem.text

    def _get_all_availabe_endpoints_from_page(self):
        """
        Retrieves the "/breeds/list/all" endpoint from the documentation page,
        executes it and converts the json formatted string to a dictionary.
        The dictionary is then used to compile a list of all possible breed
        and sub-breed endpoints and returns then as one large list.

        :return: The list of all possible available /breed and /sub-breed
                 endpoints
        :rtype: list
        """

        ep_doc_lnks = self._get_ep_links_from_documentation_page()
        lst_all_ep = self._get_endpoint_from_page(
            ep_doc_lnks[0], '/breeds/list/all'
        )
        json_data = self._do_request(lst_all_ep)

        return utils.get_all_available_breed_endpoints_from_list_all(
            self.home_page_https.replace('dog-api', 'api'), json_data
        )

    def _try_subscribe_with_email_value(self, email_val, expect_err_msg):
        """
        Attempts to use the subscribe via email using the page form.
        Attempting a subscription opens a new window_handle/tab in the
        browser where the check happens.

        :param email_val: The email value to be submitted to the form
        :type email_val: str
        :param expect_err_msg: The expected error message to assert is
                               returned to the user
        :type expect_err_msg: str
        """

        self.browser.get(self.home_page_https)
        main_url = self.browser.current_url
        signup_element = self.browser.find_element_by_id('mce-EMAIL')
        self.assertIsNotNone(signup_element)
        join_button = self.browser.find_element_by_id(
            'mc-embedded-subscribe'
        )
        self.assertIsNotNone(join_button)
        self.assertEqual(len(self.browser.window_handles), 1)
        main_window = self.browser.current_window_handle
        signup_element.send_keys(email_val)
        join_button.click()
        self.assertEqual(len(self.browser.window_handles), 2)
        other_window = self.browser.window_handles[-1]
        self.browser.switch_to.window(other_window)
        err_feedbck = self.browser.find_element_by_xpath(
            '//div[@class="feedback error"]'
        )
        self.assertIsNotNone(err_feedbck)
        err_text = err_feedbck.find_element_by_xpath(
            '//div[@class="errorText"]'
        ).text
        self.assertEqual(err_text, expect_err_msg)
        self.browser.switch_to.window(main_window)
        self.assertEqual(self.browser.current_url, main_url)
        self.browser.switch_to.window(other_window)
        # close the new tab here
        self.browser.close()

    def _get_raw_data_from_page(self, page_url):
        """
        Retrieves the raw json data from the browser after an endpoint
        is executed in the browser

        :param page_url: The endpoint url to execute in the browser
        :type page_url: str
        :return: The JSON formatted data as a python dictionary
        :rtype: dict
        """

        self.browser.get(page_url)
        self.browser.find_element_by_id('rawdata-tab').click()
        raw_data = self.browser.find_element_by_xpath(
            '//pre[@class="data"]'
        ).text
        self.assertIsNotNone(raw_data)
        json_data = json.loads(raw_data)
        self.assertIsNotNone(json_data)
        self.assertTrue('message' in json_data.keys())
        self.assertTrue('status' in json_data.keys())

        return json_data

    def _do_request(self, endpoint):
        """
        Performs a GET request to an endpoint using requests module

        :param endpoint: The endpoint to GET
        :type endpoint: str
        :return: JSON formatted response as a python dictionary
        :rtype: dict
        """

        response = requests.get(endpoint)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Content-Type' in response.headers.keys())
        self.assertEqual(
            response.headers['Content-Type'], 'application/json'
        )
        self.assertIsNotNone(response.text)
        json_response = json.loads(response.text)
        self.assertIsNotNone(json_response)
        self.assertTrue('message' in json_response.keys())
        self.assertTrue('status' in json_response.keys())
        self.assertEqual(json_response['status'], 'success')

        return json_response

    def test_get_home_page_over_http_https_redirect(self):
        """
        Tests that http://dog.ceo/dog-api redirects to https://dog.ceo/dog-api

        Test Steps:
            1. Open the browser and go to http://dog.ceo/dog-api
            2. Assert page is redirected to https://dog.ceo/dog-api
            3. Perform step 1 in requests
            4. Assert redirect 301 HTTP code

        Expected Result:
            The browser redirects http://dog.ceo/dog-api to
            https://dog.ceo/dog-api
        """

        self.browser.get(self.home_page_http)
        self.assertNotEqual(
            self.browser.current_url.rstrip('/'),
            self.home_page_http
        )
        self.assertEqual(
            self.browser.current_url.rstrip('/'),
            self.home_page_https
        )
        self.browser.get(self.home_page_https)
        self.assertEqual(
            self.browser.current_url.rstrip('/'),
            self.home_page_https
        )
        response = requests.get(self.home_page_http, allow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.history)
        for res in response.history:
            self.assertEqual(res.status_code, 301)
        self.assertEqual(
            str(response.url).rstrip('/'), self.home_page_https
        )

    def test_do_fetch_on_page_check_image_updated(self):
        """
        Use the Fetch button on the page and check a new image is loaded

        Test Steps:
            1. Go to homepage
            2. Locate the JSON element on the page
            3. Retrieve the data and convert to a dictionary
            4. Locate the get-dog button element
            5. Click the button element
            6. Retrieve the JSON element from the page again
            7. Assert the 'message' field has changed to a new image link

        Expected Result:
            Fetch button updated the image displayed on the page
        """

        self.browser.get(self.home_page_https)
        # first line contains JSON\n title so need to strip it from string
        # before json loads
        img_element = self.browser.find_element_by_class_name('json')
        self.assertIsNotNone(img_element)
        current_displayed_image = json.loads(img_element.text.strip('JSON\n'))
        self.assertTrue('message' in current_displayed_image.keys())
        self.assertTrue('status' in current_displayed_image.keys())
        self.assertEqual(current_displayed_image['status'], 'success')
        button_element = self.browser.find_element_by_xpath(
            '//a[@class="get-dog button"]'
        )
        self.assertIsNotNone(button_element)
        button_element.click()
        img_element = self.browser.find_element_by_class_name('json')
        fetched_new_image = json.loads(img_element.text.strip('JSON\n'))
        self.assertTrue('message' in current_displayed_image.keys())
        self.assertTrue('status' in current_displayed_image.keys())
        self.assertEqual(current_displayed_image['status'], 'success')
        self.assertNotEqual(
            current_displayed_image['message'],
            fetched_new_image['message']
        )

    def test_navigate_to_random_endpoint_choice_go_back_refresh(self):
        """
        Navigate to any random page from the home page, refresh the page
        then return back to the home page.

        Test Steps:
            1. Get all available links from /documentation page
            2. Store the current url
            3. Choose one random page from the list and navigate to it
            4. Refresh the page and assert url remains unchanged
            5. Go back to the original page
            6. Assert new page is equal to the original chosen page

        Expected Result:
            Dog API website behaves as expected on page refresh and go back
        """

        random_endpoint = None
        # don't care which link is chosen to navigate to
        # randomly picking one
        ep_doc_lnks = self._get_ep_links_from_documentation_page()
        current_url = self.browser.current_url
        self.browser.refresh()
        refreshed_url = self.browser.current_url
        self.assertEqual(current_url, refreshed_url)
        # remove link from list if it's already the current page
        # this will avoid it being picked randomly from the list
        ep_doc_lnks = [
            epdl
            for epdl in ep_doc_lnks
            if self.browser.current_url.rstrip('/') != epdl
        ]
        random_endpoint = random.choice(ep_doc_lnks)
        self.browser.get(random_endpoint)
        self.assertEqual(
            self.browser.current_url.rstrip('/'), random_endpoint
        )
        self.assertNotEqual(self.browser.current_url, refreshed_url)
        self.browser.back()
        self.assertEqual(self.browser.current_url, refreshed_url)

    def test_check_page_title_metadata(self):
        """
        Checks the home page's title, url, description etc. meta values

        Test Steps:
            1. Navigate to home page
            2. Check the title property matches the expected text
            3. Check the url meta tag matches the page url
            4. Check the description meta tag matches the expected text

        Expected Result:
            Meta information on page matches expected data
        """

        expect_text = 'Dog API'
        self.browser.get(self.home_page_https)
        # title page
        page_title = self.browser.title
        self.assertEqual(page_title, expect_text)
        meta_title = self.browser.find_element_by_xpath(
            '//meta[@property="og:title"]'
        )
        self.assertIsNotNone(meta_title)
        self.assertEqual(meta_title.get_attribute('content'), expect_text)
        self.assertEqual(meta_title.get_attribute('content'), page_title)
        meta_url = self.browser.find_element_by_xpath(
            '//meta[@property="og:url"]'
        )
        self.assertIsNotNone(meta_url)
        self.assertEqual(
            meta_url.get_attribute('content'), self.home_page_https
        )
        # meta description
        meta_desc = self.browser.find_element_by_xpath(
            '//meta[@name="description"]'
        )
        self.assertIsNotNone(meta_desc)
        self.assertTrue(expect_text in meta_desc.get_attribute('content'))

    def test_select_breed_from_breed_list_page_random(self):
        """
        Navigate to https://dog.ceo/dog-api/breeds-list and randomly choose a
        breed from the selection-box, click it and assert image updated

        Test Steps:
            1. Retrieve the https://dog.ceo/dog-api/breeds-list from the
               documentation page and navigate to it
            2. Retrieve the image element currently displayed in the browser
            3. Retrieve the dog-selector element and choose one at random
            4. Click the selected breed option
            5. Check the image element has been updated

        Expected Result:
            The image is updated to the appropriate breed choice
        """

        self.browser.get(self._get_ep_links_from_documentation_page()[-1])
        img_element = self.browser.find_element_by_xpath(
            '//div[@class="demo-image"]'
        )
        self.assertIsNotNone(img_element)
        src_imgs = img_element.find_elements_by_tag_name('img')
        self.assertIsNotNone(src_imgs)
        self.assertEqual(len(src_imgs), 1)
        src_img_value = src_imgs[0].get_attribute('src')
        select_element = self.browser.find_element_by_xpath(
            '//select[@class="dog-selector"]'
        )
        self.assertIsNotNone(select_element)
        all_options = select_element.find_elements_by_tag_name('option')
        self.assertIsNotNone(all_options)
        self.assertTrue(len(all_options) > 1)
        random.choice(all_options).click()
        src_imgs = img_element.find_elements_by_tag_name('img')
        self.assertIsNotNone(src_imgs)
        self.assertEqual(len(src_imgs), 1)
        new_img_value = src_imgs[0].get_attribute('src')
        self.assertNotEqual(src_img_value, new_img_value)

    def test_check_cookies_available_across_site(self):
        """
        Verifies the information on the site cookies and checks cookies are
        available across the site

        Test Steps:
            1. Retrieve the cookies on the home page
            2. Check the domain information on the cookie matches the dog.ceo
               domain
            3. Store the cookie IDs for GA and CF
            4. Navigate to another page
            5. Verify cookie IDs have not changed

        Expected Result:
            Cookies are available across the site

        Note:
            Is possible test could be extended to verify expiration date as
            well
        """

        # test could also include cookie expiration by getting time at test
        # start then verifying expiration is 24 hours from current time
        def get_cookies():
            """
            [summary]

            :return: [description]
            :rtype: [type]
            """

            cf_uid = None
            ganalytics_uid = None
            cookies = self.browser.get_cookies()
            for dct in cookies:
                if dct['name'] == '_gid': # google analytics cookie id
                    ganalytics_uid = dct['value']
                elif dct['name'] == '__cfduid': # cloudflare cookie id
                    cf_uid = dct['value']

            return cookies, cf_uid, ganalytics_uid

        self.browser.get(self.home_page_https)
        cookies, cf_uid_1, ganalytics_uid_1 = get_cookies()
        self.assertIsNotNone(cf_uid_1)
        self.assertIsNotNone(ganalytics_uid_1)
        for dct in cookies:
            self.assertTrue('domain' in dct.keys())
            # strip top level '.' from domain, verify domain in page
            # address
            self.assertTrue(
                dct['domain'].lstrip('.') in self.home_page_https
            )
        # navigate to a new page
        self.browser.find_element_by_link_text('Documentation').click()
        _, cf_uid_2, ganalytics_uid_2 = get_cookies()
        self.assertIsNotNone(cf_uid_2)
        self.assertIsNotNone(ganalytics_uid_2)
        self.assertEqual(cf_uid_1, cf_uid_2)
        self.assertEqual(ganalytics_uid_1, ganalytics_uid_2)

    def test_subscribe_via_email_invalid_email_syntax_given(self):
        """
        Attempts to subscribe via invalid email

        Test Steps:
            1. Attempt to subscribe using an email using invalid syntax
            2. Verify error message matches the expected error message

        Expected Result:
            Appropriate error message regarding an invalid email
        """

        invalid_syntax_email = 'example1.3'
        expect_err_msg = 'An email address must contain a single @'
        self._try_subscribe_with_email_value(
            invalid_syntax_email, expect_err_msg
        )

    def test_subscribe_via_email_invalid_email_given(self):
        """
        Attempts to subscribe via a fake email, that is syntactically valid

        Test Steps:
            1. Attempt to subscribe using an email using a fake email
            2. Verify error message matches the expected error message

        Expected Result:
            Appropriate error message regarding a fake email
        """

        invalid_syntax_email = 'example@example.com'
        expect_err_msg = 'This email address looks fake or invalid. '\
                         'Please enter a real email address.'
        self._try_subscribe_with_email_value(
            invalid_syntax_email, expect_err_msg
        )

    def test_get_request_against_every_available_endpoint(self):
        """
        Tests every available breed endpoint that should be available.
        Does not validate data, only a 200 HTTP response

        Test Steps:
            1. Retrieve a list of all available breed endpoints
            2. Loop through each endpoint in the list and perform a GET
               request
            3. Assert an HTTP 200 response code

        Expected Result:
            All endpoints are live and contactable
        """

        # does not validate response json data
        available_ep_lst = self._get_all_availabe_endpoints_from_page()
        for ep_ in available_ep_lst:
            response = requests.get(ep_)
            self.assertEqual(response.status_code, 200)

    def test_validate_json_response_matches_page(self):
        """
         Tests that the JSON data shown on the '/documentation/random' page
         matches the JSON data returned from a GET request

        Test Steps:
            1. Retrieve all endpoints available, remove any endpoint that is
               /random
            2. Choose an endpoint at random from the available list
            3. Access the endpoint in the browser and retrieve the raw JSON
               data
            4. Perform a GET request with requests and retrieve the JSON
               response
            5. Assert both data sets match

        Expected Result:
            Raw data from endpoint shown in the browser match the returned
            data from a requests.get()

        Note:
            It's also possible to retrieve the JSON raw data from the
            '/breed/hound' (/documentation/breed page), however that only
            tests /hound breed, as that is the only one listed on the page
        """

        available_ep_lst = self._get_all_availabe_endpoints_from_page()
        # remove the /random endpoints while compiling the endpoints list
        # as /random will not guarantee the same endpoint choice between
        # requests for api_ep
        api_ep_compiled_list = [
            ep
            for ep in available_ep_lst
            if '/random' not in ep
        ]
        self.assertIsNotNone(api_ep_compiled_list)
        api_ep = random.choice(api_ep_compiled_list)
        self.assertIsNotNone(api_ep_compiled_list)
        json_data = self._get_raw_data_from_page(api_ep)
        json_response = self._do_request(api_ep)
        self.assertEqual(json_data, json_response)

    def test_any_random_endpoint(self):
        """
         Test any /breed/images/random/{number} endpoint returns the list of
         images. Test uses a large number to begin with, but not all breeds
         would have such a large set of pictures, so the test validates list
         length is such a case.

        Test Steps:
            1. Get all available /breed endpoints
            2. Get only /random endpoints from the list, removing
               "/breeds/image/random" collections endpoint which is capped at
               50 max
            3. Perform a request toward the endpoint
            4. Check the length of the returned image list is equal to the
               requested number of random images

        Expected Result:
            The /random/{number_of_imgs} endpoint returns the requested number
            of images or the most it has available otherwise
        """

        # this could also be random.randint(1, 100)
        number_of_random_imgs = 100
        available_ep_lst = self._get_all_availabe_endpoints_from_page()
        # any random endpoint works for this test except /breed/image/random
        # covered in next test with max 50 limit
        api_ep_compiled_list = [
            ep
            for ep in available_ep_lst
            if '/random' in ep and ep != \
                'https://dog.ceo/api/breeds/image/random'
        ]
        # not all breeds have large numbers of pictures
        # solution is to get the available pictures list beforehand
        # and assert json_data matches that list, using requests
        random_ep = \
            f'{random.choice(api_ep_compiled_list)}/'\
            f'{str(number_of_random_imgs)}'
        json_response = self._do_request(random_ep)
        if len(json_response['message']) != number_of_random_imgs:
            number_of_random_imgs = len(json_response['message'])
        json_data = self._get_raw_data_from_page(random_ep)
        self.assertEqual(len(json_data['message']), number_of_random_imgs)

    def test_random_collection_max_50(self):
        """
        Tests retrieving a collection of random dog images from /breeds/random
        by providing a number larger that 50; 50 images being the max
        available

        Test Steps:
            1. Do a GET at 'https://dog.ceo/api/breeds/image/random/100'
            2. Verify returned list of images exists and is only length 50

        Expected Result:
            Random collection of images returned is 50, if provided with a
            larger that 50 request
        """

        number_of_random_imgs = 100
        # endpoint could be pulled from the same list as above tests, but no
        # need to process them for one link that never changes
        page_url = \
            'https://dog.ceo/api/breeds/image/random/'\
            f'{number_of_random_imgs}'
        json_data = self._get_raw_data_from_page(page_url)
        self.assertNotEqual(len(json_data['message']), number_of_random_imgs)
        self.assertEqual(len(json_data['message']), 50)

if __name__ == '__main__':
    unittest.main()
