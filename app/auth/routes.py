import logging

from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.services.auth_service import AuthService


logger = logging.getLogger(__name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        logger.info("[auth.login] attempt extra=%s", {"email": form.email.data.lower()})
        user = AuthService().authenticate(form.email.data, form.password.data)
        if user is None:
            flash("Неверный email или пароль.", "danger")
        else:
            login_user(user)
            flash("Вход выполнен успешно.", "success")
            logger.info("[auth.login] success extra=%s", {"user_id": user.id})
            return redirect(url_for("main.dashboard"))

    return render_template("auth/login.html", form=form)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegistrationForm()
    if form.validate_on_submit():
        logger.info("[auth.register] attempt extra=%s", {"email": form.email.data.lower()})
        try:
            user = AuthService().register_user(form.email.data, form.password.data)
        except ValueError as exc:
            flash(str(exc), "danger")
        else:
            login_user(user)
            flash("Регистрация прошла успешно.", "success")
            logger.info("[auth.register] success extra=%s", {"user_id": user.id})
            return redirect(url_for("main.dashboard"))

    return render_template("auth/register.html", form=form)


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logger.info("[auth.logout] start extra=%s", {"user_id": current_user.id})
    logout_user()
    flash("Вы вышли из системы.", "success")
    return redirect(url_for("auth.login"))
