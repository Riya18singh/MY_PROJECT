from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        # Include the default fields plus your custom ones
        fields = UserCreationForm.Meta.fields + ('phone_number',)