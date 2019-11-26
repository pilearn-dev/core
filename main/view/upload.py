import os, hashlib
from flask import request, redirect, url_for, render_template, send_file, abort
from model import user as muser, upload as mupload
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_PATH = os.path.abspath("upload-images")
USER_FILE_LIMIT = 40

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_dialog():
    cu = muser.getCurrentUser()
    if muser.require_login() or cu.isDisabled():
        abort(404)
    uc = mupload.UserUpload.has_by_user(cu)
    if uc > 0:
        if request.values.get("upload-for-sure", 0) == 0 or (uc >= USER_FILE_LIMIT and not cu.isTeam()):
            return render_template("uploader/dialog_select_first.html", cu=cu, images=mupload.UserUpload.get_by_user(cu), ufl=USER_FILE_LIMIT)
    return render_template("uploader/dialog.html", cu=cu)

def upload_dialog_new():
    cu = muser.getCurrentUser()
    if muser.require_login() or cu.isDisabled():
        abort(404)
    uc = mupload.UserUpload.has_by_user(cu)
    has_reached_limit = uc >= USER_FILE_LIMIT and not cu.isTeam()
    return render_template("uploader/inline-dialog.html", cu=cu, has_reached_limit=has_reached_limit)

def upload_get_image(id, fn=None):
    if not mupload.UserUpload.exists(id):
        abort(404)
    img = mupload.UserUpload(id)
    if img.isDeleted():
        abort(404)
    path = img.getPath()
    return send_file(os.path.join(UPLOAD_PATH, path))

def upload_download_image(id, fn=None):
    if not mupload.UserUpload.exists(id):
        abort(404)
    img = mupload.UserUpload(id)
    if img.isDeleted():
        abort(404)
    path = img.getPath()
    return send_file(os.path.join(UPLOAD_PATH, path), as_attachment=True, attachment_filename=path)

def upload_remove_image(id, fn=None):
    if not mupload.UserUpload.exists(id):
        abort(404)
    img = mupload.UserUpload(id)
    if img.isDeleted():
        abort(404)
    path = img.getPath()
    cu = muser.getCurrentUser()
    if cu.isMod() or cu.id == img.getDetail("user_id"):
        os.remove(os.path.join(UPLOAD_PATH, path))
        img.setDetail("removed_by", cu.id)
        return "Ok."
    return "Nope. :D"

def upload_post():
    cu = muser.getCurrentUser()
    if not cu.isLoggedIn() or cu.isDisabled():
        return redirect(url_for("upload_dialog", error="not-anonymous"))
    if 'file' not in request.files:
        return redirect(url_for("upload_dialog", error="not-selected"))
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return redirect(url_for("upload_dialog", error="not-selected"))

    if file and allowed_file(file.filename):
        filext = file.filename.rsplit('.', 1)[1].lower()

        img_key = hashlib.md5(file.read()).hexdigest()
        file.seek(0)
        file.save(os.path.join(UPLOAD_PATH, img_key + "." + filext))

        filesize = os.stat(os.path.join(UPLOAD_PATH, img_key + "." + filext)).st_size

        img = mupload.UserUpload.new(cu, img_key + "." + filext, filesize)


        return render_template("uploader/info.html", filepath="/upload/"+str(img)+"/"+secure_filename(file.filename))
    return redirect(url_for("upload_dialog", error="not-allowed"))

def apply(app):
    app.route("/upload/dialog")(upload_dialog)
    app.route("/upload/dialog/new")(upload_dialog_new)
    app.route("/upload/post", methods=["POST"])(upload_post)
    app.route("/upload/<int:id>/<fn>")(upload_get_image)
    app.route("/upload/<int:id>/info")(upload_get_image)
    app.route("/upload/<int:id>/<fn>/download")(upload_download_image)
    app.route("/upload/<int:id>/<fn>/remove")(upload_remove_image)
