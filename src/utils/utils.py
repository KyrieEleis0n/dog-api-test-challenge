""" A common method that both Selenium test cases and Locust task use """

def get_all_available_breed_endpoints_from_list_all(url, list_all_dict):
    """
    Given a url, i.e. https://dog.ceo/api, and a JSON formatted python
    dictionary result from a GET at /breeds/list/all, compile a list of
    all available endpoints for all breeds and sub-breeds of dogs.

    :param url: The url to attach to the endpoints, i.e. https://dog.ceo/api
    :type url: str
    :param list_all_dict: A dictionary with all breeds retrieved from
                          json.loads(GET(https://dog.ceo/api/breeds/list/all))
    :type list_all_dict: dict
    :return: A compiled list of all available breed and sub-breed endpoints,
             including /list, /images, /random
    :rtype: list
    """

    all_endpoints_list = list()
    breeds_ep_dct = dict()
    breeds = list_all_dict['message']
    for breed in breeds:
        breed_api = f'{url}/breed/{breed}'
        breeds_ep_dct[breed_api] = list()
        if breeds[breed]:
            for bred in breeds[breed]:
                sub_breed_api = bred
                if '/list' not in breeds_ep_dct[breed_api]:
                    breeds_ep_dct[breed_api].append('/list')
                img_sub_breed = f'/{sub_breed_api}/images'
                breeds_ep_dct[breed_api].append(img_sub_breed)
                img_rand_sub_breed = f'{img_sub_breed}/random'
                breeds_ep_dct[breed_api].append(img_rand_sub_breed)
        else:
            img_breed = '/images'
            breeds_ep_dct[breed_api].append(img_breed)
            img_rand_breed = f'{img_breed}/random'
            breeds_ep_dct[breed_api].append(img_rand_breed)

    for ep_k in breeds_ep_dct:
        for ep_v in breeds_ep_dct[ep_k]:
            all_endpoints_list.append(f'{ep_k}{ep_v}')

    return all_endpoints_list
