from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return False

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        if commit:
            user.save()
        return user
