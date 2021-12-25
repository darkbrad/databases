from flask import Blueprint, jsonify, request, redirect
from core import errors
from schemas.user import RegistrationModel
from crud import user_crud, posts_crud, follow_crud
from core.db import get_connection
from blueprints import deps

user_blueprint = Blueprint("user_blueprint", __name__, url_prefix="/user")


@user_blueprint.route("", methods=["POST"])
def register():
    registration_data = deps.get_input(RegistrationModel)

    with get_connection() as conn:
        user_crud.create(conn, registration_data)

    return jsonify({"info": "OK"}), 201


@user_blueprint.route("")
def get_user_data():
    current_user = deps.get_current_user()
    return redirect(f"/api/user/{current_user.login}")


@user_blueprint.route("/posts")
def get_user_posts():
    current_user = deps.get_current_user()
    return redirect(f"/api/user/{current_user.login}/posts")


@user_blueprint.route("<string:login>")
def get_selected_user_data(login: str):
    user_data = deps.get_user_by_login(login)
    return jsonify(user_data.dict())


@user_blueprint.route("/myposts")
def get_selected_user_posts():
    user_data = deps.get_current_user()

    with get_connection() as conn:
        posts = posts_crud.get_by_creator(conn, user_data)

    return jsonify([post.dict() for post in posts])


@user_blueprint.route("<string:login>/follow", methods=["POST"])
def follow(login: str):
    current_user = deps.get_current_user()
    user_to_follow = deps.get_user_by_login(login)

    if current_user.id == user_to_follow.id:
        raise errors.ForbiddenError("Can not follow yourself")

    with get_connection() as conn:
        if follow_crud.exists(conn, current_user, user_to_follow):
            raise errors.ConflictError("Already subscribed")

        follow_crud.create(conn, current_user, user_to_follow)

    return jsonify({"info": "OK"})


@user_blueprint.route("<string:login>/follow", methods=["DELETE"])
def unfollow(login: str):
    current_user = deps.get_current_user()
    user_to_un_follow = deps.get_user_by_login(login)

    if current_user.id == user_to_un_follow.id:
        raise errors.ForbiddenError("Can not unfollow yourself")

    with get_connection() as conn:
        if not follow_crud.exists(conn, current_user, user_to_un_follow):
            raise errors.ConflictError("Already not subscribed")

        follow_crud.delete(conn, current_user, user_to_un_follow)

    return jsonify({"info": "OK"})

@user_blueprint.route("/follow")
def get_followers_and_follows():
    current_user=deps.get_current_user()
    with get_connection() as conn:
        user_crud.get_followers_and_follows(current_user)