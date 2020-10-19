from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail, BadHeaderError
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.views import PasswordChangeView

from .forms import *
from .models import *


class AuthorCreateView(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'surname', 'curriculum_vitae']
    success_url = reverse_lazy('authors')
    permission_required = "create_author"


class AuthorsListView(ListView):
    model = Author
    fields = ['first_name', 'surname', 'curriculum_vitae']
    success_url = reverse_lazy('authors')


class AuthorsDetailView(DetailView):
    model = Author

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class AuthorsUpdateView(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ['first_name', 'surname', 'curriculum_vitae']
    success_url = reverse_lazy('authors')
    permission_required = "create_author"


class AuthorsDeleteView(PermissionRequiredMixin, DeleteView):
    model = Author
    fields = ['first_name', 'surname', 'curriculum_vitae']
    success_url = reverse_lazy('authors')
    permission_required = "create_author"


class HandicraftListView(ListView):
    model = Handicraft


class HandicraftCreateView(PermissionRequiredMixin, CreateView):
    model = Handicraft
    fields = ['image', 'title', 'category', 'description', 'author', 'added_date', 'price']
    permission_required = "create_handicraft"

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        return super().form_valid(form)

    success_url = reverse_lazy('authors')


class HandicraftUpdateView(PermissionRequiredMixin, UpdateView):
    model = Handicraft
    fields = ['image', 'title', 'category', 'description', 'author', 'added_date', 'price']
    success_url = reverse_lazy('offer')
    permission_required = "create_handicraft"


class HandicraftDeleteView(PermissionRequiredMixin, DeleteView):
    model = Handicraft
    fields = ['image', 'title', 'category', 'description', 'author', 'added_date', 'price']
    success_url = reverse_lazy('offer')
    permission_required = "create_handicraft"


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


class UserUpdateView(UpdateView):
    form = UserChangeForm
    fields = ['username', 'email', 'first_name', 'last_name']
    template_name = 'user_profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user


class PasswordUpdateView(PasswordChangeView):
    form = PasswordChangeView
    success_url = reverse_lazy('success')


class SuccessView(View):
    def get(self, request):
        return render(request, 'password_complete.html')


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
                return redirect('home')
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
def buy_art(request, pk):
    handicraft = get_object_or_404(Handicraft, pk=pk)
    order_handicraft, created = OrderArt.objects.get_or_create(
        user=request.user,
        ordered=False,
        handicraft=handicraft,
    )
    handicraft.is_available = False
    handicraft.save()
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.handicrafts.filter(handicraft__id=handicraft.id).exists():
            messages.info(request, "Produkt jest już w koszyku")
            return redirect("order")
        else:
            order.handicrafts.add(order_handicraft)
            messages.info(request, "This item was added to your cart.")
            return redirect("order")
    else:
        created = timezone.now()
        order = Order.objects.create(
            user=request.user, created=created)
        order.handicrafts.add(order_handicraft)
        messages.info(request, "This item was added to your cart.")
        return redirect("order")


@login_required
def remove_art(request, pk):
    handicraft = get_object_or_404(Handicraft, pk=pk)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.handicrafts.filter(handicraft__pk=handicraft.id).exists():
            order_handicraft = OrderArt.objects.filter(
                handicraft=handicraft,
                user=request.user,
                ordered=False
            )[0]
            order.handicrafts.remove(order_handicraft)
            order_handicraft.delete()
            handicraft.is_available = True
            handicraft.save()
            messages.info(request, "This item was removed from your cart.")
            return redirect("order")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("home")
    else:
        messages.info(request, "You do not have an active order")
        return redirect("home")


class OrderView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("order")

    login_url = "login"


class ProfileView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            orders = Order.objects.filter(user=self.request.user).exclude(ordered=False)
            context = {
                'objects': orders
            }
            # for order in orders:
            #     print(order.handicrafts.all())
            return render(self.request, 'history.html', context)
        except ObjectDoesNotExist:
            messages.info(self.request, "Jeszcze u nas niczego nie zamawiałes")
            return redirect("home")

    login_url = "login"


class OrderConfirmationView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = OrderConfirmationForm()
            context = {
                'form': form,
                'object': order,
            }
            return render(self.request, "order.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "nie masz zamówień w trakcie realizacji")
            return redirect("home")

    login_url = "login"

    def post(self, *args, **kwargs):
        form = OrderConfirmationForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                order_handicrafts = order.handicrafts.all()
                order_handicrafts.update(ordered=True)
                for handicraft in order_handicrafts:
                    handicraft.save()
                order.user = self.request.user
                order.ordered = True
                order.additional_info = form.cleaned_data.get('additional_info')
                order.country = form.cleaned_data.get('country')
                order.citi = form.cleaned_data.get('citi')
                order.zip = form.cleaned_data.get('zip')
                order.street_address = form.cleaned_data.get('street_address')
                order.house_number = form.cleaned_data.get('house_number')
                order.flat_number = form.cleaned_data.get('flat_number')
                order.save()
                return redirect("profile")
        except ObjectDoesNotExist:
            messages.warning(self.request, "nie masz zamówień w trakcie realizacji")
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


class AvailableHandicraftList(ListView):
    context_object_name = 'available_list'
    queryset = Handicraft.objects.filter(is_available=True)
    template_name = 'available_handicra.html'


class AvailableHandicraftList2(ListView):
    context_object_name = 'available_list'
    queryset = Handicraft.objects.filter(is_available=True)
    template_name = 'available_handicra2.html'
    # paginate_by = 10
