class Page:
    def __init__(self, user=None):
        self.user = user

    def display_menu(self, user):
        pass

    def handle_choice(self, choice, user):
        pass

    def page_function(self, user):
        while True:
            self.display_menu(user)
            choice = input("> ")
            self.handle_choice(choice, user)
