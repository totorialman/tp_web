from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Question, Answer

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            avatar = self.cleaned_data.get('avatar')
            Profile.objects.create(user=user, avatar=avatar if avatar else None)
        return user

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'content', 'tags'] 

    tags = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Введите теги через запятую'}),
        required=True
    )

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
