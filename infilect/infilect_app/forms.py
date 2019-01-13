from django import forms
from django.contrib.auth import get_user_model
from .models import Photo

User = get_user_model()


def authenticate(email, password):
    try:
        user = User.objects.get(email=email, is_active=True)
    except User.DoesNotExist:
        return {'user': None, 'error': 'Invalid User'}
    # import pdb; pdb.set_trace()
    # is_password_correct = user.check_password(password)
    if user.password == password:
        return {'user': user}
    return {'user': None, 'error': 'Invalid Password'}


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

    def is_valid(self):
        """
        1. Checks if form contains email and password
        2. Then checks if email/password combination is valid
        """
        is_data_format_valid = super(forms.Form, self).is_valid()
        if not is_data_format_valid:
            return False
        email, password = self.data['email'], self.data['password']
        authentication = authenticate(email, password)
        if authentication['user'] is None:
            self.errors['auth'] = authentication['error']
            return False
        self.user = authentication['user']
        return True


class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ('title', 'group', 'image')
