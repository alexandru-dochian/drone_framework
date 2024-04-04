import threading
import numpy as np
import logging
import time
import cflib.crtp
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.crazyflie.swarm import Swarm
from cflib.crazyflie.swarm import CachedCfFactory
import pygame
from pygame.locals import *
import matplotlib.pyplot as plt
from matplotlib import cm, colors
from matplotlib import patches
import json

experiment_name = "Experiment_1"
# if not os.path.isdir(experiment_name):
#     os.mkdir(experiment_name)
#     print("The directory is created.")
# else:
#     print("The experiment directory already exists!!q!")
#     exit()

num_cf = 5
max_num_cf = 10
max_datapoint = 30000
data = []
id_list = []
log_all = np.zeros([max_datapoint*num_cf, 4])
steps_last = np.zeros([1, num_cf])
steps = np.zeros(max_num_cf)
xs = np.zeros(max_num_cf)
ys = np.zeros(max_num_cf)
hs = np.zeros(max_num_cf)
ls = np.zeros(max_num_cf)

global config
config = {}
# config_file = "./config.json"
# with open(config_file, "r") as f:
#     config = json.loads(f.read())

def display(str):
    screen.fill((255, 128, 0))
    text = font.render(str, True, (255, 255, 255), (159, 182, 205))
    textRect = text.get_rect()
    textRect.centerx = screen.get_rect().centerx
    textRect.centery = screen.get_rect().centery

    screen.blit(text, textRect)
    pygame.display.update()

def decode_aggdata(noncoded):
    x = int(np.floor(noncoded/np.power(10, 7)))/10
    noncoded = noncoded - x*10*np.power(10, 7)
    y = int(np.floor(noncoded / np.power(10, 5))) / 10
    noncoded = noncoded - y * 10 * np.power(10, 5)
    h = int(np.floor(noncoded / np.power(10, 3))) / 10
    noncoded = noncoded - h * 10 * np.power(10, 3)
    l = noncoded
    return x, y, h, l


def logg_swarm(scf):
    log_config = LogConfig(name="synthLog", period_in_ms=500)
    log_config.add_variable("synthLog.agg_data", "int32_t")
    log_config.add_variable("synthLog.agent_id", "uint8_t")

    with SyncLogger(scf, log_config) as logger:
        for entry in logger:
            agg_data = entry[1]["synthLog.agg_data"]
            agent_id = entry[1]["synthLog.agent_id"]
            x, y, h, l = decode_aggdata(agg_data)
            log_all[int((agent_id-1) + steps[agent_id-1]*max_num_cf), :] = x, y, h, l
            # print("x:", x)
            # print("y:", y)
            # print("h:", h)
            # print("l:", l)
            xs[int(agent_id-1)] = x
            ys[int(agent_id-1)] = y
            hs[int(agent_id-1)] = h
            ls[int(agent_id-1)] = l
            steps[agent_id-1] = steps[agent_id-1] + 1


def _take_off(scf):
    cf = scf.cf
    cf.param.set_value("fmodes.if_takeoff", 1)
    # cf.param.set_value("fmodes.fmode", 1)
    time.sleep(0.1)


def take_off(swarm):
    swarm.parallel_safe(_take_off)


def _land(scf):
    cf = scf.cf
    cf.param.set_value("fmodes.if_land",1)
    time.sleep(0.1)


def land(swarm):
    swarm.parallel_safe(_land)


def _terminate(scf):
    cf = scf.cf
    cf.param.set_value("fmodes.if_terminate",1)
    time.sleep(0.1)


def terminate(swarm):
    swarm.parallel_safe(_terminate)


def _update_param(scf):
    global config
    cf = scf.cf
    #####################
    sigma_base = config["sigma_base"]
    sigma_var = config["sigma_var"]
    k1 = config["k1"]
    k2 = config["k2"]
    alpha = config["alpha"]
    beta = config["beta"]
    kappa = config["kappa"]
    light_max = config["light_max"]
    light_min = config["light_min"]
    flight_height = config["flight_height"]
    umax = config["umax"]
    wmax = config["wmax"]
    u_add = config["u_add"]
    update_params = 1
    #####################
    cf.param.set_value("flockParams.sb_param", sigma_base)
    cf.param.set_value("flockParams.sv_param", sigma_var)
    cf.param.set_value("flockParams.k1_param", k1)
    cf.param.set_value("flockParams.k2_param", k2)
    cf.param.set_value("flockParams.alpha_param", alpha)
    cf.param.set_value("flockParams.beta_param", beta)
    cf.param.set_value("flockParams.kappa_param", kappa)
    cf.param.set_value("flockParams.lmx_param", light_max)
    cf.param.set_value("flockParams.lmn_param", light_min)
    cf.param.set_value("flockParams.fh_param", flight_height)
    cf.param.set_value("flockParams.umax_param", umax)
    cf.param.set_value("flockParams.wmax_param", wmax)
    cf.param.set_value("flockParams.u_add_param", u_add)
    cf.param.set_value("flockParams.update_params", update_params)
    print("update finished")


