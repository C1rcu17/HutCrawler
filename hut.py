import dates
from www import Browser


class HutException(Exception):
    pass


class Hut(Browser):

    def __init__(self, email, password):
        super().__init__()
        self.email = email
        self.password = password
        self.session.headers.update({
            'Host': 'www.myhut.pt'
        })

    def do_login(self):
        url = 'https://www.myhut.pt/myhut/functions/login.php'

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://www.myhut.pt',
            'Referer': 'https://www.myhut.pt/',
            'X-Requested-With': 'XMLHttpRequest',
        }

        post_data = {
            'myhut-login-email': self.email,
            'myhut-login-password': self.password,
        }

        response = self.url_response('POST', url, headers=headers, data=post_data)

        if response.text == '  -1':
            raise HutException('invalid login')

    def get_member_info(self):
        info = {}

        url = 'https://www.myhut.pt/myhut/aulas/'

        response, _, tree = self.url_etree('GET', url)

        if response.url != url:
            raise HutException('login needed')

        avatar = tree.cssselect('div.user-avatar > p')
        info['member_name'] = avatar[0].xpath('//strong')[0].text.strip()
        info['club_name'] = avatar[1].xpath('text()')[1].strip()
        info['member_number'] = avatar[2].xpath('text()')[0].strip()
        info['clubs'] = {club.text.strip(): int(club.get('id')) for club in tree.cssselect('select#clubes > optgroup > option')}
        info['club_id'] = info['clubs'][info['club_name']] if info['club_name'] in info['clubs'] else -1

        url = 'https://www.myhut.pt/myhut/a-minha-adesao/'

        headers = {
            'Referer': 'https://www.myhut.pt/myhut/aulas/',
        }

        response, _, tree = self.url_etree('GET', url, headers=headers)

        if response.url != url:
            raise HutException('login needed')

        info['member_id'] = tree.cssselect('input#socio')[0].get('value').strip()

        return info

    def get_classes(self, club_id, tomorrow=False):
        classes = []

        url = 'https://www.myhut.pt/myhut/functions/get-aulas.php'

        headers = {
            'Referer': 'https://www.myhut.pt/myhut/aulas/',
            'X-Requested-With': 'XMLHttpRequest',
        }

        get_data = {
            'id': club_id,
            'date': dates.f(dates.now() if not tomorrow else dates.add(dates.now(), days=1), '%Y-%m-%d'),
            'rnd': '1453419300746'
        }

        response, _, tree = self.url_etree('GET', url, headers=headers, params=get_data)

        panels = tree.cssselect('div.panel')

        for c in panels:
            info = {}

            panel_class = c.get('class').split()
            if 'panel-default' in panel_class:
                info['status'] = 'available'
            elif 'panel-red' in panel_class:
                info['status'] = 'full'
            elif 'panel-off' in panel_class:
                info['status'] = 'unavailable'

            c = c.cssselect('a.accordion-toggle')[0]
            info['class_id'] = c.get('href')[len('#aula'):]

            divs = c.xpath('./div')
            info['time'] = dates.parse(divs[0].xpath('.//span')[0].text.strip(), '%H:%M')
            info['class_name'] = divs[1].xpath('.//span')[0].text.strip()
            info['studio'] = divs[2].text.strip()
            info['duration'] = divs[3].text.strip()
            classes.append(info)

        return classes

    def get_class(self, club_id, class_name, time_min, time_max):
        for c in self.get_classes(club_id):
            if c['status'] == 'available' and c['class_name'] == class_name and time_min <= c['time'] <= time_max:
                return c

    def book_class(self, class_id, member_id):
        url = 'https://www.myhut.pt/myhut/functions/myhut.php'

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://www.myhut.pt',
            'Referer': 'https://www.myhut.pt/myhut/aulas/',
            'X-Requested-With': 'XMLHttpRequest',
        }

        post_data = {
            'aula': class_id,
            'socio': member_id,
            'op': 'book-aulas',
        }

        response, _, _ = self.url_etree('POST', url, headers=headers, data=post_data)

        if response.text != '  1':
            raise HutException('couldn\'t book class')
