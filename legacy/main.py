import logging
import time
import signal
import sys
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm

uris = {
    'radio://0/100/2M/E7E7E7E702',
    'radio://0/100/2M/E7E7E7E703',
}

# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

# Define a signal handler function
def signal_handler(sig, frame):
    print('Signal', sig, 'received. Exiting...')
    sys.exit(0)


def log_stab_callback(timestamp, data, logconf):
    print('[%d][%s]: %s' % (timestamp, logconf.name, data))

def simple_log_async(sync_cf, logconf):
    cf = sync_cf.cf
    cf.log.add_config(logconf)
    logconf.data_received_cb.add_callback(log_stab_callback)
    logconf.start()

def activate_led_bit_mask(scf):
    scf.cf.param.set_value('led.bitmask', 255)

def deactivate_led_bit_mask(scf):
    scf.cf.param.set_value('led.bitmask', 0)

def light_check(scf):
    activate_led_bit_mask(scf)
    time.sleep(1)
    deactivate_led_bit_mask(scf)

def take_off(scf):
    commander= scf.cf.high_level_commander

    commander.takeoff(1.0, 2.0)
    time.sleep(3)

def land(scf):
    commander= scf.cf.high_level_commander

    commander.land(0.0, 2.0)
    time.sleep(2)

    commander.stop()

def hover_sequence(scf):
    take_off(scf)
    land(scf)


def run_square_sequence(scf: SyncCrazyflie):
    box_size = 0.8
    flight_time = 1.5

    commander= scf.cf.high_level_commander

    commander.go_to(box_size, 0, 0, 0, flight_time, relative=True)
    time.sleep(flight_time)

    commander.go_to(0, box_size, 0, 0, flight_time, relative=True)
    time.sleep(flight_time)

    commander.go_to(-box_size, 0, 0, 0, flight_time, relative=True)
    time.sleep(flight_time)

    commander.go_to(0, -box_size, 0, 0, flight_time, relative=True)
    time.sleep(flight_time)

def log_data(timestamp, data, logconf):
    """Callback from a the log API when data arrives"""
    print(f'[{timestamp}][{logconf.name}]: ', end='')
    for name, value in data.items():
        print(f'{name}: {value:3.3f} ', end='')
    print()

def log_error(logconf, msg):
    """Callback from the log API when an error occurs"""
    print('Error when logging %s: %s' % (logconf.name, msg))

def log_async(scf: SyncCrazyflie):
    log_config = LogConfig(name='Stabilizer', period_in_ms=100)
    log_config.add_variable('stateEstimate.x', 'float')
    log_config.add_variable('stateEstimate.y', 'float')
    log_config.add_variable('stateEstimate.z', 'float')
    log_config.add_variable('stabilizer.roll', 'float')
    log_config.add_variable('stabilizer.pitch', 'float')
    log_config.add_variable('stabilizer.yaw', 'float')

    # Set configuration
    scf.cf.log.add_config(log_config)
    # This callback will receive the data
    log_config.data_received_cb.add_callback(log_data)
    # This callback will be called on errors
    log_config.error_cb.add_callback(log_error)
    # Start the logging
    log_config.start()


if __name__ == '__main__':
    # Register the signal handler for SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)

    # Initialize the low-level drivers
    cflib.crtp.init_drivers()

    factory = CachedCfFactory(rw_cache='./cache')

    with Swarm(uris, factory=factory) as swarm:
        # swarm.parallel_safe(light_check)
        swarm.reset_estimators()
        swarm.parallel_safe(log_async)
        time.sleep(10)
        # swarm.parallel_safe(take_off)
        # swarm.parallel_safe(land)
        ...
