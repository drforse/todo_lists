from . import tasks, sign_in, sign_up, test_access_token

routers = [tasks.router, sign_in.router, sign_up.router, test_access_token.router]