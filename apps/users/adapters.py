from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Кастомный адаптер для django-allauth.
    Позволяет настроить поведение регистрации и аутентификации пользователей.
    """
    
    def is_open_for_signup(self, request):
        """
        Запрещаем самостоятельную регистрацию пользователей.
        Регистрация возможна только через администратора.
        """
        return False

    def save_user(self, request, user, form, commit=True):
        """
        Сохранение пользователя при регистрации.
        Можно добавить дополнительную логику для обработки кастомных полей.
        """
        user = super().save_user(request, user, form, commit=False)
        
        # Здесь можно добавить логику для установки роли пользователя
        # Например, из данных формы или request
        # user.role = form.cleaned_data.get('role', 'client')
        
        if commit:
            user.save()
        return user
