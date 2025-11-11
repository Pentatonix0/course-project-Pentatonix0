from app.modules.auth.auth_endpoints import auth_router
from app.modules.quiz.quiz_endpoints import quiz_router
from app.modules.user.user_endpoints import user_router

all_routers = [auth_router, user_router, quiz_router]
