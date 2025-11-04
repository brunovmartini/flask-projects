from flask import Flask, Response
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError, Unauthorized, Forbidden, UnprocessableEntity
from sqlalchemy.exc import IntegrityError


def add_exception_handler(app: Flask):
    @app.errorhandler(BadRequest)
    def handle_bad_request_error(e):
        return Response(
            response='Invalid request body.',
            status=400
        )

    @app.errorhandler(Unauthorized)
    def handle_unauthorized_error(e):
        return Response(
            response=e.description,
            status=401
        )

    @app.errorhandler(Forbidden)
    def handle_forbidden_error(e):
        return Response(
            response='You do not have permission to perform this action.',
            status=403
        )

    @app.errorhandler(NotFound)
    def handle_not_found_error(e):
        return Response(
            response=e.description,
            status=404
        )

    @app.errorhandler(IntegrityError)
    def handle_conflict_error(e):
        return Response(
            response='Email already in use.',
            status=409
        )

    @app.errorhandler(UnprocessableEntity)
    def handle_unprocessable_entity_error(e):
        return Response(
            response='Current user can not be deleted.',
            status=422
        )

    @app.errorhandler(InternalServerError)
    def handle_internal_server_error(e):
        return Response(
            response=e.description,
            status=500
        )
