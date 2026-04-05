"""WSGI entrypoint for the application package."""

from app import create_app


app = create_app()
