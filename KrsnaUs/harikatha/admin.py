from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin
from .models import User, HarikathaCollection

# Register your models here.

admin.site.register(User, UserAdmin)


class HariKathaCollectionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        print(self.current_user)
        super().__init__(*args, **kwargs)
        self.fields['category'] = forms.ChoiceField(
            choices=HarikathaCollection.CATEGORY_CHOICES
        )

    class Meta:
        model = HarikathaCollection
        fields = '__all__'
        exclude = ('indexed',)


class HariKathaCollectionAdmin(admin.ModelAdmin):
    exclude = ('indexed',)
    form = HariKathaCollectionForm

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

admin.site.register(HarikathaCollection, HariKathaCollectionAdmin)
