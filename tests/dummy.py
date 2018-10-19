import argparse
import sys
import time
import random

from experience_tracker.logger import make_tracker


def get_parser():
    parser = argparse.ArgumentParser(description='PyTorch ImageNet Training')
    parser.add_argument('--data', type=str, metavar='DIR',
                        help='path to the dataset location')

    parser.add_argument('-j', '--workers', default=4, type=int, metavar='N',
                        help='number of data loading workers (default: 4)')

    parser.add_argument('--sleep', default=64, type=int, metavar='HS',
                        help='Sleep Time')

    return parser


def main():
    log = make_tracker(mode='local')

    parser = get_parser()
    args = parser.parse_args()

    print('Going to sleep for {} s'.format(args.sleep))

    time.sleep(args.sleep)

    print('Done Sleeping')

    description = log.namespace('meta')
    description.push('description', """
        Test Program, trying to do something
    """)
    train = log.namespace('train')
    metrics = log.namespace('metrics')

    for i in range(0, 10000):
        train.push_stream('cpu', random.uniform(0, 1))
        train.push_stream('gpu', random.uniform(1, 2))

    metrics.push('accuracy', 0.9876)

    log.dump()
    sys.exit(0)


if __name__ == '__main__':
    main()
