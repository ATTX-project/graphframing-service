import falcon
from ldframe.utils.logs import app_logger
from ldframe.api.healthcheck import HealthCheck

api_version = "0.2"  # TO DO: Figure out a better way to do versioning


def init_api():
    """Create the API endpoint."""
    ldframe = falcon.API()

    ldframe.add_route('/health', HealthCheck())

    app_logger.info('FramingService REST API is running.')
    return ldframe


# if __name__ == '__main__':
#     init_api()
