from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.db import transaction
import jwt
from django.conf import settings
from datetime import datetime
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist
# Create your models here.

SECRET_KEY = settings.SECRET_KEY


ISSUING_REASON_CHOICES = (
    (1, 'LOGIN'),
    (2, 'ACCESS TOKEN EXPIRY')
)

PUBLIC, PRIVATE = 1, 2

FILE_OWNERSHIP = (
    (PUBLIC, 'PUBLIC'),
    (PRIVATE, 'PRIVATE'),
)


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=252)


class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    refresh_token = models.BinaryField()
    access_token = models.BinaryField()
    session_id = models.UUIDField()
    is_valid = models.BooleanField(default=True)
    issuing_reason = models.IntegerField(
        choices=ISSUING_REASON_CHOICES, default=1)
    issued_at = models.DateTimeField(auto_now_add=True)
    last_renewed_at = models.DateTimeField(auto_now=True)

    ACCESS_TOKEN_EXP_TIME = settings.ACCESS_TOKEN_EXP_TIME

    REFRESH_TOKEN_EXP_TIME = settings.REFRESH_TOKEN_EXP_TIME

    @classmethod
    def generate_auth_token(Klass, user, issuing_reason=1,
                            refresh_token_id=None, session_id=None):
        token_key = {}
        if session_id is None:
            session_id = uuid.uuid4()
        token_id = uuid.uuid4()
        access_token = jwt.encode({
            'token_id': str(token_id),
            'user_id': str(user.id),
            'session_id': str(session_id),
            'email': user.email,
            'exp': (datetime.utcnow() +
                    timedelta(seconds=Klass.ACCESS_TOKEN_EXP_TIME)).timestamp()
        }, SECRET_KEY, algorithm='HS256')

        token_key["access_token"] = access_token
        refresh_token = jwt.encode({
            'token_id': str(token_id),
            'user_id': str(user.id),
            'session_id': str(session_id),
            'exp': (datetime.utcnow() +
                    timedelta(
                        seconds=Klass.REFRESH_TOKEN_EXP_TIME)).timestamp()
        }, SECRET_KEY, algorithm='HS256')
        token_key["refresh_token"] = refresh_token

        with transaction.atomic():
            if refresh_token_id:
                try:
                    tokens = Klass.objects.get(id=refresh_token_id)
                    Klass.objects.filter(
                        user_id=tokens.user_id,
                        session_id=tokens.session_id,
                        is_valid=True).update(is_valid=False)
                except ObjectDoesNotExist:  # pragma: no cover
                    pass
            Klass.objects.create(
                id=token_id,
                user=user,
                refresh_token=refresh_token,
                issuing_reason=issuing_reason,
                access_token=access_token,
                session_id=session_id
            )
        return token_key

    @classmethod
    def validate_token(Klass, access_token, refresh_token):
        try:
            user_info = jwt.decode(
                access_token,
                SECRET_KEY,
                algorithms=['HS256']
            )
            try:
                Token.objects.get(id=user_info['token_id'], is_valid=True)
            except ObjectDoesNotExist:
                return(False, {}, None)
        except jwt.ExpiredSignatureError:
            if refresh_token:
                try:
                    refresh_token_obj = jwt.decode(
                        refresh_token,
                        SECRET_KEY,
                        algorithms=['HS256'])
                    if refresh_token_obj:
                        try:
                            db_token_obj = Klass.objects.get(
                                id=refresh_token_obj['token_id'])
                            if(db_token_obj.is_valid):
                                user = CustomUser.objects.get(
                                    id=refresh_token_obj["user_id"])
                                token = Token.generate_auth_token(
                                    user,
                                    2,
                                    refresh_token_obj['token_id'],
                                    refresh_token_obj['session_id']
                                )
                                user_info = jwt.decode(
                                    token["access_token"],
                                    SECRET_KEY,
                                    algorithms=['HS256']
                                )

                                return(True, user_info, token)
                            else:
                                token_obj = Token.objects.get(
                                    user_id=refresh_token_obj["user_id"],
                                    session_id=refresh_token_obj["session_id"], # noqa
                                    is_valid=True)
                                if token_obj:
                                    user_info = jwt.decode(
                                        token_obj.access_token,
                                        SECRET_KEY,
                                        algorithms=['HS256']
                                    )
                                    tokens = {
                                        "access_token": token_obj.access_token, # noqa
                                        "refresh_token": token_obj.refresh_token # noqa
                                    }

                                    return(True, user_info, tokens)

                                else:
                                    return(False, {}, None)

                        except TimeoutError:  # pragma: no cover
                            return(False, {}, None)

                except jwt.ExpiredSignatureError:  # pragma: no cover
                    return(False, {}, None)

                except jwt.InvalidTokenError:  # pragma: no cover
                    return(False, {}, None)

                except ObjectDoesNotExist:  # pragma: no cover
                    return(False, {}, None)
            else:
                return(False, {}, None)  # pragma: no cover

        except jwt.InvalidTokenError:  # pragma: no cover
            return(False, {}, None)
        else:
            return(True, user_info, None)  # pragma: no cover

    @classmethod
    def invalidateRefreshToken(Klass, user_id):
        Klass.objects.filter(user=user_id).update(is_valid=False)
        return True


class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=252)
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)

    @property
    def photos(self):
        photo_count = 0
        # import pdb; pdb.set_trace()
        if Photo.objects.filter(group=self.id):
            photo_count = Photo.objects.filter(group=self.id).count()
        return photo_count


class Photo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ownership = models.IntegerField(choices=FILE_OWNERSHIP,
                                    default=1)
    title = models.CharField(max_length=252)
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name='photo')
    image = models.ImageField(null=True, blank=True, width_field="width_field", height_field="height_field")
    width_field = models.IntegerField(default=0)
    height_field = models.IntegerField(default=0)
    owner_id = models.UUIDField(default=uuid.uuid4)

    # def get_absolute_url(self):
    #     return reverse("post:detail", kwargs={"id": self.id})
    @property
    def url(self):
        return "http://127.0.0.1:8000{}{}".format(settings.MEDIA_URL, self.image)
