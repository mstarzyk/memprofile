from __future__ import print_function
import subprocess
import time
import argparse
import sys


def sample(pid):
    fname = "/proc/{}/statm".format(pid)
    with open(fname) as f:
        line = f.readline()
        stat = [int(x) for x in line.split()]
        ts = "{:0.3f}".format(time.time())
        return {'time': ts, 'size': stat[0], 'resident': stat[1]}


class Hash(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.algo = "MD5"

    def __enter__(self):
        self.proc_stdout, self.stdout = self._open()
        self.proc_stderr, self.stderr = self._open()

    def __exit__(self, exc_type, exc_value, traceback):
        for label, proc in ( ("STDOUT", self.proc_stdout)
                           , ("STDERR", self.proc_stderr)
                           ):
            ret = self._close(proc)
            print("{}({}): {}".format(label, self.algo, ret))

    def _open(self):
        proc = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        return proc, proc.stdin

    def _close(self, proc):
        proc.stdin.close()
        return proc.stdout.read().split(' ', 1)[0]


class DevNull(object):
    def __enter__(self):
        self.file = open("/dev/null", "w")
        self.stdout = self.file
        self.stderr = subprocess.STDOUT

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()


def main(sampling_time, command, hash):
    print("Running {}".format(command))
    if hash:
        out = Hash("md5sum")
    else:
        out = DevNull()

    with out:
        proc = subprocess.Popen(command, stdout=out.stdout, stderr=out.stderr)
        print("PID={}".format(proc.pid))
        start = time.time()
        now = start
        while True:
            returncode = proc.poll()
            if returncode is None:
                print(sample(proc.pid))
                time.sleep(sampling_time)
            else:
                now = time.time()
                elapsed = now - start
                print("Process finished, retcode={0}, time={1:0.3f}".format(returncode, elapsed))
                break
    return returncode


def parse_configuration():
    parser = argparse.ArgumentParser(
            description="Runs memory profile.",
            epilog=""
            )

    default_sampling_time = 1.0
    parser.add_argument("-t", dest="sampling_time", help='Sampling time (in seconds, default {}).'.format(default_sampling_time), default=default_sampling_time, type=float)
    parser.add_argument("-s", action="store_true", help='Captures stdout and stderr into MD5 hash.', dest="hash", default=False)
    parser.add_argument("-c", dest="command", help='Command to run.', nargs=argparse.REMAINDER, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    config = parse_configuration()
    sys.exit(main(**vars(config)))
