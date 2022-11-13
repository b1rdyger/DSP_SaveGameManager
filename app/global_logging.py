import logging

logger = logging.getLogger(__name__)


def wrap(pre, post):
    """ Wrapper """

    def decorate(func):
        """ Decorator """

        def call(*args, **kwargs):
            """ Actual wrapping """
            pre(func, *args)
            result = func(*args, **kwargs)
            post(func)
            return result

        return call

    return decorate


# noinspection SpellCheckingInspection
def wrapee():
    return wrap(entering, exiting)


def entering(func, *args):
    logger.debug(f'{func.__code__.co_filename}:{func.__code__.co_firstlineno+1}'
                 f' : Entering : {func.__name__}')


def exiting(func):
    logger.debug(f'{func.__code__.co_filename} : Exiting : {func.__name__}')
