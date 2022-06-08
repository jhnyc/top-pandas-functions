import pandas as pd
import requests
from bs4 import BeautifulSoup as bs

all_sections = ['arrays.ndarray', 'generated/numpy.ndarray']


def parse_data(link):
    """Parse functions from the sidebar of the Numpy API documentation page.

    Args:
        link (str): Pandas API documentation page.

    Returns:
        pd.DataFrame: Pandas DataFrame with the parsed functions.
    """
    response = requests.get(link)
    soup = bs(response.content)
    section = soup.findAll('a', class_='current reference internal')[
        0].text.replace('\n', '')
    current_section = soup.find(
        'li', class_=f'toctree-l{2 if "generated" in link else 1} current active has-children')
    functions = [i.text.replace('\n', '') for i in current_section.findAll(
        'a', class_='reference internal')]

    data = {
        'section': [section]*len(functions),
        'function': functions
    }
    df = pd.DataFrame(data)
    return df


def parse_properties():
    url = "https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html"
    response = requests.get(url)
    soup = bs(response.content)
    _ = soup.findAll(
        'dl', class_="field-list simple")[1].findAll('a', class_="reference internal")
    all_attr = [i['title'] for i in _]
    return all_attr


if __name__ == '__main__':
    all_df = []
    for s in all_sections:
        url = f"https://numpy.org/doc/stable/reference/{s}.html"
        try:
            all_df.append(parse_data(url))
        except:
            print(f"Error parsing: {url}")
    df = pd.concat(all_df).reset_index(drop=True)
    df['function'] = df['function'].str.strip()
    df = df[df['function'].str.contains('numpy.')].reset_index(drop=True)
    # identify method or property
    all_props = parse_properties()
    df['is_prop'] = df['function'].apply(
        lambda x: True if any([p in x for p in all_props]) else False)
    # output csv
    df.to_csv('../data/np_array_methods.csv', index=False)
