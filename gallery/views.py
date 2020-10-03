from django.shortcuts import render
from django.views.generic.edit import CreateView, FormView, UpdateView, DeleteView
from .models import Handicraft, Author, Comment
from django.views.generic.list import ListView
from django.urls import reverse_lazy, reverse
from django.views.generic.detail import DetailView
from .forms import CommentForm, UserAddForm
from django.shortcuts import redirect, render, HttpResponse
from django.views import View
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm


class AuthorCreateView(CreateView):
    model = Author
    fields = ['first_name', 'surname', 'curriculum_vitae']
    success_url = reverse_lazy('authors')


class UserCreateView(CreateView):
    model = User
    fields = ['first_name', 'surname', 'curriculum_vitae']
    success_url = reverse_lazy('authors')


class AuthorsListView(ListView):
    model = Author


class HandicraftListView(ListView):
    model = Handicraft


class HandicraftCreateView(CreateView):
    model = Handicraft
    fields = ['image', 'title', 'category', 'description', 'author', 'added_date', 'added_by', 'price']
    success_url = reverse_lazy('handicrafs')


class HandicraftDetailView(DetailView):
    model = Handicraft

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['comment_form'] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = Comment(
                author=request.user,
                handicraft=self.get_object(),
                text=comment_form.cleaned_data['comment']
            )
            comment.save()
        else:
            raise Exception
        return redirect(reverse('detail', args=[self.get_object_or_404().id]))


class HomePage(View):
    def get(self, request):
        return render(request, 'base.html')


class UserCreateView(View):
    def get(self, request):
        form = UserAddForm()
        return render(request, 'add_user.html', {'form': form})

    def post(self, request):
        form = UserAddForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, f'Konto użytkowania {user} zostało stworzone.')
            return redirect('login')
        return render(request, 'add_user.html', {'form': form})


class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('authors')
        else:
            messages.error(request, 'Logowanie nie powiodło się')
            return render(request, 'login.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('login')
