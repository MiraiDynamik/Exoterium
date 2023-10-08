import hashlib


def getUserID(session):
    if session is not None:
        userSub = session['userinfo']['sub']
        md5 = hashlib.md5()
        md5.update(userSub.encode("utf-8"))
        userID = md5.hexdigest()
        return userID
    else:
        return None
