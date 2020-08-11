from flask import request, Response
from socialgroupmain.model.models import User,Group
from flask_restful import Resource
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    if User.objects.filter(name=username).first():
        user = User.objects.filter(name=username).first()
        if check_password_hash(user.password, password):
            return True

# Sign up page for user


class SignupApi(Resource):
    def post(self):
        # name and email is supplied in body
        try:
            body = request.get_json()
            body['password'] = generate_password_hash(body['password'])
            user = User(**body).save()
            userid = user.id
            return {'userid': str(userid)}, 200
        except:
            return "username should be unique try again",500


class GetUserApi(Resource):
    @auth.login_required
    def get(self):
        user = request.authorization
        uid = User.objects(name=user['username']).to_json()

        return Response(uid, mimetype="application/json", status=200)


class DeleteUserApi(Resource):
    @auth.login_required
    def delete(self):
        user = request.authorization
        uid = User.objects.get(name=user['username'])
        userid = str(uid.id)
        uid.delete()
        groups = Group.objects()
        for group in groups:
            temp = group.role_dict
            lastactive = group.lastactive_dict
            if userid in temp and lastactive:
                for key in list(group.role_dict):
                    if key == userid:
                        del temp[userid]
                        break
                # element should be deleted in dict via this way otherwise iteration error
                for key in list(group.lastactive_dict):
                    if key == userid:
                        del lastactive[userid]
                        break
            elif userid in temp:
                for key in list(group.role_dict):
                    if key == userid:
                        del temp[userid]
                        break
            else:
                continue
            group.update(set__lastactive_dict=lastactive)
            group.update(set__role_dict=temp)
        return "User deleted successfully", 500






