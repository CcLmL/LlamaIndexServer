from functools import wraps
from flask import abort, session, g
from flask import request, jsonify, current_app
from info.utils.response_code import RET, error_map
from config import Config


# 登录验证装饰器
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 验证token
        try:
            token = request.headers['Authorization'].split(' ')[1]
        except:
            return jsonify(error_code=RET.AUTHFORMATERR, error_msg=error_map[RET.AUTHFORMATERR])
        if token != Config.SECRET_KEY:
            return jsonify(error_code=RET.AUTHERR, error_msg=error_map[RET.AUTHERR])
        result = func(*args, **kwargs)
        return result

    return wrapper


# 权限验证装饰器
def privilege_required(privilege):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            privilege_list = request.headers['Privilege'].split(' ')
            if privilege not in privilege_list:
                return jsonify(errno=RET.ROLEERR, errmsg=error_map[RET.ROLEERR])
            return f(*args, **kwargs)

        return decorated_function

    return decorator


# 角色验证装饰器
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            role_code = [_role.code for _role in g.user.role]
            print('role', role, role_code)
            if role not in role_code:
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


# 管理员验证装饰器
def admin_required(f):
    return role_required('level3')(f)
