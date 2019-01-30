from AGRe import setup

setup()

from functools import reduce
from core.models import Interest, Course
import random



courses = {
    'Databases': [
        'SQL',
        'NOSQL',
        'mongo',
        'ORM',
        'index',
        'b+',
    ],
    'Data mining': [
        'data+mining',
        'statistics',
        'big+data',
        'ensemble',
        'machine+learning',
        'decision+trees',
        'clustering',
        'classification',
        'svm'
    ],

    'Big data': [
        'big+data',
        'hadoop',
        'apache+spark',
        'pig',
        'hive'
        'impala'
    ],

    'Machine learning': [
        'statistics',
        'algorithms',
        'clustering',
        'classification',
        'svm',
        'knn',
        'k-means',
        'decision+trees',
        'boosting',
        'bagging',
        'random+forest'
    ],

    'Computer networks': [
        'tcp',
        'networking',
        'udp',
        'internet',
        'router',
        'traffic',
        'ping',
        'ip',
        'ftp'
    ],

    'Cryptography': [
        'RSA',
        'DES',
        'SHA',
        'hash',
        'private+key',
        'public+key',
        'hacking'
    ],

    'Mathematics': [
        'series',
        'gradient',
        'numerical+analysis',
        'linear+algebra',
        'geometry',
        'kernel+functions',
        'fourier'
    ],

    'Programming': [
        'c/c++',
        'java',
        'python',
        'OOP',
    ],

    'Web technologies': [
        'html',
        'css',
        'angular',
        'node+js',
        'php',
        'semantic+web',
        'http',
    ],

    'Artificial Intelligence': [
        'min-max',
        'a+star',
        'chatbot',
        'nlp',
        'statistics',
    ],
}

ALL_TAGS = set(reduce(lambda x, y: x + y, courses.values()))


if __name__ == '__main__':

    # Interest.objects.all().delete()
    # Course.objects.all().delete()

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    times = ['08-10', '10-12', '12-14', '14-16', '16-18', '18-20']
    years = [1, 2, 3, 4, 5]
    for c in courses:
        day = random.choice(days)
        time = random.choice(times)
        duration = '12 weeks'
        timetable = day + ' ' + time
        year = random.choice(years)
        course = Course.objects.get_or_create(name=c, year=year, duration=duration, timetable=timetable)[0]
        print(c)
        for tag in courses[c]:
            print('\t' + tag)
            interest = Interest.objects.get_or_create(name=tag)[0]
            course.tags.add(interest)
            course.save()
