# Copyright (C) 2016 SignalFx, Inc. All rights reserved.

from . import computation, ws
from .. import constants


class SignalFlowClient(object):
    """SignalFx SignalFlow client.

    Client for SignalFx's SignalFlow real-time analytics API. Allows for the
    execution of ad-hoc computations, returning its output in real-time as it
    is produced; to start new background computations; attach, keep alive or
    stop existing computations.
    """

    def __init__(self, token, endpoint=constants.DEFAULT_STREAM_ENDPOINT,
                 timeout=constants.DEFAULT_TIMEOUT,
                 transport=ws.WebSocketTransport):
        self._transport = transport(token, endpoint, timeout)
        self._computations = set([])

    def _get_params(self, **kwargs):
        return dict((k, v) for k, v in kwargs.items() if v)

    def execute(self, program, start=None, stop=None, resolution=None,
                max_delay=None, persistent=False):
        """Execute the given SignalFlow program and stream the output back."""
        params = self._get_params(start=start, stop=stop,
                                  resolution=resolution,
                                  maxDelay=max_delay,
                                  persistent=persistent)

        def exec_fn(since=None):
            if since:
                params['start'] = since
            return self._transport.execute(program, params)

        c = computation.Computation(exec_fn)
        self._computations.add(c)
        return c

    def start(self, program, start=None, stop=None, resolution=None,
              max_delay=None):
        """Start executing the given SignalFlow program without being attached
        to the output of the computation."""
        params = self._get_params(start=start, stop=stop,
                                  resolution=resolution,
                                  maxDelay=max_delay)
        self._transport.start(program, params)

    def attach(self, handle, filters=None, resolution=None):
        """Attach to an existing SignalFlow computation."""
        params = self._get_params(filters=filters, resolution=resolution)
        c = computation.Computation(
                lambda since: self._transport.attach(handle, params))
        self._computations.add(c)
        return c

    def keepalive(self, handle):
        """Keepalive a SignalFlow computation."""
        self._transport.keepalive(handle)

    def stop(self, handle, reason=None):
        """Stop a SignalFlow computation."""
        params = self._get_params(reason=reason)
        self._transport.stop(handle, params)

    def close(self):
        """Close this SignalFlow client."""
        self._transport.close()
