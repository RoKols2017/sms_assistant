"""Application error handlers."""

from __future__ import annotations

from flask import Flask, render_template, request


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(400)
    def bad_request(error):
        app.logger.warning(
            "[errors.bad_request] request failed extra=%s",
            {"path": request.path, "error": str(error)},
        )
        return render_template("errors/400.html"), 400

    @app.errorhandler(404)
    def not_found(error):
        app.logger.warning(
            "[errors.not_found] route missing extra=%s",
            {"path": request.path, "error": str(error)},
        )
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.exception(
            "[errors.internal_error] unhandled exception extra=%s",
            {"path": request.path, "error": str(error)},
        )
        return render_template("errors/500.html"), 500
