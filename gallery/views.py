from django.shortcuts import render
from django.views.generic.edit import CreateView, FormView, UpdateView, DeleteView
from .models import Handicraft, Author, Comment, Order, OrderHandicraft
from django.views.generic.list import ListView
from django.urls import reverse_lazy, reverse
from django.views.generic.detail import DetailView
from .forms import CommentForm, UserAddForm, ContactForm
from django.shortcuts import redirect, render, HttpResponse, get_object_or_404
from django.views import View
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.utils import timezone
from django.core.mail import send_mail, BadHeaderError


class AuthorCreateView(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'surname', 'curriculum_vitae']
    success_url = reverse_lazy('authors')
    permission_required = "create_author"


class AuthorsListView(ListView):
    model = Author


class HandicraftListView(ListView):
    model = Handicraft


class HandicraftCreateView(PermissionRequiredMixin, CreateView):
    model = Handicraft
    fields = ['image', 'title', 'category', 'description', 'author', 'added_date', 'price']

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        return super().form_valid(form)

    success_url = reverse_lazy('authors')


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
            messages.error(request, 'wysyłanie komentarza nie powiodło się')
            return redirect(reverse('detail', args=[self.get_object().id]))
        return redirect(reverse('detail', args=[self.get_object().id]))


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


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    fields = ['order_handicraft', 'country', 'citi', 'zip', 'street_address', 'house_number', 'flat_number']
    login_url = "login"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    success_url = reverse_lazy('authors')


@login_required
def add_to_cart(request, pk):
    handicraft = get_object_or_404(Handicraft, pk=pk)
    order_handicraft, created = OrderHandicraft.objects.get_or_create(
        user=request.user,
        ordered=False,
        handicraft=handicraft,
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.order_handicraft.filter(handicraft__pk=handicraft.id).exists():
            messages.info(request, "Produkt jest już w koszyku")
            return redirect("order")
        else:
            order.order_handicraft.add(order_handicraft)
            messages.info(request, "This item was added to your cart.")
            return redirect("order")
    else:
        created = timezone.now()
        order = Order.objects.create(
            user=request.user, created=created)
        order.order_handicraft.add(order_handicraft)
        messages.info(request, "This item was added to your cart.")
        return redirect("home")


class PaintingListView(View):
    def get(self, request):
        paintings = Handicraft.objects.filter(category='OBRAZ')
        context = {
            'paintings': paintings,
        }
        return render(request, 'paintings_list.html', context)


class PicturesListView(View):
    def get(self, request):
        pictures = Handicraft.objects.filter(category='ZDJĘCIE')
        context = {
            'pictures': pictures,
        }
        return render(request, 'pictures_list.html', context)


class HomeView(View):
    def get(self, request):
        return render(request, 'home.html')


class ContactView(View):
    def get(self, request):
        form = ContactForm()
        return render(request, 'contact.html', {'form': form})

    def post(self, request):
        form = ContactForm(data=request.POST)
        if form.is_valid():
            subject = f'Wiadomość od {form.cleaned_data["name"]}'
            message = form.cleaned_data["message"]
            from_email = form.cleaned_data["email"]
            recipients = ['jarotalik69@gmail.com']
            try:
                send_mail(subject, message, from_email, recipients, fail_silently=True)
            except BadHeaderError:
                messages.error(request, 'spróbuj ponownie wysyłanie wiadomosci nie powiodło się')
                return render(request, 'contact.html', {'form': form})
            messages.success(request, 'Dziękujemy za kontakt odpowiemy jak najszybciej')
            return render(request, 'contact.html', {'form': form})
        return render(request, 'contact.html', {'form': form})
