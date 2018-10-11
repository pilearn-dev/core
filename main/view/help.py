# coding: utf-8
from flask import render_template, abort, request, redirect, url_for
from model import privileges as mprivileges, user as muser, help as mhelp
import time, re

def help_index():
    return render_template('help/index.html', title=u"Hilfe", thispage="help", help_cat=mhelp.HelpCategory)

def help_cathome(caturl):
    if mhelp.HelpCategory.exists_url(caturl):
        cat = mhelp.HelpCategory.from_url(caturl)
        cuser = muser.getCurrentUser()
        if not cat.isActive() and not cuser.isAdmin():
            abort(404)
        if request.values.get("editor", "no") == "yes" and cuser.isAdmin() and (cat.mayAdminEdit() or cuser.isTeam()):
            if request.method == "POST":
                if not cuser.isTeam() or request.form["action"] == "save":
                    cat.setDetail("override_excerpt", request.form["excerpt"])
                elif cuser.isTeam() and request.form["action"] == "replace":
                    cat.setDetail("original_excerpt", request.form["excerpt"])
                    cat.setDetail("override_excerpt", "")
                elif cuser.isTeam() and request.form["action"] == "reset":
                    cat.setDetail("override_excerpt", "")

                if request.form["action"] != "reset" or not cuser.isTeam():
                    cat.setDetail("title", request.form["title"])
                    cat.setDetail("cat_symbol", request.form["cat_symbol"])
                    if cuser.isTeam():
                        cat.setDetail("active", request.form.get("active", "false")=="true")
                        cat.setDetail("editable_by_admin", request.form.get("may_edit", "false")=="true")
                        cat.setDetail("newpage_by_admin", request.form.get("subpage", "false")=="true")
                        cat.setDetail("url_part", request.form["url_part"])
                        caturl = request.form["url_part"]

                return redirect(url_for("help_cathome", caturl=caturl, editor="no"))
            return render_template('help/cathome--editor.html', title=u"Hilfe - Kategorie: " + cat.getTitle(), thispage="help", cat=cat)
        else:
            return render_template('help/cathome.html', title=u"Hilfe - Kategorie: " + cat.getTitle(), thispage="help", cat=cat)
    else:
        abort(404)


def help_any(fullurl):
    if mhelp.HelpEntry.exists_url(fullurl):
        entry = mhelp.HelpEntry.from_url(fullurl)
        cuser = muser.getCurrentUser()
        if not entry.isActive() and not cuser.isAdmin():
            abort(404)
        cat = mhelp.HelpCategory(entry.getDetail("help_cat"))
        if request.values.get("editor", "no") == "yes" and cuser.isAdmin() and (entry.mayAdminEdit() or cuser.isTeam()):
            if request.method == "POST":
                if not cuser.isTeam() or request.form["action"] == "save":
                    entry.setDetail("override_content", request.form["content"])
                    entry.setDetail("last_change", time.time())
                    entry.setDetail("last_editor", cuser.id)
                elif cuser.isTeam() and request.form["action"] == "replace":
                    entry.setDetail("original_content", request.form["content"])
                    entry.setDetail("override_content", "")
                    entry.setDetail("last_change", 0)
                    entry.setDetail("last_editor", 0)
                elif cuser.isTeam() and request.form["action"] == "reset":
                    entry.setDetail("override_content", "")
                    entry.setDetail("last_change", 0)
                    entry.setDetail("last_editor", 0)

                if request.form["action"] != "reset" or not cuser.isTeam():
                    entry.setDetail("title", request.form["title"])
                    if cuser.isTeam():
                        entry.setDetail("active", request.form.get("active", "false")=="true")
                        entry.setDetail("is_pinned", request.form.get("pinned", "false")=="true")
                        entry.setDetail("is_deprecated", request.form.get("deprecated", "false")=="true")
                        entry.setDetail("editable_by_admin", request.form.get("may_edit", "false")=="true")
                        entry.setDetail("subpage_by_admin", request.form.get("subpage", "false")=="true")
                        entry.setDetail("url_part", request.form["url_part"])
                        entry._HelpEntry__data = entry.getInfo()

                fullurl = cat.getDetail("url_part")
                mp = entry.getDetail("master_page")
                while mp != 0:
                    mp = mhelp.HelpEntry(mp)
                    fullurl += "/" + mp.getDetail("url_part")
                    mp = mp.getDetail("master_page")
                fullurl += "/" + entry.getDetail("url_part")
                entry.setDetail("url", fullurl)

                return redirect(url_for("help_any", fullurl=fullurl, editor="no"))
                #render_template('help/'+entry.getTemplate()+'--editor.html', title=u"Hilfe - " + entry.getTitle(), thispage="help", cat=cat, entry=entry, done=True)
            return render_template('help/'+entry.getTemplate()+'--editor.html', title=u"Hilfe - " + entry.getTitle(), thispage="help", cat=cat, entry=entry, done=False)
        else:
            return render_template('help/'+entry.getTemplate()+'.html', title=u"Hilfe - " + entry.getTitle(), thispage="help", cat=cat, entry=entry)
    else:
        abort(404)

def help_newelement(element):
    if element == "entry":
        cat = request.values.get("category", "@")
        if mhelp.HelpCategory.exists_url(cat):
            cat = mhelp.HelpCategory.from_url(cat)
            cuser = muser.getCurrentUser()
            if not cat.isActive() and not cuser.isAdmin():
                abort(400)
            if not (cat.mayAdminCreateNewpage() or cuser.isTeam()):
                abort(403)

            try:
                parent = int(request.values.get("parent", 0))
            except:
                abort(400)
            if parent != 0:
                if not mhelp.HelpEntry.exists(parent):
                    abort(400)
                parent = mhelp.HelpEntry(parent)
                if parent.getDetail("help_cat") != cat.id:
                    abort(400)
            else:
                parent = None
            if request.method == "POST":
                t = request.form.get("title", "Neuer Beitrag")
                u = t.replace(u"π", "pi")
                u = re.sub("[^a-zA-Z0-9- ]+", "", u)
                u = re.sub("[ ]+", "-", u)
                u = u.lower()[:50].strip("-")
                x = mhelp.HelpEntry.create_new(cat.id, parent.id if parent else 0, t, u)
                return redirect(url_for("help_any", fullurl=x.getUrl(), editor="yes"))
            return render_template('help/new--entry.html', title=u"Hilfe", thispage="help", cat=cat, parent=parent)
        else:
            abort(400)
    abort(404)



def h():
    data = mprivileges.getInformations()
    data = sorted(data, key=lambda x:mprivileges.getOne(x["id"]))
    return render_template('help/privileges.html', data=data, title=u"Hilfe", thispage="help")

def apply(app):
    app.route("/help/")(help_index)
    app.route("/help/category:<caturl>", methods=["GET", "POST"])(help_cathome)
    app.route("/help/new:<element>", methods=["GET", "POST"])(help_newelement)
    app.route("/help/<path:fullurl>", methods=["GET", "POST"])(help_any)
