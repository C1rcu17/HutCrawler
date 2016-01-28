import smtp
import objdump
import dates
from apscheduler.schedulers.blocking import BlockingScheduler
from hut import Hut, HutException
from time import sleep

dates.set_tz('Europe/Lisbon')

TIME_FORMAT = '%H:%M'
MIDNIGHT = dates.parse('00:00', TIME_FORMAT)
HUT = None
CRAWLER_SMTP = None
SCHEDULER = None
MEMBER_INFO = None


def main(myhut_info, smtp_info, plan):
    global HUT, CRAWLER_SMTP, SCHEDULER

    HUT = Hut(myhut_info['username'], myhut_info['password'])
    CRAWLER_SMTP = smtp.Server(
        smtp_info['server'],
        smtp_info['port'],
        smtp_info['username'],
        smtp_info['password'],
        smtp_info['name'],
        smtp_info['email'])

    member_info_update()

    # job = {
    #   "club": "Braga",
    #   "class": "V-CLASS CYCLING",
    #   "day_of_week": "wed",
    #   "time": "10:30"
    # }
    # book_class(job)
    # return

    SCHEDULER = BlockingScheduler()
    SCHEDULER.add_job(member_info_update, trigger='cron', hour=0, minute=0)

    for job in plan:
        start_date = dates.parse(job['time'], TIME_FORMAT)
        book_date = dates.sub(start_date, hours=10)
        if book_date < MIDNIGHT:
            book_date = dates.dup(MIDNIGHT)

        # day_of_week = mon,tue,wed,thu,fri,sat,sun
        SCHEDULER.add_job(
            book_class, args=[job], trigger='cron',
            day_of_week=job['day_of_week'], hour=book_date.hour, minute=book_date.minute)

    SCHEDULER.start()


def member_info_update():
    global MEMBER_INFO
    HUT.do_login()
    MEMBER_INFO = HUT.get_member_info()
    print('Member info:')
    objdump.stdout(MEMBER_INFO)
    print('Today classes for {} club:'.format(MEMBER_INFO['club_name']))
    objdump.stdout(HUT.get_classes(MEMBER_INFO['club_id']))
    print('Tomorrow classes for {} club:'.format(MEMBER_INFO['club_name']))
    objdump.stdout(HUT.get_classes(MEMBER_INFO['club_id'], tomorrow=True))
    if SCHEDULER:
        print('Jobs:')
        SCHEDULER.print_jobs()


def book_class(job):
    objdump.stdout(job)
    time = dates.parse(job['time'], TIME_FORMAT)

    c = None

    # Wait for available
    while True:
        try:
            c = HUT.get_class(MEMBER_INFO['clubs'][job['club']], job['class'], time, time)
            if not c:
                raise Exception('no class found')
        except Exception as e:
            print(str(e))
            print('waiting 10 seconds before retry check')
            sleep(10)
        else:
            break

    objdump.stdout(c)

    while True:
        try:
            HUT.do_login()
            HUT.book_class(c['class_id'], MEMBER_INFO['member_id'])
        except Exception as e:
            print(str(e))
            print('waiting 5 seconds before retry book')
            sleep(5)
        else:
            break

    CRAWLER_SMTP.send_email(HUT.email, 'Marcação de aula no Fitness Hut',
        'Bom dia :D\n\n\tMarquei uma aula de {} de {} no {} do clube de {} que começa hoje, às {}.\n\nAproveita, e bom treino\n\t{}'.format(
            c['class_name'], c['duration'], c['studio'], job['club'], job['time'], CRAWLER_SMTP.name
        ))


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
    except KeyboardInterrupt:
        pass
    except Exception as e:
        raise
        sys.exit('error: ' + str(e))