def update_param(swarm):
    swarm.parallel_safe(_update_param)

def log_swarm(swarm):
    swarm.parallel_safe(logg_swarm)


if __name__ == "__main__":

    uris = {
        # 'radio://0/100/2M/E7E7E7E701',
        'radio://0/100/2M/E7E7E7E702',
        'radio://0/100/2M/E7E7E7E703',
        # 'radio://0/100/2M/E7E7E7E704',
        # 'radio://0/100/2M/E7E7E7E705',
        # 'radio://0/100/2M/E7E7E7E706',
        # 'radio://0/100/2M/E7E7E7E707',
        # 'radio://0/100/2M/E7E7E7E70A',
        # 'radio://0/100/2M/E7E7E7E709',
        # 'radio://0/100/2M/E7E7E7E708',
    }

    size_x = 8.0
    size_y = 6.0
    norm = colors.Normalize(vmin=50.0, vmax=600.0, clip=True)
    mapper = cm.ScalarMappable(norm=norm, cmap=cm.inferno)

    plt.ion()
    plt.show()

    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Python numbers')
    screen.fill((255, 128, 0))
    font = pygame.font.Font(None, 45)
    done = False

    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)
    factory = CachedCfFactory(rw_cache='./cache')
    display_msg = "No key is pressed!"
    last = time.time()
    last_pressed = time.time()
    with Swarm(uris, factory=factory) as swarm:
        thread_1 = threading.Thread(target=log_swarm, args=([swarm]))
        thread_1.start()
        log_index = 0
        while not done:
            pygame.event.pump()
            keys = pygame.key.get_pressed()
            display(display_msg)
            if time.time() - last > 0.5:
                last = time.time()
                ##PLOT##
                plt.clf()
                plt.axis([-1, size_x, -1, size_y])
                rect = patches.Rectangle((0.0, 0.0), 5.81, 4.12, linewidth=5, edgecolor='r', facecolor='none')
                ax = plt.gca()
                ax.add_patch(rect)
                plt.scatter(xs, ys, color=mapper.to_rgba(ls))
                plt.scatter(np.mean(xs), np.mean(ys), color='red')
                # print("X-Com is: ", np.mean(xs), " ||| Y-Com is: ", np.mean(ys))
                plt.quiver(xs, ys, np.cos(hs), np.sin(hs))
                plt.draw()
                plt.pause(0.01)
                steps_last = steps
                log_index += 1
                ###
            if keys[pygame.locals.K_ESCAPE]:
                done = True
            if keys[pygame.locals.K_t] and ((time.time() - last_pressed) > 0.5):
                take_off(swarm)
                display_msg = "Takeoff command is sent!"
                last_pressed = time.time()
            elif keys[pygame.locals.K_l] and ((time.time() - last_pressed) > 0.5):
                land(swarm)
                display_msg = "Land command is sent!"
                last_pressed = time.time()
            elif keys[pygame.locals.K_e] and ((time.time() - last_pressed) > 0.5):
                terminate(swarm)
                display_msg = "Emergency terminate command is sent!"
                last_pressed = time.time()
            elif keys[pygame.locals.K_u] and ((time.time() - last_pressed) > 0.5):
                with open(config_file, "r") as f:
                    config = json.loads(f.read())
                    print("New config file loaded")
                time.sleep(0.5)
                update_param(swarm)
                display_msg = "Parameters are updated!"
                last_pressed = time.time()
            elif keys[pygame.locals.K_q] and ((time.time() - last_pressed) > 0.5):
                display_msg = "Terminate the experiment!"
                last_pressed = time.time()
                # np.save(experiment_name + "/log_data_1.npy", log_all)
                # np.save(experiment_name + "/steps_last.npy", steps_last)
                exit()