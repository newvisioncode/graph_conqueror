from castle_graph.models import ContestUser


import jwt
from jwt import InvalidTokenError
from .settings import SECRET_KEY


def decode_token(token: str):
    try:
        decoded = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"],
        )
        return decoded
    except InvalidTokenError:
        return None


class GetContestUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.headers.get("Authorization")
        if token and token.startswith("Bearer "):
            token = token.split(" ")[1]
            payload = decode_token(token)
            if payload:
                request.contest_user = ContestUser.objects.filter(
                    id=payload["contest_user_id"]
                ).first()

        response = self.get_response(request)
        return response
