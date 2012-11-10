import re
import os
import sys
import urllib2
import mechanize
import BeautifulSoup

class Udacity:

    def __init__(self, course=None):
        self.course  = course
        self.website = 'http://www.udacity.com/wiki/downloads'

        self.browser = mechanize.Browser()
        self.browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) \
                                    Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
        self.browser.set_handle_robots(False)


    def findAllCourses(self):
        get  = urllib2.urlopen(self.website).read()
        html = BeautifulSoup.BeautifulSoup(get)

        browse  = html.find('div', {'id' : 'pb'})
        courses = browse.findAll('li')

        data = []

        for course in courses:
            code = course.find('a').string
            name = str(course).split(' - ')[1].split('</')[0]

            data.append({'name' : code + ' - ' + name,
                         'url'  : course.find('a')['href'],
                         'code' : code.lower()})

        return data


    def getContents(self, course=None):
        if course is None:
            course = self.course.lower()

        courses = self.findAllCourses()
        dlinfo  = [i for i in courses if i['code'] == course]
        url     = dlinfo[0]['url']

        get  = urllib2.urlopen(url).read()
        html = BeautifulSoup.BeautifulSoup(get)

        list = html.findAll('li')
        data = []

        for link in list:
            url = link.find('a', {'rel' : 'nofollow'})

            if url == None:
                pass
            else:
                link = url['href']
                name = url.string.replace('amp;', '')
                data.append({ 'url'  : link,
                              'name' : name})

        return dlinfo, data



    def downloadTree(self, course=None):
        if course is None:
            course = self.course

        name, content = self.getContents(course)


        print name[0]['name']

        for item in content:
            #print '  >>  ' + item['name']

            dlPathName = self._renameFolder(name[0]['name'].rstrip(' '))
            pathName   = dlPathName + '/' + item['name']

            try:
                os.makedirs(dlPathName)
            except OSError as e:
                if e.errno != 17 and e.errno != 2:
                    raise e
                pass

            self.downloadFile(item['url'], pathName)


    def downloadFile(self, url, fileName):
        if os.path.exists(fileName):
            print " " * 10 + " - %s (Already Saved)" % fileName.split('/')[-1]
        else:
            print " " * 10 + " - %s" % fileName.split('/')[-1]

            try:
                self.browser.retrieve(url, fileName, self._progressBar)
            except KeyboardInterrupt:
                if os.path.exists(fileName):
                    os.remove(fileName)
                raise
            except Exception, e:
                err = e
                if os.path.exists(fileName):
                    os.remove(fileName)
                if e.errno == 2:
                    err = "Errno 2 (No such file or directory)"
                print " " * 10 + " X %s - %s" % (fileName.split('/')[-1], err)


    def _progressBar(self, blocknum, bs, size):
        if size > 0:
            if size % bs != 0:
                blockCount = size/bs + 1
            else:
                blockCount = size/bs

            fraction = blocknum*1.0/blockCount
            width    = 50

            stars    = '*' * int(width * fraction)
            spaces   = ' ' * (width - len(stars))
            progress = ' ' * 12 + ' [%s%s] (%s%%)' % (stars, spaces, int(fraction * 100))

            if fraction*100 < 100:
                sys.stdout.write(progress)

                if blocknum < blockCount:
                    sys.stdout.write('\r')
                else:
                    sys.stdout.write('\n')
            else:
                sys.stdout.write(' ' * int(width * 1.5) + '\r')
                sys.stdout.flush()


    def _renameFolder(self, name):
        name = re.sub("[^A-Za-z0-9\.\(\)\_\s\-]", "", name.replace(':', '-'))
        name = re.sub(" +", " ", name)
        return name


x = Udacity('cs101')
x.downloadTree()
