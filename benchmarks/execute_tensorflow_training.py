#!/usr/bin/env python

from __future__ import absolute_import

import argparse
import itertools
import os

from sagemaker import Session
from sagemaker.estimator import Framework
from sagemaker.tensorflow import TensorFlow

default_bucket = Session().default_bucket
dir_path = os.path.dirname(os.path.realpath(__file__))

_DEFAULT_HYPERPARAMETERS = {
    'batch_size':           32,
    'model':                'resnet32',
    'num_epochs':           10,
    'data_format':          'NHWC',
    'summary_verbosity':    1,
    'save_summaries_steps': 10,
    'data_name':            'cifar10'
}


class ScriptModeTensorFlow(Framework):
    """This class is temporary until the final version of Script Mode is released.
    """

    __framework_name__ = "tensorflow-scriptmode-beta"

    create_model = TensorFlow.create_model

    def __init__(self, py_version='py3', **kwargs):
        super(ScriptModeTensorFlow, self).__init__(**kwargs)
        self.py_version = py_version
        self.framework_version = '1.12.0'


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--instance-types', nargs='+', help='<Required> Set flag', required=True)
    parser.add_argument('-r', '--role', required=True)
    parser.add_argument('-w', '--wait', action='store_true')
    parser.add_argument('--region', default='us-east-1')
    parser.add_argument('--py-versions', nargs='+', help='<Required> Set flag', default=['py3'])
    parser.add_argument('--checkpoint-path',
                        default=os.path.join('huilgolr-tf-sm', 'benchmarks', 'checkpoints'),
                        help='The S3 location where the model checkpoints and tensorboard events are saved after training')
    parser.add_argument('--image', default=None)
    return parser.parse_known_args()


def main(args, script_args):
    for instance_type, py_version in itertools.product(args.instance_types, args.py_versions):
        base_name = '%s-%s-%s' % (py_version, instance_type[3:5], instance_type[6:])
        model_dir = os.path.join(args.checkpoint_path, base_name)

        job_hps = create_hyperparameters(model_dir, script_args)

        print('hyperparameters:')
        print(job_hps)

        estimator = ScriptModeTensorFlow(
            entry_point='tf_cnn_benchmarks.py',
            role=args.role,
            source_dir=os.path.join(dir_path, 'tf_cnn_benchmarks'),
            base_job_name=base_name,
            train_instance_count=1,
            hyperparameters=job_hps,
            train_instance_type=instance_type,
  	    image_name=args.image
        )

        input_dir = 's3://sagemaker-sample-data-%s/spark/mnist/train/' % args.region
        estimator.fit({'train': input_dir}, wait=args.wait)

    print("To use TensorBoard, execute the following command:")
    cmd = 'S3_USE_HTTPS=0 S3_VERIFY_SSL=0  AWS_REGION=%s tensorboard --host localhost --port 6006 --logdir %s'
    print(cmd % (args.region, args.checkpoint_path))


def create_hyperparameters(model_dir, script_args):
    job_hps = _DEFAULT_HYPERPARAMETERS.copy()

    job_hps.update({'train_dir': model_dir, 'eval_dir': model_dir})

    script_arg_keys_without_dashes = [key[2:] if key.startswith('--') else key[1:] for key in script_args[::2]]
    script_arg_values = script_args[1::2]
    job_hps.update(dict(zip(script_arg_keys_without_dashes, script_arg_values)))

    return job_hps


if __name__ == '__main__':
    args, script_args = get_args()
    main(args, script_args)
