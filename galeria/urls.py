"""galeria URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from gallery.views import AuthorCreateView, AuthorsListView, HandicraftListView, HandicraftCreateView, \
    HandicraftDetailView, UserCreateView, LoginView, logout_user, OrderCreateView, \
    PaintingListView, PicturesListView, HomeView, ContactView, buy_art, AuthorsDetailView, AuthorsUpdateView, \
    AuthorsDeleteView, OrderView, remove_art, OrderConfirmationView, HandicraftUpdateView, \
    HandicraftDeleteView, AvailableHandicraftList2, UserUpdateView, PasswordUpdateView, ProfileView, SuccessView

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('accounts/', include('django.contrib.auth.urls')),
                  path('accounts/profile/', ProfileView.as_view(), name='profile1'),


                  path('add-author/', AuthorCreateView.as_view(), name='add_author'),
                  path('update_author/<pk>', AuthorsUpdateView.as_view(), name='update_author'),
                  path('delete_author/<pk>', AuthorsDeleteView.as_view(), name='delete_author'),
                  path('authors/', AuthorsListView.as_view(), name='authors'),
                  path('author/<pk>', AuthorsDetailView.as_view(), name='author'),

                  path('dziela/', HandicraftListView.as_view(), name='handicrafs'),
                  path('dodaj_dzielo/', HandicraftCreateView.as_view(), name='add-handicraf'),
                  path('paintings/', PaintingListView.as_view(), name='paintings'),
                  path('pictures/', PicturesListView.as_view(), name='pictures'),
                  # path('offer/', AvailableHandicraftList.as_view(), name='offer'),
                  path('handicraft/<pk>/', HandicraftDetailView.as_view(), name='detail'),
                  path('update-handicraft/<pk>/', HandicraftUpdateView.as_view(), name='update-handicraft'),
                  path('delete-handicraft/<pk>/', HandicraftDeleteView.as_view(), name='delete-handicraft'),
                  path('offer/', AvailableHandicraftList2.as_view(), name='offer'),

                  path('register/', UserCreateView.as_view(), name='user'),
                  path('update_user/', UserUpdateView.as_view(), name='update_user'),
                  path('login/', LoginView.as_view(), name='login'),
                  path('logout/', logout_user, name='logout'),
                  path('', HomeView.as_view(), name='home'),
                  path('contact/', ContactView.as_view(), name='contact'),
                  path('change-password/', PasswordUpdateView.as_view(template_name='password.html'),
                       name='change-password'),
                  path('success/', SuccessView.as_view(), name='success'),

                  path('add-order/', OrderCreateView.as_view(), name='add-order'),
                  path('buy/<pk>', buy_art, name='buy'),
                  path('remove/<pk>', remove_art, name='remove'),
                  path('order-1/', OrderView.as_view(), name='order-1'),
                  path('profile/', ProfileView.as_view(), name='profile'),
                  path('order/', OrderConfirmationView.as_view(), name='order'),

                  # path('add-to-cart/<pk>/', add_to_cart, name='add-to-cart'),
                  # path('add_art/', add_art, name='add_art'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
