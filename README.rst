===================
Dog API Test Suite
===================

| A small suite of test cases related to `Dog API <https://dog.ceo/dog-api>`_.
| Tests are writted in **Python 3** (*Python 3.8.4*).
| Functional tests use the `Selenium WebDriver <https://www.selenium.dev/>`_, `Selenium-Python Library <https://selenium-python.readthedocs.io/>`_ and `unittest <https://docs.python.org/3/library/unittest.html>`_.
| Some tests also make use of `requests <https://requests.readthedocs.io/en/master/>`_.
| Load tests utilise `Locust <https://locust.io/>`_.
| Test Case Documentation in `reStructuredText <https://docutils.sourceforge.io/docs/user/rst/quickref.html>`_ and generated using `Sphinx <https://www.sphinx-doc.org/en/master/>`_ in HTML format.

Installation
------------
- Requires `geckodriver <https://github.com/mozilla/geckodriver/releases>`_

.. code-block:: text

  tar -zxvf </path/to/downloaded/tarball.tar.gz> -C </path/to/extracted/bin/path>
  export PATH=${PATH}:</path/to/extracted/bin/path>

- Install Python library requirements with `pip <https://pypi.org/project/pip/>`_

.. code-block:: text

  pip install -r requirements.txt

Run Tests
---------

- Run all Selenium tests

.. code-block:: text

  python src/testset_webpage_with_selenium.py

- Run a single test case

.. code-block:: text

  python src/testset_webpage_with_selenium.py TestSuiteDogAPIWebSelenium.test_get_home_page_over_http_https_redirect
  python src/testset_webpage_with_selenium.py TestSuiteDogAPIWebSelenium.test_do_fetch_on_page_check_image_updated
  python src/testset_webpage_with_selenium.py TestSuiteDogAPIWebSelenium.test_subscribe_via_email_invalid_email_given

- Run Locust load tests

.. code-block:: text

  locust -f src/testset_load_with_locust.py --list
  locust -f src/testset_load_with_locust.py DogApiUser --user <no. of users to simulate> --hatch-rate <user hatch rate> --headless --run-time <how long to run for i.e. 1m/3h> --host https://dog.ceo

Suite Improvements
------------------

- Suite does not provide 100% coverage
- Avoided any testing round the Paypal donation system
- Tested for invalid email subcriptions, but not tested for valid email subscriptions
- Not all site links tested
- A few test cases utilise random library to randomly pick certain API endpoints to test against, rather than test each possible API endpoint. This was to save time while provide extra coverage, though should not be condired standard practice.
- Selenium test suite contains a *logger* to capture *sys.stdout* which was used for DEBUG purposes. All logging was removed from test cases but can be included back in if required for test logs.
- Selenium suite calls utils.get_all_available_breed_endpoints_from_list_all() in many test cases, but it could be optimised by calling it once during a setUpClass() method and populate the list once for all tests. Would save some time during test run.

Improvement Suggestions from Functional Selenium Run
----------------------------------------------------

- Navigating to `Breeds List <http://dog.ceo/dog-api/breeds-list>`_ page, the *selection-box* appears, at first glance, to be a text box
- Navigating directly to Breeds List page does not seem enforce HTTPS, though it seems to be the case I could see as such. Navigating from any other page on the site to Breeds List seems ok.
- `By breed <https://dog.ceo/dog-api/documentation/sub-breed>`_ and `By sub-breed <https://dog.ceo/dog-api/documentation/sub-breed>`_ documentation only uses */breed/hound* in the examples. Consider adding a selection box, as in Breeds List above, instead; or make it clear that more breeds exist as it's not clearly apparent at first glance.
- Page Title says *Dog API* regardless of what sub-page on the site the user has currently loaded.

Locust Load Analysis
---------------------------------------------------
- Without defined KPIs it was tough to know what should be expected from the results
- Ran the following tests:
   - **1 user** executing requests for **1 minute**
   - **10 users** at a **hatch rate of 1** (*1 user added every second*) for *4 minutes*
   - **20 users** at a **hatch rate of 3** for **10 minutes**
   - **45 users** at a **hatch rate of 3** for  for **10 minutes**
   - **100 users** at a **hatch rate of 5** for **30 minutes**
   - **wait_time** for each user was **between 3 and 9 seconds**
- For CircleCI specified only the 1 user for 1 minute due to the limitations for free users
- Results:
   - Throughout all the runs there were **0 failures**, all requests were successful
   - As expected, tasks with higher weights appeared more in the list of requests (more users chose to perform those tasks), so *images/random/<some number>* appear much more often that the rest with a weight of 4
   - /breeds/list/all is executed on_start() by all users
   - During the 100 users run, requests per second could reach up 19 (aggregated results), but seems to hover between 12 and 16 for the most part