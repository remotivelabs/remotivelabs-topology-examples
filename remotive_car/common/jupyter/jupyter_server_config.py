# Allow RemotiveStudio's web page panel to embed this notebook.
#
# jupyter_server defaults to `Content-Security-Policy: frame-ancestors 'self'`,
# where 'self' is http://localhost:8888 — so Studio, served from a different
# origin, cannot render the frame. There is no dedicated CSP trait; overriding
# tornado_settings["headers"] is the only supported way to change the header
# (AuthenticatedHandler.content_security_policy checks it before falling back
# to its default).
#
# NOTE: this lets any page on loopback frame this notebook, not just Studio.
# That is acceptable for a local example topology and should not be copied
# into anything reachable from off the machine.

c.ServerApp.tornado_settings = {  # noqa: F821  (`c` is injected by traitlets)
    "headers": {
        "Content-Security-Policy": "frame-ancestors 'self' http://localhost:* https://localhost:* studio://app",
    }
}
