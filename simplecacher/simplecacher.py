import sha
import cPickle as pickle
import datetime
import os
import io
import shutil
import requests

class SimpleCache(object):
    DIRNAME = "simplecache"
    def __init__(self, daysback=0):
        dt = datetime.datetime.now()
        date_string = dt.strftime("%Y_%m_%d")
        self.cache_dir_name = os.path.join(self.DIRNAME, date_string)
        self.index_file_name = os.path.join(self.cache_dir_name, "index.pickle")
        self.index = self.load_index(self.index_file_name)
        self.days_indices = {date_string: self.index}
        if daysback>0:
            for i in range(1, daysback+1):
                tdelta = datetime.timedelta(days=i)
                dd = dt - tdelta
                d_string = dd.strftime("%Y_%m_%d")
                cache_dir_name = os.path.join(self.DIRNAME, d_string)
                d_index_file_name = os.path.join(cache_dir_name, "index.pickle")
                ii = self.load_index(d_index_file_name)
                if ii:
                    self.days_indices[d_string] = ii
        self.days = self.days_indices.keys()
        self.days.sort(reverse=True)

    def load_index(self, name):
        if os.path.isfile(name):
            with open(name, 'rb') as ff:
                index = pickle.load(ff)
                return index
        return {}

    def clear(self):
        shutil.rmtree(self.cache_dir_name, ignore_errors=True)
        self.index = {}

    def save_index(self):
        self.check_dir()
        with open(self.index_file_name,'wb') as ff:
            pickle.dump(self.index, ff)

    def check_dir(self):
        if not os.path.isdir(self.cache_dir_name):
            os.makedirs(self.cache_dir_name)

    def write_url_to_cache(self, url, data):
        self.check_dir()
        url_sha = sha.sha(url).hexdigest()
        file_name = os.path.join(self.cache_dir_name, url_sha)

        with io.open(file_name, 'w') as ff:
            ff.write(data)


    def read_url_from_cache(self, url):
        url_sha = sha.sha(url).hexdigest()
        indexdate = None
        for k in self.days:
            if url in self.days_indices[k]:
                indexdate = k
        if not indexdate:
            return False
        #print 'in cache', indexdate
        file_name = os.path.join(self.DIRNAME, indexdate, url_sha)
        #try:
        if 1:
            with io.open(file_name, encoding="utf8") as ff:
                data = ff.readlines()
            #print "from cache"
            return "\n".join(data)
        #except IOError:
            #file should be here but is not
        #    return False

    def get_url(self, url, force=False):
        url_sha = sha.sha(url).hexdigest()
        data = self.read_url_from_cache(url)
        if data == False or force:
            print "new request"
            try:
                res = requests.get(url)
                if res.status_code not in range(500,600):
                    data = res.text
                    self.index[url] = url_sha
                    self.write_url_to_cache(url, data)
                    self.save_index()
                else:
                    print 'failed request'
            except requests.ConnectionError:
                return None
        return data

#sc = SimpleCache()
#dd=sc.get_url("http://www.neti.ee")
#"http://www.neti.ee" in sc.index
