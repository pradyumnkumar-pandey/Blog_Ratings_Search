from django.contrib import admin
from .models import BookMark, CustomUser, Blog, Ratings,Role
from django.contrib.auth.admin import UserAdmin
# Register your models here.


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'is_staff', 'is_superuser', 'is_deleted')
    readonly_fields = ('last_login', 'date_joined',)
    ordering = ('email',)
    search_fields = ('first_name', 'last_name', 'email')
    fieldsets = (
        (
            'Fields',
            {
                'fields': (
                    'email',
                    'first_name',
                    'last_name',
                    'date_joined',
                    'last_login',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'is_deleted',
                    'user_permissions',
                    'password',
                    'role',
                )
            },
        ),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


class BlogAdmin(admin.ModelAdmin):
    list_display = ('author', 'blog_title', 'blog_description', 'created_at')
    fieldsets = (
        (
            'Fields',
            {
                'fields': (
                    'author',
                    'blog_title',
                    'blog_description',
                    'blog_image'
                )
            },
        ),
    )
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Blog,BlogAdmin)
admin.site.register(Role)
admin.site.register(BookMark)
admin.site.register(Ratings)