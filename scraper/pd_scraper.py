import pandas as pd
import requests
from bs4 import BeautifulSoup as bs

all_sections = ['io', 'general_functions', 'series',
                'frame', 'arrays', 'general_utility_functions', 'api/pandas.Series', 'api/pandas.DataFrame', 'plotting']


def parse_data(link):
    """Parse functions from the sidebar of the Pandas API documentation page.

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
        'li', class_=f'toctree-l{2 if "api" in link else 1} current active has-children')
    functions = [i.text.replace('\n', '') for i in current_section.findAll(
        'a', class_='reference internal')]

    data = {
        'section': [section]*len(functions),
        'function': functions
    }
    df = pd.DataFrame(data)
    return df


def parse_properties():
    """Parse all properties to differentiate whether the function is method or property/attribute

    Returns:
        list: List of all properties/attributes.
    """
    all_props = []
    for s in ['series', 'frame']:
        url = f"https://pandas.pydata.org/docs/reference/{s}.html"
        df = pd.concat(pd.read_html(url))
        # filter properties
        df = df.dropna(subset=[0])
        props = df[(~df[0].astype(str).str.contains('\('))][0].tolist()
        all_props.extend(props)
    return all_props


if __name__ == '__main__':
    all_df = []
    for s in all_sections:
        url = f"https://pandas.pydata.org/docs/reference/{s}.html"
        try:
            all_df.append(parse_data(url))
        except:
            print(f"Error parsing: {url}")
    df = pd.concat(all_df).reset_index(drop=True)
    # identify method or property
    all_props = parse_properties()
    df['is_prop'] = df['function'].apply(
        lambda x: True if any([p in x for p in all_props]) else False)
    # output csv
    df.to_csv('../data/all_functions.csv', index=False)
