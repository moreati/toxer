import argparse
from subprocess import Popen, PIPE
from time import sleep
import sys
import os
from voluptuous import Schema
import yaml


def call(cmd):
    return Popen(cmd, stdout=PIPE, shell=True).communicate()[0].strip()


def build_images():
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    parser.add_argument('prefix', default='test_')
    parser.add_argument('--dist', default=False)
    args = parser.parse_args()

    path = args.path
    prefix = args.prefix

    if args.dist:
        all_distr = args.dist.split(',')
    else:
        all_distr = os.listdir(path)

    for image in all_distr:
        print('Building %s ...' % image)
        os.system('docker build -t %(prefix)s%(image)s %(path)s/%(image)s' % locals())
        print('done building: %(path)s/%(image)s -> %(prefix)s%(image)s' % locals())

    print('All done.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cov', action='store_true', default=False)
    parser.add_argument('--dist', default=False)
    parser.add_argument('--env', default=False)
    parser.add_argument('-p', '--parallel', action='store_true', default=False)
    parser.add_argument('-m', '--marks', default=False)
    parser.add_argument('-s', action='store_true', default=False)
    parser.add_argument('--coverage-dir', default='coverage_html')

    parser.add_argument('--no-large', default=False)
    parser.add_argument('--no-medium', default=False)

    parser.add_argument('--large', default=False)
    parser.add_argument('--medium', default=False)
    parser.add_argument('--small', default=False)

    args = parser.parse_args()

    with open('toxer.yml') as f:
        config = yaml.load(f)

    schema = Schema({
        'images': {
            str: {
                'image': str,
                'envs': [str]
            }
        },
        'packages': {
            'code': str,
            'tests': str
        },
        'coverage': {
            'image': str
        }
    })
    schema(config)

    os.system("find %s -name *.pyc -delete" % config['packages']['code'])
    os.system("find %s -name *.pyc -delete" % config['packages']['tests'])

    if args.dist:
        all_distr = [x.strip() for x in args.dist.split(',')]
    else:
        all_distr = config['images'].keys()

    processes_running = []
    for image, info in config['images'].items():

        if not image in all_distr:
            continue

        if args.parallel:
            running_mode = '-d'
        else:
            running_mode = '-i -t'

        cmd = 'docker run %(mode)s -w "/code" -e "TOX_DOCKER=1" -e "TOX_DISTRO=%(image)s" -v %(cwd)s:/code %(image)s' % {
            'image': info['image'],
            'cwd': os.getcwd(),
            'mode': running_mode
        }

        envs = info['envs']

        if args.env:
            env_to_run = [e for e in args.env.split(',') if e in envs]
        else:
            env_to_run = envs

        if not env_to_run:
            print('Skip %s as there is no env needed [%s]' % (image, ','.join(envs)))
            continue

        for env in env_to_run:
            cmd_env = cmd + ' tox -c tox.toxer.ini -e %s' % env

            cmd_env += ' --'

            if args.cov:
                cmd_env += ' --cov-config .tox.coveragerc --cov %s' % config['packages']['code']

            if args.s:
                cmd_env += ' -s'

            if args.parallel:
                process_id = call(cmd_env)
                processes_running.append((process_id, image, env))
            else:
                os.system(cmd_env)

    if args.parallel:

        while processes_running:
            sleep(0.5)

            sys.stdout.write('.')

            for process_info in processes_running:

                process, image, env = process_info

                is_running = call('docker inspect --format=\'{{.State.Running}}\' %s' % process) == "true"

                if not is_running:
                    processes_running.remove(process_info)

                    ret = int(call('docker inspect --format=\'{{.State.ExitCode}}\' %s' % process))

                    print('%s:%s ... done' % (image, env))
                    print('ret code: %s' % ret)
                    if ret != 0:
                        print('=' * 40)
                        print('=' * 40)
                        os.system('docker logs %s' % process)
                        print('=' * 40)
                        print('=' * 40)
                    else:
                        print('ok')


