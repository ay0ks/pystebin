#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ANNIHILATION <annihilation.ga>
# Dimitriy i0x <contact@annihilation.ga>

import random

import beaker.middleware

from dominate import document
from dominate.util import raw
from dominate.tags import *
from pony.orm import *
from bottle import *


db = Database()
db.bind(provider="mysql", host="localhost", user="root", passwd="", db="paste")
app = beaker.middleware.SessionMiddleware(
    app(),
    {
        "session.type": "file",
        "session.data_dir": "./session/",
        "session.auto": True,
        "session.cookie_expires": True,
    },
)


class Paste(db.Entity):
    id = PrimaryKey(str)
    paste = Required(unicode, max_len=16777215)


# set_sql_debug(True)
db.generate_mapping(create_tables=True)


@hook("after_request")
def enable_cors():
    response.headers["Access-Control-Allow-Origin"] = "self"


@hook("before_request")
def setup_request():
    request.session = request.environ["beaker.session"]


@get("/")
def index():
    if not "id" in request.session:
        request.session["id"] = "%030x" % random.randrange(16 ** 64)
    else:
        request.session["id"] = "%030x" % random.randrange(16 ** 64)

    with document(title="pystebin") as doc:
        with doc.head:
            meta(name="viewport", content="width=device-width, initial-scale=1")
            link(rel="stylesheet", href="/static/pystebin.css")

        with doc.body:
            attr(onload="brython()")
            with div(id="page"):
                textarea(
                    id="paste",
                    name="paste",
                    placeholder="Paste..",
                    spellcheck=False,
                )

                with div(id="controls"):
                    span("Not saved", id="status")
                    raw("&nbsp;:&nbsp;")
                    a("new", href="/")
                    raw("&nbsp;&bull;&nbsp;")
                    a("about", href="/about")

            script(defer=True, src="/static/pystebin.js")

        return template(doc.render(pretty=False))


@get("/<paste:re:[a-f0-9]+>")
@db_session
def view_paste(paste):
    if Paste.exists(id=paste):
        paste = Paste.get(id=paste)
    else:
        response.status = 404

    with document(title="pystebin") as doc:
        with doc.head:
            meta(name="viewport", content="width=device-width, initial-scale=1")
            link(rel="stylesheet", href="/static/pystebin.css")

        with doc.body:
            with div(id="page"):
                textarea(paste.paste, readonly=True, spellcheck=False)

                with div(id="controls"):
                    span("Viewing paste", id="status")
                    raw("&nbsp;:&nbsp;")
                    a("new", href="/")
                    raw("&nbsp;&bull;&nbsp;")
                    a("about", href="/about")

        return template(doc.render(pretty=False))


@post("/paste")
@db_session
def create_paste():
    response.content_type = "application/json; charset=utf-8"
    content = request.forms.get("paste")

    if not Paste.exists(id=request.session["id"]):
        Paste(id=request.session["id"], paste=content)
        commit()
    else:
        Paste.get(id=request.session["id"]).set(paste=content)

    return {"id": request.session["id"]}


@get("/about")
def about():
    about = "<br>".join(open("./static/about.txt", "r").readlines())
    with document(title="pystebin : about") as doc:
        with doc.head:
            meta(name="viewport", content="width=device-width, initial-scale=1")

        with doc.body:
            p(raw(about))

        return template(doc.render(pretty=False))


@get("/static/<name>")
def static(name):
    return static_file(name, root="./static")


@get("/favicon.ico")
def favicon():
    return static_file("favicon.ico", root="./static")


@error(404)
def not_found(error):
    return error


@error(403)
def forbidden(error):
    return error


run(app=app, host="localhost", port=8118)
