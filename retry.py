class AgainException(Exception):
    pass


def hut_login_needed(function):
    def wrapper(self, *args, **kwargs):
        try:
            return function(self, *args, **kwargs)
        except AgainException:
            pass

        self.login()
        self.session_save()
        return function(self, *args, **kwargs)
    return wrapper
