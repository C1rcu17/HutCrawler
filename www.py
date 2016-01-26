import requests
import pickle
import objdump
import lxml.etree


class BrowserException(Exception):
    pass


class Browser(object):
    def __init__(self, encoding='utf-8'):
        self.encoding = encoding
        self.html_parser = lxml.etree.HTMLParser(
            encoding=self.encoding,
            remove_blank_text=True,
            remove_comments=True,
            remove_pis=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36'
        })

    def save_cookies(self, file):
        with open(file, 'wb') as fd:
            pickle.dump(requests.utils.dict_from_cookiejar(self.session.cookies), fd)

    def load_cookies(self, file):
        try:
            with open(file, 'rb') as fd:
                self.session.cookies = requests.utils.cookiejar_from_dict(pickle.load(fd))
        except OSError:
            pass

    def url_response(self, method, url, *args, **kwargs):
        response = self.session.request(method, url, *args, **kwargs)
        return response

    def url_content(self, method, url, *args, **kwargs):
        response = self.url_response(method, url, *args, **kwargs)
        content = response.content.decode(self.encoding)
        return response, content

    def url_etree(self, method, url, *args, **kwargs):
        response, content = self.url_content(method, url, *args, **kwargs)
        etree = lxml.etree.HTML(content, self.html_parser)
        return response, content, etree

    def url_dump(self, method, url, dump_file=None, *args, **kwargs):
        response, content, etree = self.url_etree(method, url, *args, **kwargs)

        with open(dump_file, 'w') as fd:
            fd.write('<!--\nSESSION = ')
            objdump.write(self.session, fd)
            fd.write('\n\nRESPONSE = ')
            objdump.write(response, fd)
            fd.write('\n-->\n')
            fd.write(lxml.etree.tostring(etree, encoding=self.encoding, pretty_print=True).decode(self.encoding))

        return response, content, etree
