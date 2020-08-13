""" Locust file for Dog API testing """

import json
import random
from locust import HttpUser, task, between
import utils.utils as utils


class DogAPIUser(HttpUser):
    """
    HttpUser class for Locust, simulated users of Dog API
    """

    wait_time = between(3, 9)

    def __init__(self, *args, **kwargs):
        """
        Inherits from HttpUser and extends with additional parameters for
        the tasks to be executed
        """

        super(DogAPIUser, self).__init__(*args, **kwargs)
        self.api_endpoint = 'https://dog.ceo/api'
        self.list_breeds_ep = '/breeds/list/all'
        self.all_breeds_ep = list()

    def _get_random_endpoint_from_list_by_substring(self, substr,
                                                    has_substr=True):
        """
        A method the return a specific endpoint by substr from all
        endpoints

        :param substr: The substring to search the list for, i.e. /random
        :type substr: str
        :param has_substr: True if should match substring. If False will
                           return a sublist that doesn't match the subtring
        :type substr: bool
        :return: The sublist specified by the substring
        :rtype: list
        """

        ab_ep = self.all_breeds_ep

        return random.choice(
            [api_ep for api_ep in ab_ep if substr in api_ep]) \
                if has_substr else \
                    random.choice(
                        [api_ep for api_ep in ab_ep if substr not in api_ep])

    @task(3)
    def list_by_breed(self):
        """
        Randomly chooses a sub-breed from the breed list returned by
        /breed/list
        """

        chosen_endpoint = \
            self._get_random_endpoint_from_list_by_substring('/list')
        self.client.get(chosen_endpoint)

    @task(2)
    def list_all_breeds(self):
        """
        Lists all breeds from /breeds/list/all
        """
        self.client.get(f'{self.api_endpoint}{self.list_breeds_ep}')

    @task(3)
    def get_random_image(self):
        """
        Gets a single /random image
        """

        chosen_endpoint = \
            self._get_random_endpoint_from_list_by_substring('/random')
        self.client.get(chosen_endpoint)

    @task(4)
    def get_random_images(self):
        """
        Gets a list of images from /random endpoint using a random range
        from 2 to 60
        """

        random_no_images = random.randint(2, 60)
        chosen_endpoint = \
            self._get_random_endpoint_from_list_by_substring('/random')
        self.client.get(f'{chosen_endpoint}/{random_no_images}')

    @task(2)
    def get_list_of_images(self):
        """
        Gets a list of images from the /images endpoint
        """

        chosen_endpoint = \
            self._get_random_endpoint_from_list_by_substring('/images')
        self.client.get(chosen_endpoint)

    def on_start(self):
        """
        User performs the actions before any tasks are executed
        """

        # gets all available /breed && /sub-breed endpoints such as
        # /list, /images, /random
        response = self.client.get(
            f'{self.api_endpoint}{self.list_breeds_ep}'
        )
        self.all_breeds_ep = \
            utils.get_all_available_breed_endpoints_from_list_all(
                self.api_endpoint, json.loads(response.content))
