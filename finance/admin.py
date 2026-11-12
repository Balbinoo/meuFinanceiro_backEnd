from django.contrib import admin
from .models import User, Goal, Expense, Income, Account

# Register your models here.
admin.site.register(User)
admin.site.register(Goal)
admin.site.register(Expense)
admin.site.register(Income)
admin.site.register(Account)
