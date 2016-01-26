import smtp
import objdump
import datetime
import schedule
from hut import Hut

HUT = None
COOKIE_FILE = None
CRAWLER_SMTP = None
MEMBER_INFO = None


def main(myhut_info, smtp_info, plan):
    global HUT, COOKIE_FILE, CRAWLER_SMTP, MEMBER_INFO

    HUT = Hut(myhut_info['username'], myhut_info['password'])
    COOKIE_FILE = HUT.email + '.session'
    CRAWLER_SMTP = smtp.Server(
        smtp_info['server'],
        smtp_info['port'],
        smtp_info['username'],
        smtp_info['password'],
        smtp_info['name'],
        smtp_info['email'])

    HUT.login()
    MEMBER_INFO = HUT.member_info()
    t = datetime.time(18, 30, 0, 0, HUT.timezone)
    zumba = HUT.get_class(MEMBER_INFO['club_id'], 'LESMILLS CXWORX', t, t)

    # hut.book_class(zumba['class_id'], member_info['member_id'])
    objdump.stdout(MEMBER_INFO)
    objdump.stdout(zumba)


if __name__ == '__main__':
    import sys
    import json
    import argparse

    def json_file(string):
        try:
            with open(string, 'r') as fd:
                return json.load(fd)
        except OSError as e:
            raise argparse.ArgumentTypeError(e.strerror)
        except ValueError as e:
            raise argparse.ArgumentTypeError('\n'.join(e.args))

    parser = argparse.ArgumentParser(description='A crawler for https://www.myhut.pt/')
    parser.add_argument('plan_file', type=json_file, help='The JSON formated plan file')
    parser.add_argument('-hp', '--myhut-password', metavar='pass', help='MyHUT password')
    parser.add_argument('-sp', '--smtp-password', metavar='pass', help='SMTP server password')

    args = parser.parse_args()

    myhut_info = args.plan_file['myhut']
    smtp_info = args.plan_file['smtp']
    plan = args.plan_file['plan']

    if args.myhut_password:
        myhut_info['password'] = args.myhut_password

    if args.smtp_password:
        smtp_info['password'] = args.smtp_password

    try:
        main(myhut_info, smtp_info, plan)
    except Exception as e:
        raise
        sys.exit('error: ' + str(e))
