# Lets a RemotiveStudio web page panel embed this notebook by widening Jupyter's
# default `frame-ancestors 'self'` CSP. Any page on loopback may frame the
# notebook, not just Studio.

c = get_config()  # noqa: F821

c.ServerApp.tornado_settings = {
    "headers": {
        "Content-Security-Policy": "frame-ancestors 'self' http://localhost:* https://localhost:* studio://app",
    }
}
