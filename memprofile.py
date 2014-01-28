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

def main(sampling_time, command):
    print("Running {}".format(command))
    with open("/dev/null", 'w') as dev_null:
        proc = subprocess.Popen(command, stdout=dev_null, stderr=subprocess.STDOUT)
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

    parser.add_argument("-t", dest="sampling_time", help='Sampling time (seconds, default 1.0)', default=1.0, type=float)
    parser.add_argument("-c", dest="command", help='Command.', nargs=argparse.REMAINDER, required=True)

    return parser.parse_args()


if __name__ == "__main__":
    config = parse_configuration()
    sys.exit(main(**vars(config)))
