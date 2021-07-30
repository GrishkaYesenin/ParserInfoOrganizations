import requests
from bs4 import BeautifulSoup as BS

import csv

HOST = 'https://zakupki.gov.ru'

URL = 'https://zakupki.gov.ru/epz/rkpo/search/results.html'

HEADERS = {
    "accept": "*/*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) /"
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
}

FEATURES = ('Сокращенное наименование', 'Адрес места нахождения', 'Адрес электронной почты',
            'Контактные телефоны', 'Лицо, имеющее право действовать без доверенности от имени юридического лица',
            'Специализация')


def fetch_card_detail_links(pages=1):
    """
    Fetching links for card detail info
    :param pages:
    :return: list of links
    """

    links = []

    for num_page in range(1, pages + 1):

        # TODO: add try expect

        postfix = f'?searchString=&morphology=on&search-filter=Дате+размещения&savedSearchSettingsIdHidden=/' \
                  f'&sortBy=UPDATE_DATE/&pageNumber={num_page}&sortDirection=false&recordsPerPage=_10/' \
                  f'&showLotsInfoHidden=false&active=on&archival=on&ownerIdOrg=&customerFz94id=&customerTitle=/' \
                  f'&preselectionNumber=&selectedSubjectsIdHidden=&selectedSubjectsIdNameHidden=%7B%7D&worktypeIds=/' \
                  f'&worktypeNames=&worktypeIdsParent=&priceFrom=&priceTo=&entryRkpoDateFrom=&entryRkpoDateTo=/' \
                  f'entrySvrDateFrom=&entrySvrDateTo=&expirationRkpoDateFrom=&expirationRkpoDateTo=/' \
                  f'&expirationSvrDateFrom=&expirationSvrDateTo=&publishDateFrom=&publishDateTo=&updateDateFrom=/' \
                  f'&updateDateTo=&rejectReasonIdHidden=&rejectReasonIdNameHidden=%7B%7D&customerPlace=/' \
                  f'&customerPlaceCodes='

        url = URL + postfix

        req = requests.get(url=url, headers=HEADERS)
        soup = BS(req.text, 'lxml')

        for elem in soup.find_all(class_="search-registry-entry-block"):
            elem = elem.find(class_="registry-entry__header-mid__number").find("a")
            link = HOST + elem.get('href')
            links.append(link)
    return links


def get_dict_info_organization(link):
    info_dict = dict()
    req = requests.get(url=link, headers=HEADERS)
    soup = BS(req.text, 'lxml')

    try:
         info_dict['Специализация'] = soup.find(class_="cardMainInfo row").find(text="Предмет электронного аукциона").parent.parent.find(class_="cardMainInfo__content").text.strip()
    except Exception:
        pass

    for elem in soup.find_all(class_="blockInfo__section section"):
        try:
            feature = elem.find(class_="section__title").text.strip()
            if feature in FEATURES:
                info_dict[feature] = elem.find(class_="section__info").text.strip()
        except Exception:
            pass

    return info_dict


if __name__ == '__main__':

    with open('data.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FEATURES)
        detail_links = fetch_card_detail_links(pages=100)
        for link in detail_links:
            try:
                writer.writerow(get_dict_info_organization(link))
            except Exception:
                pass