from rest_framework import authentication
from rest_framework import exceptions
from .models import Token


class BaseJWTAuthentication(authentication.BaseAuthentication):
    def get_user_by_token(self, tokens, request):
        auth_headers = {}
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        is_valid, user_info, refresh_info = Token.validate_token(
            access_token, refresh_token)
        if refresh_info:
            if 'access_token' in refresh_info.keys():
                auth_headers['X-ACCESS-TOKEN'] = refresh_info['access_token']
            if 'refresh_token' in refresh_info.keys():
                auth_headers['X-REFRESH-TOKEN'] = refresh_info['refresh_token']

        if auth_headers:
            request._request.auth_headers = auth_headers
        if not is_valid:
            raise exceptions.NotAuthenticated("You are not logged in")
        return (user_info, tokens)


class JWTAuthentication(BaseJWTAuthentication):
    def authenticate(self, request):
        tokens = {}
        access_token = request.META.get('HTTP_X_ACCESS_TOKEN', None)
        refresh_token = request.META.get('HTTP_X_REFRESH_TOKEN', None)
        if access_token is None:
            raise exceptions.NotAuthenticated('access token not supplied')
        tokens = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }

        return self.get_user_by_token(tokens, request)
