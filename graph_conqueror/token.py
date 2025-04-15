from rest_framework_simplejwt.tokens import (
    Token,
    BlacklistMixin,
    T,
    AccessToken,
)
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.utils import get_md5_hash_password
from castle_graph.models import ContestUser


class CustomToken(Token):
    @classmethod
    def for_user(cls, user) -> T:
        user_id = getattr(user, api_settings.USER_ID_FIELD)
        if not isinstance(user_id, int):
            user_id = str(user_id)

        contest_user = ContestUser.objects.filter(user_id=user_id).first()

        token = cls()
        token[api_settings.USER_ID_CLAIM] = user_id
        token["contest_user_id"] = contest_user.id if contest_user is not None else None

        if api_settings.CHECK_REVOKE_TOKEN:
            token[api_settings.REVOKE_TOKEN_CLAIM] = get_md5_hash_password(
                user.password
            )

        return token


class RefreshToken(BlacklistMixin["RefreshToken"], CustomToken):
    token_type = "refresh"
    lifetime = api_settings.REFRESH_TOKEN_LIFETIME
    no_copy_claims = (
        api_settings.TOKEN_TYPE_CLAIM,
        "exp",
        api_settings.JTI_CLAIM,
        "jti",
    )
    access_token_class = AccessToken

    @property
    def access_token(self) -> AccessToken:
        access = self.access_token_class()
        access.set_exp(from_time=self.current_time)

        no_copy = self.no_copy_claims
        for claim, value in self.payload.items():
            if claim in no_copy:
                continue
            access[claim] = value

        return access
