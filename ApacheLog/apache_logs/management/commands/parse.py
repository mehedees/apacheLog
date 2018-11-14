#! python
# -*- coding: utf-8 -*-

"""
Module: parse.py
Author: HZ
Created: October 27, 2018

Description: ''
"""

# global imports below: built-in, 3rd party, own
from django.core.management import BaseCommand


# Ownership information

__author__ = 'HZ'
__copyright__ = "Copyright 2018, HZ, Divine IT Ltd."
__credits__ = ["HZ"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "HZ"
__email__ = "hz.ce06@gmail.com"
__status__ = "Development"


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        # parser.add_argument('poll_id', nargs='+', type=int)

        # Named (optional) arguments
        # parser.add_argument(
        #     '--delete',
        #     action='store_true',
        #     dest='delete',
        #     default=False,
        #     help='Delete poll instead of closing it',
        # )
        pass

    def handle(self, *args, **options):
        import time
        print time.time()