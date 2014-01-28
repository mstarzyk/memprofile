from __future__ import print_function
import subprocess
import time
import argparse

def sample(pid):
    fname = "/proc/{}/statm".format(pid)
    with open(fname) as f:
        line = f.readline()
        stat = [int(x) for x in line.split()]
        return {'size': stat[0], 'resident': stat[1]}

def main(sampling_time, command):
    print("Running {}".format(command))
    # proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    with open("/dev/null", 'w') as dev_null:
        proc = subprocess.Popen(command, stdout=dev_null, stderr=dev_null)
        print("Running process with PID={}".format(proc.pid))
        start = time.time()
        now = start
        while True:
            returncode = proc.poll()
            if returncode is None:
                print(sample(proc.pid))
                time.sleep(sampling_time)
            else:
                now = time.time()
                latency = now - start
                print("Process finished, retcode={}, latency={}.".format(returncode, latency))
                break
    # now - start

    # print(stdout)
    # print(stderr, file=sys.stderr)



def parse_configuration():
    parser = argparse.ArgumentParser(
            description="Runs memory profile.",
            epilog=""
            )

    parser.add_argument("-t", dest="sampling_time", help='Sampling time (seconds, default 1.0)', default=1.0, type=float)
    parser.add_argument("-c", dest="command", help='Command.', nargs=argparse.REMAINDER)

    return parser.parse_args()


if __name__ == "__main__":
    config = parse_configuration()
    main(**vars(config))
