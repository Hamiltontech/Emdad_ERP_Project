import warnings
import emdad.http


def application(environ, start_response):

    warnings.warn("The WSGI application entrypoint moved from "
                  "emdad.service.wsgi_server.application to emdad.http.root "
                  "in 15.3.",
                  DeprecationWarning, stacklevel=1)
    return emdad.http.root(environ, start_response)
