from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from django.db import IntegrityError
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .models import User

class UserRegistrationView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Account created successfully! Please log in.')
            return response
        except IntegrityError as e:
            if 'username' in str(e):
                form.add_error('username', 'This username is already taken. Please choose another one.')
            elif 'email' in str(e):
                form.add_error('email', 'This email is already registered. Please use a different email.')
            else:
                form.add_error(None, 'An error occurred while creating your account. Please try again.')
            return self.form_invalid(form)

class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('products:product_list')  # Redirect to product list after login

    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().username}!')
        return super().form_valid(form)

def logout_view(request):
    """Simple logout view that works reliably"""
    if request.user.is_authenticated:
        messages.info(request, 'You have been logged out successfully.')
        logout(request)
    return redirect('accounts:login')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('accounts:register')
    
    return render(request, 'accounts/delete_account.html')
