import requests
from bs4 import BeautifulSoup
import tqdm

import time
import pickle
import json
import re

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
        links = div.find_all('a', href=True)
        universities = []
        for a in links:
            university = {'text': a.get_text(), 'url': root_url + a['href']}
            universities.append(university)
        res_d['universities'] = universities

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
        links = div.find_all('a', href=True)
        categories = []
        for a in links:
            category = {'text': a.get_text(), 'url': root_url + a['href']}
            categories.append(category)
        res_d['categories'] = categories

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

    div = soup.find('div', attrs={'class': 'fivestar-summary fivestar-summary-average-count'})
    if div is not None:
        span = div.find('span', attrs={'class': 'average-rating'})
        if span is not None:
            span2 = span.find('span')
            if span2 is not None:
                rating = float(span2.get_text())
                res_d['rating'] = rating

        span = div.find('span', attrs={'class': 'total-votes'})
        if span is not None:
            span2 = span.find('span')
            if span2 is not None:
                votes = int(span2.get_text())
                res_d['votes'] = votes

    div = soup.find('div', attrs={'class': 'field_recommended-background campo-info'})
    if div is not None:
        div2 = div.find('div', attrs={'class': 'field-item even'})
        background = {'text': div2.get_text()}
        res_d['language'] = background

    div = soup.find('div', attrs={'class': 'field field-name-field-course-level field-type-taxonomy-term-reference field-label-hidden'})
    if div is not None:
        a = div.find('a', href=True)
        course_level = {'text': a.get_text(), 'url': root_url + a['href']}
        res_d['course_level'] = course_level

    div = soup.find('div', attrs={'class': 'field-certificate-price campo-info'})
    if div is not None:
        divs = div.find_all('div', attrs={'class': 'field field-name-field-certificate-price field-type-number-decimal field-label-hidden'})
        string = []
        for div in divs:
            string.append(div.get_text())
        res_d['certificate_price'] = ' '.join(string)

    div = soup.find('div', attrs={'class': 'field field-name-field-subtitles field-type-taxonomy-term-reference field-label-hidden'})
    if div is not None:
        links = div.find_all('a', href=True)
        subtitles = []
        for a in links:
            subtitle = {'text': a.get_text(), 'url': root_url + a['href']}
            subtitles.append(subtitle)
        res_d['subtitles'] = subtitles

    div = soup.find('div', attrs={'class': 'field field-name-field-tags field-type-taxonomy-term-reference field-label-hidden'})
    if div is not None:
        links = div.find_all('a', href=True)
        tags = []
        for a in links:
            tag = {'text': a.get_text(), 'url': root_url + a['href']}
            tags.append(tag)
        res_d['tags'] = tags

    return res_d

prof_sufix = 'MOOCs and Free Online Courses'
prof_sufix_len = len(prof_sufix)

def parse_generic(url):
    response = requests.get(url)
    html = response.text

    soup = BeautifulSoup(html, 'lxml')
    res_d = dict()
    res_d['link'] = url

    h1 = soup.find('h1', attrs={'id': 'page-title'})
    if h1 is not None:
        prof_name = h1.get_text()[:-prof_sufix_len]
        res_d['name'] = prof_name.strip()

    div = soup.find('div', attrs={'class': 'views-field views-field-description-1'})
    if div is not None:
        res_d['description'] = div.get_text()

    return res_d

def flatten_property_list(courses, property):
    items = set()

    for course in tqdm.tqdm(courses):
        if property in course:
            for item in course[property]:
                if item['url'] not in items:
                    items.add(item['url'])
    return items

def get_instructors_urls(courses):
    return flatten_property_list(courses, 'instructors')

def get_providers_urls(courses):
    return flatten_property_list(courses, 'provider')

def get_universities_urls(courses):
    return flatten_property_list(courses, 'universities')

if __name__ == "__main__":
    # with open('data/mooc_list_courses.pkl', 'rb') as f:
    #     all_courses = pickle.load(f)
    #
    # results = []
    # for course in tqdm.tqdm(all_courses):
    #     url = course['link']
    #     try:
    #         d = parse_course_page(url)
    #     except Exception as e:
    #         print(e)
    #         continue
    #     results.append(d)
    #     time.sleep(0.1)
    #     with open('data/mooc_list_courses_detailed.json', 'w') as f:
    #         json.dump(results, f)

    with open('data/mooc_list_courses_detailed.json', 'r') as f:
        results = json.load(f)

    all_courses = results
    instructors_data = []
    instructor_urls = get_instructors_urls(all_courses)
    for instructor_url in tqdm.tqdm(instructor_urls):
        try:
            instructor_data = parse_generic(instructor_url)
        except Exception:
            continue
        instructors_data.append(instructor_data)
        time.sleep(0.1)
        with open('data/mooc_list_instructors.json', 'w') as f:
            json.dump(instructors_data, f)

    universities_data = []
    uni_urls = get_universities_urls(all_courses)
    for uni_url in tqdm.tqdm(uni_urls):
        try:
            uni_data = parse_generic(uni_url)
        except Exception:
            continue
        universities_data.append(uni_data)
        time.sleep(0.1)
        with open('data/mooc_list_universities.json', 'w') as f:
            json.dump(universities_data, f)

    providers_data = []
    provider_urls = set([course['provider']['url'] for course in all_courses])
    for provider_url in tqdm.tqdm(provider_urls):
        try:
            provider_data = parse_generic(provider_url)
        except Exception:
            continue
        providers_data.append(provider_data)
        time.sleep(0.1)
        with open('data/mooc_list_providers.json', 'w') as f:
            json.dump(providers_data, f)