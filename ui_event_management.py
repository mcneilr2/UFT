from threading import Thread as thr


def th_test_initiate():
    t_test_initiate=thr(target = test_initiate)
    t_test_initiate.start()
def test_initiate():
    print('test initiate')


def th_display_force():
    t_display_force=thr(target = display_force)
    t_display_force.start()
def display_force():
    print('display force')


def th_move():
    t_move=thr(target = move)
    t_move.start()
def move():
    print('move')


def th_home():
    t_home=thr(target = home)
    t_home.start()
def home():
    print('home')


def th_commit():
    t_commit=thr(target = commit)
    t_commit.start()
def commit():
    print('commit')


def th_calibration():
    t_calibration=thr(target = calibrate)
    t_calibration.start()
def calibrate():
    print('calibrate')