import argparse
import os
from voluptuous import Schema
import yaml


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
    parser.add_argument('--coverage-dir', default='coverage_html')
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

    last_dist_command = None
    for image, info in config['images'].items():

        print('*' * 60)
        print(image)
        print('*' * 60)

        if not image in all_distr:
            continue

        cmd = 'docker run -w "/code" -e "TOX_DOCKER=1" -e "TOX_DISTRO=%s" -v %s:/code -i -t %s' % (
            info['image'], os.getcwd(), info['image'])

        envs = info['envs']

        if args.env:
            env_to_run = [e for e in args.env.split(',') if e in envs]
        else:
            env_to_run = envs

        if not env_to_run:
            print('Skip %s as there is no env needed [%s]' % (image, ','.join(envs)))
            continue

        last_dist_command = cmd

        cmd += ' tox -c tox.toxer.ini -e %s' % (','.join(env_to_run))

        if args.cov:
            cmd += ' -- --cov-config .tox.coveragerc --cov %s' % config['packages']['code']

        os.system(cmd)
        print(cmd)

    if args.cov:
        os.system('%s coverage combine' % last_dist_command)
        os.system('%s coverage html --include="%s/*" -d %s' % (
            last_dist_command, config['packages']['code'], args.coverage_dir))

