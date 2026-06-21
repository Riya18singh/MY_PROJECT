from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Automatically log the user in
            return redirect('product_list') # Redirect to the homepage/products
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})
