#! /usr/bin/python
import os, sys
sys.path.append("./main")
sys.path.append("./election")
sys.path.append("./helpdesk")
sys.path.append("./chat")

from werkzeug.wsgi import DispatcherMiddleware
from main import app as main
from election import app as election
from helpdesk import app as helpdesk
#from pychat import app as chat

app = DispatcherMiddleware(main, {
    '/election': election,
    '/helpdesk': helpdesk,
#    '/beta-chat': chat
})


if __name__ == "__main__":
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 80, app, use_reloader=True)
