import smtp
import objdump
import datetime
import schedule
from time import sleep
from hut import Hut

HUT = None
CRAWLER_SMTP = None
MEMBER_INFO = None


def member_info_update():
    global MEMBER_INFO
    MEMBER_INFO = HUT.member_info()
    print('Updated member info:', objdump.get(MEMBER_INFO))


def main(myhut_info, smtp_info, plan):
    global HUT, CRAWLER_SMTP

    HUT = Hut(myhut_info['username'], myhut_info['password'])
    CRAWLER_SMTP = smtp.Server(
        smtp_info['server'],
        smtp_info['port'],
        smtp_info['username'],
        smtp_info['password'],
        smtp_info['name'],
        smtp_info['email'])

    HUT.login()
    schedule.every().day.at('20:44').do(member_info_update)

    while True:
        schedule.run_pending()
        sleep(1)

    # member_info_update()

    # t = datetime.time(18, 30, 0, 0, HUT.timezone)
    # zumba = HUT.get_class(MEMBER_INFO['club_id'], 'LESMILLS CXWORX', t, t)

    # hut.book_class(zumba['class_id'], member_info['member_id'])



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
        sys.exit('error: ' + str(e))
        raise
