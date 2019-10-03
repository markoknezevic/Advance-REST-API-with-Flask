from flask_restful import Resource
from flask import request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_uploads import UploadNotAllowed

from libs import image_helper
from schemas.image import ImageSchema
from libs.strings import gettext
import os

image_schema = ImageSchema()

class Image(Resource):

    @classmethod
    @jwt_required
    def get(cls, filename):

        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        print(filename)
        if not image_helper.is_filename_safe(filename):
            return {'message': 'illegal file name'}, 400

        try:
            return send_file(image_helper.get_path(filename, folder=folder))

        except FileNotFoundError:
            return {'message': "Item not found"}, 404


    @classmethod
    @jwt_required
    def delete(cls, filename):

        user_id = get_jwt_identity()
        folder ='user_{}'.format(user_id)

        if not image_helper.is_filename_safe(filename):
            return {'message': 'Filename not safe'}
        print(image_helper.get_path(filename, folder=folder))
        try:
            os.remove(image_helper.get_path(filename, folder=folder))
            return {'message': 'image deleted'}, 200
        except FileNotFoundError:
            return {'message': 'File not found'}, 404
        except :
            return {'message': 'Internal error'}, 500




class ImageUpload(Resource):

    @classmethod
    @jwt_required
    def post(cls):
        data = image_schema.load(request.files)
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        try:
            image_path = image_helper.save_image(data["image"], folder=folder)
            basename = image_helper.get_basename(image_path)
            return {'message': gettext("image_uploaded").format(basename)}, 201
        except UploadNotAllowed:
            extension = image_helper.get_extension(data["image"])
            return {'message': gettext("image_illegal_extension").format(extension)}, 400


class AvatarUpload(Resource):
    @classmethod
    @jwt_required
    def put(cls):
        data = image_schema.load(request.files)
        filename = "user_{}".format(get_jwt_identity())
        folder = "avatar"

        avatar_path = image_helper.find_image_any_format(filename, folder=folder)
        if avatar_path:
            os.remove(avatar_path)

        try:
            ext = image_helper.get_extension(data["image"].filename)
            avatar = filename + ext
            avatar_path = image_helper.save_image(data["image"], folder=folder, name=avatar)
            return {'message': 'Avatar updated'}

        except UploadNotAllowed:
            ext = image_helper.get_extension(filename)
            return {'message': 'Avatar not updated. Extension {} not allowed'.format(ext)}

        except:
            return {'message': 'Avatar not updated'}


class Avatar(Resource):

    @classmethod
    def get(cls, user_id):
        folder = "avatar"
        filename = "user_{}".format(user_id)

        avatar = image_helper.find_image_any_format(filename, folder)
        if avatar:
            return send_file(avatar)
        return {'message': 'Avatar not found'}



