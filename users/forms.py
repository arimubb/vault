import datetime
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm, PasswordResetForm

class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин',widget=forms.TextInput(attrs={'class': 'form-input'}))
    
    password = forms.CharField(label='Пароль',widget=forms.PasswordInput(attrs={'class':'form-input'}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']

class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин',widget=forms.TextInput(attrs={'class': 'form-input-login'}))
        
    password1 = forms.CharField(label='Пароль',widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Повтор пароля',widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        labels = {
            'email': 'E-mail',
            'first_name': 'Имя',
            'last_name': 'Фамилия'
        }   
        widgets = {
            'email': forms.TextInput(attrs={'class': 'form-input-mail'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'})
        }


    
    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError('Такой Email уже существует!')
        return email
    



class ProfileUserForm(forms.ModelForm):
    username = forms.CharField(disabled=True, label='Логин', widget=forms.TextInput(attrs={'class': 'form-input-prof username-input'}))
    email = forms.CharField(disabled=True, label='Email', widget=forms.TextInput(attrs={'class': 'form-input-prof email-input'}))
    this_year = datetime.date.today().year
    date_birth = forms.DateField(label='Дата рождения',widget=forms.SelectDateWidget(years=tuple(range(this_year-55, this_year-18))))
    photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'id': 'id_photo', 'accept': 'image/*'})
    )
    class Meta:
        model = get_user_model()
        fields = ['photo','username', 'email', 'date_birth','first_name', 'last_name']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'})
        }



class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Старый пароль', widget=forms.PasswordInput(attrs={'class':'form-input'}))
    new_password1 = forms.CharField(label='Новый пароль', widget=forms.PasswordInput(attrs={'class':'form-input'}))
    new_password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput(attrs={'class':'form-input'}))

class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-input-reset'})
    )