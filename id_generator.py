#!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# author:Samray <samrayleung@gmail.com>

import functools
import time
from uuid import getnode as get_mac

from exception import GetHardwareIdFailedException, InvalidSystemClockException


def singleton(cls):
    ''' Use class as singleton. '''

    cls.__new_original__ = cls.__new__

    @functools.wraps(cls.__new__)
    def singleton_new(cls, *args, **kw):
        it = cls.__dict__.get('__it__')
        if it is not None:
            return it

        cls.__it__ = it = cls.__new_original__(cls, *args, **kw)
        it.__init_original__(*args, **kw)
        return it

    cls.__new__ = singleton_new
    cls.__init_original__ = cls.__init__
    cls.__init__ = object.__init__

    return cls


class IdGenerator():
    """id format =>
    timestamp | machineId|sequence
    41        | 10       |12
    """

    def __init__(self):
        self.sequence_bits = 12
        self.machine_id_bits = 10
        self.max_machine_id = -1 ^ (-1 << self.machine_id_bits)
        self.machine_id_shift = self.sequence_bits
        self.timestamp_left_shift = self.sequence_bits + self.machine_id_bits
        self.twepoch = 1242424374657
        self.machine_id = self.get_machine_id()
        self.sequence_max = 4096  # 2**12
        self.last_timestamp = -1
        self.sequence = 0

    def get_system_millisecond(self):
        return int(round(time.time() * 1000))

    def till_next_millis(self, last_timestamp):
        timestamp = self.get_system_millisecond()
        while(timestamp <= last_timestamp):
            timestamp = self.get_system_millisecond()
        return timestamp

    def get_machine_id(self):
        mac = get_mac()
        machine_id = mac & self.max_machine_id
        if machine_id > self.max_machine_id or machine_id < 0:
            raise GetHardwareIdFailedException(
                "machineId must be less than max_machine_id")
        return machine_id

    def generate_id(self):
        timestamp = self.get_system_millisecond()
        if timestamp < self.last_timestamp:
            raise InvalidSystemClockException("Clock moved backwards.\
            Refusing to generate id for {} millseconds".format(self.last_timestamp - timestamp))
        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) % self.sequence_max
            if self.sequence == 0:
                timestamp = self.till_next_millis(self.last_timestamp)
        else:
            self.sequence = 0
        self.last_timestamp = timestamp
        _id = ((timestamp - self.twepoch) <<
               self.timestamp_left_shift) | (self.machine_id << self.machine_id_shift) | self.sequence
        return _id


if __name__ == "__main__":
    id_set = set()
    id_generator = IdGenerator()
    for i in range(1000000):
        id_set.add(id_generator.generate_id())
    print(1000000 - len(id_set))
