# Python 2 backwards compatibility
from __future__ import unicode_literals, print_function

from threading import Event, Thread
import logging
logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)s [%(name)s] {%(threadName)s} %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from IoticAgent import IOT


class ThingRunner(object):

    def __init__(self, config=None):
        """config: IOT.Client config file to use (or None to try to use default location"""
        self.__client = IOT.Client(config=config)
        self.__shutdown = Event()
        self.__bgthread = None

    def run(self, background=False):
        """Runs on_startup, main and on_shutdown, blocking until finished, unless background is set."""
        if self.__bgthread:
            raise Exception('run has already been called (since last stop)')
        self.__shutdown.clear()
        if background:
            self.__bgthread = Thread(target=self.__run, name=('bg_' + self.__client.agent_id))
            self.__bgthread.daemon = True
            self.__bgthread.start()
        else:
            self.__run()

    def __run(self):
        with self.__client:
            logger.debug('Calling on_startup')
            self.on_startup()
            logger.debug('Calling main')
            try:
                self.main()
            except Exception as ex:  # pylint: disable=broad-except
                exception = ex
                if not isinstance(ex, KeyboardInterrupt):
                    logger.warning('Exception in main(): %s', ex)
            else:
                exception = None
            logger.debug('Calling on_shutdown')
            self.on_shutdown(exception)

    def stop(self, timeout=None):
        """Requests device to stop running, waiting at most the given timout in seconds (fractional). Has no effect if
        run() was not called with background=True set."""
        self.__shutdown.set()
        if self.__bgthread:
            logger.debug('Stopping bgthread')
            self.__bgthread.join(timeout)
            if self.__bgthread.is_alive():
                logger.warning('bgthread did not finish within timeout')
            self.__bgthread = None

    @property
    def client(self):
        return self.__client

    @property
    def shutdown_requested(self):
        """Whether stop() has been called and thus the device should be shutting down"""
        return self.__shutdown.is_set()

    def wait_for_shutdown(self, timeout=None):
        """Blocks until shutdown has been requested (or the timeout has been reached, if specified). False is returned
        for the latter, True otherwise."""
        return self.__shutdown.wait(timeout)

    def on_startup(self):
        """One-off tasks to perform straight AFTER agent startup."""
        pass

    def main(self):  # pylint: disable=no-self-use
        """Application logic goes here. Should return (or raise exception) to end program run. Should check whether the
        shutdown_requested property is True an return if this is the case."""
        pass

    def on_shutdown(self, exc):  # pylint: disable=no-self-use
        """One-off tasks to perform on just before agent shutdown. exc is the exception which caused the shutdown (from
        the main() function) or None if the shutdown was graceful. This is useful if one only wants to perform certains
        tasks on success. This is not called if on_startup() was not successful. It is possible that due to e.g. network
        problems the agent cannot be used at this point.
        If not overriden, the exception will be re-raised."""
        if exc is not None:
            raise exc
