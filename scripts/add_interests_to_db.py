from AGRe import setup

setup()

from core.models import Interest

a = ['vpn', 'ip', 'cryptography', 'networking', 'data+structures', 'machine+learning', 'programming',
     'artificial+intelligence', 'database', 'neural+networks', 'semantic+web', 'web+technologies', 'algorithms', 'c',
     'data+mining', 'big+data', 'html', 'django', 'linear', 'svm', 'sparql']

Interest.objects.all().delete()

for it in a:
    Interest(name=it).save()
