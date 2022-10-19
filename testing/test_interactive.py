import os.path
import time

import pexpect


TEST_DIR = os.path.dirname(__file__)
FCOMPLETE_PATH = os.path.join(TEST_DIR, 'fcomplete.py')


def test_global_matches():
    prefix = 'complete_'
    names = ['a', 'b', 'c']
    full_names = [prefix + name for name in names]

    args = [FCOMPLETE_PATH]
    args.extend(full_names)

    fcomplete = pexpect.spawn('python', args)

    try:
        fcomplete.send(prefix)
        output = fcomplete.read_nonblocking(1000).decode('utf-8')
        assert output == prefix

        fcomplete.send('\t')
        fcomplete.read_nonblocking(1000).decode('utf-8')

        fcomplete.send('\t')
        time.sleep(0.1)
        output = fcomplete.read_nonblocking(1000).decode('utf-8')
        lines = output.split('\r\n')

        assert len(lines) == 3
        assert lines[2].endswith(prefix)

        assert all(full_name in lines[1] for full_name in full_names)
        completed_names = lines[1].strip().split('  ')
        assert set(completed_names) == set(full_names)

    finally:
        fcomplete.terminate(force=True)
