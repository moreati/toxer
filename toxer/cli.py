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

    for image, info in config['images'].items():

        if not image in all_distr:
            continue

        print('*' * 60)
        print(image)
        print('*' * 60)

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

        cmd += ' tox -c tox.toxer.ini -e %s' % (','.join(env_to_run))

        cmd += ' --'

        if args.cov:
            cmd += ' --cov-config .tox.coveragerc --cov %s' % config['packages']['code']

        if args.s:
            cmd += ' -s'

        os.system(cmd)
        print cmd

    if args.cov:

        print('collecting coverage.')

        cmd = 'docker run -w "/code" -v %s:/code -i -t %s' % (
            os.getcwd(), config['coverage']['image'])

        os.system('%s coverage combine' % cmd)
        os.system('%s coverage html --include="%s/*" -d %s' % (cmd, config['packages']['code'], args.coverage_dir))

        print('Coverage link: file://%s/%s/index.html' % (os.getcwd(), args.coverage_dir))

