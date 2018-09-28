from django.contrib import admin
from library.models import *
# Register your models here.
admin.site.register(LibraryBook)
admin.site.register(LibraryStock)
admin.site.register(LibraryLoan)
admin.site.register(LibraryEmployee)
admin.site.register(LibraryReader)
admin.site.register(LibraryNotification)
admin.site.register(LibrarySuggestion)