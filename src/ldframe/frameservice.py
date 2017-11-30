import click
import multiprocessing
import gunicorn.app.base
from ldframe.app import init_api
from gunicorn.six import iteritems
from ldframe.utils.broker import broker
from ldframe.applib.messaging import ScalableRpcServer


@click.group()
def cli():
    """Run cli tool."""
    pass


@cli.command('server')
@click.option('--host', default='127.0.0.1', help='indexservice host.')
@click.option('--port', default=4303, help='indexservice server port.')
@click.option('--workers', default=2, help='indexservice server workers.')
@click.option('--log', default='logs/server.log', help='log file for app.')
def server(host, port, log, workers):
    """Run web server with options."""
    options = {
        'bind': '{0}:{1}'.format(host, port),
        'workers': workers,
        'daemon': 'True',
        'errorlog': log
    }
    FramingService(init_api(), options).run()


@cli.command('rpc')
def rpc():
    """RPC server."""
    RPC_SERVER = ScalableRpcServer(broker['host'], broker['user'], broker['pass'], broker['rpcqueue'])
    RPC_SERVER.start_server()


class FramingService(gunicorn.app.base.BaseApplication):
    """Create Standalone Application Framing Service."""

    def __init__(self, app, options=None):
        """The init."""
        self.options = options or {}
        self.application = app
        super(FramingService, self).__init__()

    def load_config(self):
        """Load configuration."""
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        """Load configuration."""
        return self.application


# Unless really needed to scale use this function. Otherwise 2 workers suffice.
def number_of_workers():
    """Establish the number or workers based on cpu_count."""
    return (multiprocessing.cpu_count() * 2) + 1


def main():
    """Main function."""
    cli()


if __name__ == '__main__':
    main()
