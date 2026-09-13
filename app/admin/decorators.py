from functools import wraps

from flask import abort
from flask_login import current_user


def admin_required(f):
    """Restrict a view to authenticated users with is_admin=True.
    Anyone else (including anonymous visitors) gets a 403."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated
