import logging

from toolbox import make_directory, time_for_files


def setup_logging(name=None, log_path=None, level=logging.DEBUG, out_to_log_and_console=True, console_level=logging.INFO):
    """
    Sets up my logging files
    :return:
    """
    if name is None:
        name = "Routing"
    [logging.root.removeHandler(handler) for handler in logging.root.handlers[:]]
    log_path = './output/logs/' if log_path is None else log_path
    fn = f'{log_path}/{name}_{time_for_files()}.log'
    make_directory(fn)
    fmt_log = '%(asctime)s %(levelname)-9s [%(funcName)-24s] %(message)-120s [%(module)s : %(lineno)d]'
    logging.basicConfig(filename=fn, format=fmt_log, level=level)
    if out_to_log_and_console:
        console = logging.StreamHandler()
        console.setLevel(console_level)
        fmt_out = '%(asctime)s %(levelname).6s [%(funcName).12s] %(message)-60s (Module:%(module)s Line:%(lineno)d)'
        console.setFormatter(logging.Formatter(fmt_out, datefmt='%Y-%m-%d %H:%M:%S'))
        logging.getLogger('').addHandler(console)
    print(f'Completed Setting up log in {fn}')
    logging.debug(f'Completed Setting up log in {fn}')


# 10 DEBUG:     Detailed information, typically of interest only when diagnosing problems.
# 20 INFO:      Confirmation that things are working as expected.
# 30 WARNING:   An indication that something unexpected happened, or indicative of some problem in the
#               near future (e.g. ‘disk space low’). The software is still working as expected.
# 40 ERROR:     Due to a more serious problem, the software has not been able to perform some function.
# 50 CRITICAL:  A serious error, indicating that the program itself may be unable to continue running.
