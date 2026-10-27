from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Profile, Post, Comment


class SignUpForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Create a solid password (min 6 chars)',
            'class': 'form-input',
            'autocomplete': 'new-password'
        }),
        min_length=6,
        help_text="Keep it safe and secret 🔐"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Type that password one more time',
            'class': 'form-input',
            'autocomplete': 'new-password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'e.g. matcha_lover22',
                'class': 'form-input',
                'autocomplete': 'username'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'yourname@campus.edu or personal',
                'class': 'form-input',
                'autocomplete': 'email'
            }),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise ValidationError("A username is required!")
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters long.")
        if not username.replace('_', '').replace('.', '').isalnum():
            raise ValidationError("Letters, numbers, dots, and underscores only!")
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("That handle is already taken! Pick another iconic one.")
        return username.lower()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("Email is required so we can keep in touch.")
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email.lower()

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', "Passwords don't match! Double check and try again.")
        return cleaned_data


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your handle or username',
            'class': 'form-input',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
            'class': 'form-input',
            'autocomplete': 'current-password'
        })
    )


class PostForm(forms.ModelForm):
    MAX_IMAGE_SIZE_MB = 5

    class Meta:
        model = Post
        fields = ['content', 'mood', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': "What's the vibe today? Spill the campus tea, drop a hot take, or share a chaotic thought... ✨",
                'class': 'form-textarea post-textarea',
                'rows': 3,
                'maxlength': 1000
            }),
            'mood': forms.Select(attrs={
                'class': 'form-select mood-select'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-file-input',
                'accept': 'image/jpeg,image/png,image/gif,image/webp'
            })
        }

    def clean_content(self):
        content = self.cleaned_data.get('content', '').strip()
        if not content:
            raise ValidationError("Don't leave us hanging! Post cannot be empty.")
        if len(content) > 1000:
            raise ValidationError("Post exceeds the 1,000 character vibe limit.")
        return content

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Check size
            if image.size > self.MAX_IMAGE_SIZE_MB * 1024 * 1024:
                raise ValidationError(f"Image is too large! Maximum allowed size is {self.MAX_IMAGE_SIZE_MB}MB.")
            # Check extension/type
            content_type = getattr(image, 'content_type', '')
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if content_type and content_type not in allowed_types:
                raise ValidationError("Only JPG, PNG, GIF, and WEBP image formats are supported.")
        return image


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'placeholder': 'Drop your thoughts... 💭',
                'class': 'form-input comment-input',
                'maxlength': 500,
                'autocomplete': 'off'
            })
        }

    def clean_content(self):
        content = self.cleaned_data.get('content', '').strip()
        if not content:
            raise ValidationError("Comment cannot be empty.")
        if len(content) > 500:
            raise ValidationError("Comment is too long (max 500 characters).")
        return content


class ProfileUpdateForm(forms.ModelForm):
    MAX_IMAGE_SIZE_MB = 3

    class Meta:
        model = Profile
        fields = ['display_name', 'bio', 'pronouns', 'campus', 'vibe_tag', 'interests', 'website', 'avatar', 'theme_preference']
        widgets = {
            'display_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Alex Rivera ✨'}),
            'bio': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Tell everyone what makes you tick... (max 300 chars)'}),
            'pronouns': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'they/them, she/her, he/him, any'}),
            'campus': forms.TextInput(attrs={'class': 'form-input', 'placeholder': "NYU '26, Berkeley, High School, Self-taught"}),
            'vibe_tag': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Chief Chaos Officer, Matcha Enthusiast'}),
            'interests': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Indie Rock, Film, Photography, Thrifting, Figma'}),
            'website': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://yourportfolio.me or spotify'}),
            'avatar': forms.FileInput(attrs={'class': 'form-file-input', 'accept': 'image/*'}),
            'theme_preference': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and hasattr(avatar, 'size'):
            if avatar.size > self.MAX_IMAGE_SIZE_MB * 1024 * 1024:
                raise ValidationError(f"Avatar file must be under {self.MAX_IMAGE_SIZE_MB}MB.")
        return avatar


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'your@email.com'}),
        }
