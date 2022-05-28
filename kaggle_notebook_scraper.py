import shutil
import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import time
import os
from tqdm import tqdm  # to show download status bar
import yaml
import warnings
warnings.filterwarnings("ignore")


def get_code_links(start=1, page=10):
    """Visit the pages and get all the notebook links and names

    Args:
        page (int, optional): Number of pages to visit. Defaults to 10.
        save (bool, optional): Whether to save the list of links to a json file. Defaults to False.

    Returns:
        dict: Url and name of the notebook.
    """
    options = webdriver.chrome.options.Options()
    options.add_argument('--headless')  # to run Chrome in headless mode
    driver = webdriver.Chrome(
        '/Users/Johnny/Desktop/Python/chromedriver', chrome_options=options)

    # load base url from config file
    with open("kaggle_notebook_scraper_config.yaml", 'r') as f:
        BASE_URL = yaml.safe_load(f)['base_url']

    output = {}
    for i in range(start, start+page+1):
        url = BASE_URL.format(page=i)
        driver.get(url)
        time.sleep(5)
        soup = bs(driver.page_source)
        list_ = driver.find_element_by_xpath(
            '//*[@id="site-content"]/div[7]/div').get_attribute("outerHTML")
        classname = " ".join(bs(list_).find('div')['class'])
        container = soup.find('div', class_=f"{classname}")
        all_href = [i['href'] for i in container.findAll('a')]
        code_name_href = {"https://www.kaggle.com"+i: i.split(
            '/')[-1] for i in all_href if '/code' in i and 'comments' not in i}
        output.update(code_name_href)
    return output


def download_nb_from_id(_id, name, folder_dir='codes'):
    """Download a Kaggle notebook given the notebook id.

    Args:
        _id (str): Notebook id.
        folder_dir (str): Folder to save the notebook. Defaults to 'codes'.

    Returns:
        str: Path to the downloaded notebook.
    """
    url = f"https://www.kaggle.com/kernels/scriptcontent/{_id}/download"
    file = f'{_id}_{name}.ipynb'
    local_filename = os.path.join(folder_dir, file)
    with requests.get(url, stream=True) as r:
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    return local_filename


def get_nb_id_and_download(links):
    """Parse the notebook id from the notebook url and download the notebook.

    Args:
        links (dict): url-name pairs
    """
    existing_nb_ids = [i.split('_')[0]
                       for i in os.listdir('codes') if i.endswith('ipynb')]
    print("Downloading notebooks...")
    for url in tqdm(links):
        res = requests.get(url)
        soup = bs(res.content)
        _ = soup.find('link', rel="alternate")['href']
        # parse notebook id from the link
        _id = _.split('%')[-1][2:]
        # avoid redownloading the same file
        if _id not in existing_nb_ids:
            download_nb_from_id(_id, name=links[url])


if __name__ == '__main__':
    # get number of pages to download
    start_page = input('starting page: ').strip()
    start_page = 1 if start_page == '' else int(start_page)
    page = int(input('number of pages to download: '))
    # get all notebook links
    all_hrefs = get_code_links(start=start_page, page=page)
    # download all notebooks
    get_nb_id_and_download(all_hrefs)
    # complete
    print('Download completed!')
