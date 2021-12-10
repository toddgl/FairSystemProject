# accounts/view.py
from django.contrib import messages
from .forms import CustomUserChangeForm, ProfileChangeForm
from django.shortcuts import  redirect, render

# Create your views here.

def customuser_update_view(request):
    if request.method == "POST":
        user_form = CustomUserChangeForm(request.POST, instance=request.user)
        profile_form = ProfileChangeForm(request.POST, instance=request.user.profile)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your user details was successfully updated!')
        elif profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Your profile information was successfully updated!')
        else:
            messages.error(request, 'Unable to complete request')
        return redirect("accounts:user-update")
    user_form = CustomUserChangeForm(instance=request.user)
    profile_form = ProfileChangeForm(instance=request.user.profile)
    return render(request=request, template_name="accounts/user_update.html", context={"id": request.user.id, "user_form": user_form, "profile_form": profile_form})
