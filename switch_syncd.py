#!./venv/bin/python
from ouimeaux.environment import Environment
import logging.config
import sys

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'short': {
            'format': '[%(asctime)s %(levelname)s %(name)s] %(message)s',
            'datefmt': '%m/%d %H:%M:%S'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'short'
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
        },
        'requests.packages.urllib3.connectionpool': {'level': 'WARNING'},
    }
}

log = logging.getLogger('switch_syncd')


class SwitchSyncd(object):
    def __init__(self):
        super(SwitchSyncd, self).__init__()
        self.devices = dict()

    def main(self):
        try:
            env = Environment(self.on_switch, with_subscribers=False)
            env.start()
            env.discover(10)
            while True:
                env.wait(5)
                self.check()
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            log.exception('Unhandled error')
            sys.exit(0)

    def on_switch(self, device):
        log.info('Discovered switch %s = %s', device.name, device.get_state(force_update=True))
        self.devices[device] = device.get_state()

    def check(self):
        for device, old_state in self.devices.items():
            new_state = device.get_state(force_update=True)
            if old_state != new_state:
                log.info('%s changed from %s to %s, broadcasting change', device.name, old_state, new_state)
                self.switch_all(new_state)
                break

    def switch_all(self, state):
        for device in self.devices.keys():
            device.set_state(state)
            self.devices[device] = state


if __name__ == '__main__':
    logging.config.dictConfig(LOGGING_CONFIG)
    SwitchSyncd().main()
