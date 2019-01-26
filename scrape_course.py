import requests
from bs4 import BeautifulSoup

import time
import pickle
import json

def get_course_providers():
    url = 'https://www.mooc-list.com'
    response = requests.get(url)
    html = response.text

    soup = BeautifulSoup(html, 'lxml')

    res_links = []
    result_block = soup.find_all('div', attrs={'class': 'block-inner clearfix'})
    # result_block.reverse()
    for result in result_block:
        h3 = result.find('h3')
        if h3 is None:
            continue
        if h3.text == 'Active MOOC and Free Online Courses Providers:':
            links = result.find_all('a', href=True)
            for link in links:
                res_links.append(url + link['href'])
            break

    return res_links

def parse_result_page(url):
    root_url = 'https://www.mooc-list.com'
    response = requests.get(url)
    html = response.text

    soup = BeautifulSoup(html, 'lxml')

    results = []
    result_block = soup.find_all('div', attrs={'class': 'views-row views-row-1 views-row-odd views-row-first'})

    for res in result_block:
        res_d = dict()
        title_div = res.find('div', attrs={'class': 'views-field views-field-title'})
        link = title_div.find('a', href=True)
        if link is None:
            continue
        res_d['link'] = root_url + link['href']
        res_d['title'] = link.get_text()

        div = res.find('div', attrs={'class': 'views-field views-field-body'})
        p = div.find('p')
        if p is None:
            continue
        res_d['description'] = p.get_text()

        tags = []
        divs = res.find('div', attrs={'class': 'views-field views-field-field-categories'})
        for div in divs:
            a = div.find('a', href=True)
            if a is not None:
                tags.append({'tag':a.get_text(), 'url':root_url + a['href']})
        res_d['tags'] = tags
        results.append(res_d)
    return results

def parse_provider(provider_link):
    all_results = []
    i = 0
    page_url = provider_link + '?page=%d' % (i)
    results = parse_result_page(page_url)
    while len(results) > 0:
        print(i)
        all_results += results
        time.sleep(0.1)
        i += 1
        page_url = provider_link + '?page=%d' % (i)
        results = parse_result_page(page_url)
    return all_results

def parse_all_courses():
    providers = get_course_providers()

    all_courses = []
    for provider in providers:
        print(provider)
        courses = parse_provider(provider)
        all_courses += courses

        with open('data/mooc_list_courses.json', 'w') as f:
            json.dump(all_courses, f)
    return all_courses

def parse_course_page(url):
    root_url = 'https://www.mooc-list.com'
    response = requests.get(url)
    html = response.text

    soup = BeautifulSoup(html, 'lxml')
    res_d = dict()
    res_d['link'] = url

    h1 = soup.find('h1', attrs={'class': 'page-title'})
    if h1 is not None:
        res_d['title'] = h1.get_text()

    div = soup.find('div', attrs={'class': 'col-md-9 main-c'})
    if div is not None:
        ps = div.find_all('p')
        p_texts = [p.get_text() for p in ps]
        desc = '\n'.join(p_texts)
        res_d['description'] = desc

    div = soup.find('div', attrs={'class': 'field field-name-field-initiative field-type-taxonomy-term-reference field-label-hidden'})
    if div is not None:
        a = div.find('a', href=True)
        provider = {'text': a.get_text(), 'url': root_url + a['href']}
        res_d['provider'] = provider

    div = soup.find('div', attrs={'class': 'field field-name-field-university-entity field-type-taxonomy-term-reference field-label-hidden'})
    if div is not None:
        a = div.find('a', href=True)
        university = {'text': a.get_text(), 'url': root_url + a['href']}
        res_d['university'] = university

    div = soup.find('div', attrs={
        'class': 'field field-name-field-instructors field-type-taxonomy-term-reference field-label-hidden'})
    if div is not None:
        links = div.find_all('a', href=True)
        instructors = []
        for a in links:
            txt = a.get_text()
            if txt == 'N/A':
                continue
            instructor = {'text': txt, 'url': root_url + a['href']}
            instructors.append(instructor)
        res_d['instructors'] = instructors

    div = soup.find('div', attrs={'class': 'field field-name-field-categories field-type-taxonomy-term-reference field-label-hidden'})
    if div is not None:
        a = div.find('a', href=True)
        category = {'text': a.get_text(), 'url': root_url + a['href']}
        res_d['category'] = category

    div = soup.find('div', attrs={'class': 'field field-name-field-country field-type-taxonomy-term-reference field-label-hidden'})
    if div is not None:
        a = div.find('a', href=True)
        country = {'text': a.get_text(), 'url': root_url + a['href']}
        res_d['country'] = country

    div = soup.find('div', attrs={'class': 'field field-name-field-length field-type-taxonomy-term-reference field-label-hidden'})
    if div is not None:
        a = div.find('a', href=True)
        duration = {'text': a.get_text(), 'url': root_url + a['href']}
        res_d['duration'] = duration

    div = soup.find('div', attrs={'class': 'field field-name-field-estimated-effort field-type-taxonomy-term-reference field-label-hidden'})
    if div is not None:
        a = div.find('a', href=True)
        frequency = {'text': a.get_text(), 'url': root_url + a['href']}
        res_d['frequency'] = frequency

    div = soup.find('div', attrs={'class': 'field field-name-field-exam field-type-taxonomy-term-reference field-label-hidden'})
    if div is not None:
        a = div.find('a', href=True)
        exam = {'text': a.get_text(), 'url': root_url + a['href']}
        res_d['exam'] = exam

    div = soup.find('div', attrs={'class': 'field field-name-field-certificate field-type-taxonomy-term-reference field-label-hidden'})
    if div is not None:
        a = div.find('a', href=True)
        certificate = {'text': a.get_text(), 'url': root_url + a['href']}
        res_d['certificate'] = certificate

    div = soup.find('div', attrs={'class': 'field field-name-field-language field-type-taxonomy-term-reference field-label-hidden'})
    if div is not None:
        a = div.find('a', href=True)
        language = {'text': a.get_text(), 'url': root_url + a['href']}
        res_d['language'] = language

    return res_d


if __name__ == "__main__":
    with open('data/mooc_list_courses.pkl', 'rb') as f:
        all_courses = pickle.load(f)

    results = []
    for course in all_courses:
        url = course['link']
        try:
            d = parse_course_page(url)
        except Exception:
            continue
        results.append(d)
        time.sleep(0.1)
        with open('data/mooc_list_courses_detailed.json', 'w') as f:
            json.dump(results, f)