import requests
import random

BASE_URL = 'http://localhost:8000/'
LOGIN_URL = 'http://localhost:8000/accounts/login/'
LOGOUT_URL = 'http://localhost:8000/accounts/logout/'
REVIEW_URL = BASE_URL + 'review/'

RESOURCE_URL = BASE_URL + 'resource/?id={}/'

PASS = 'cacacaca'

users = ['eve30', 'eve31', 'mihai30', 'mihai31', 'andrei30', 'andrei31', 'test', 'eve29', 'testtest', ]
messages = ['Very nice', "It was good", 'Not good', 'best book ever', 'Super', 'Not that nice', 'Insightful', 'I reallt enjoyed this', 'Didnt do it for me']

min_id = 3200
max_id = 3250


def main():
    for user in users:
        session = requests.Session()
        session.get(LOGIN_URL)  # sets cookie
        csrftoken = session.cookies['csrftoken']
        login_data = dict(username=user, password=PASS, csrfmiddlewaretoken=csrftoken, next='/')
        p = session.post(LOGIN_URL, data=login_data, headers=dict(Referer=LOGIN_URL))
        # print(p.text)
        print(user)
        for i in range(15):
            rand_id = random.randint(min_id, max_id)
            print('\t %s' % rand_id)
            # session.get(RESOURCE_URL.format(rand_id))  # sets cookie
            # csrftoken = session.cookies['csrftoken']
            review_data = dict(item=rand_id, comment=random.choice(messages),
                               rating=random.randint(1, 5), is_anonymous=False)
            p = session.post(REVIEW_URL, data=review_data)
            # print(p)
        session.get(LOGOUT_URL)


if __name__ == '__main__':
    main()
