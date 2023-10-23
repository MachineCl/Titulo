from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

urlpatterns = [
    path('chatbot', views.chatbot, name='chatbot'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('conversations', views.conversation_list, name='conversation_list'),
    path('conversation_list', views.conversation_list, name='conversation_list'),
    path('casillas', login_required(views.casillas), name='casillas'),
    path('formulario', login_required(views.formulario), name='formulario'),
    path('formulario_d', login_required(views.formulario_d), name='formulario_d'),
    path('formulario_p', login_required(views.formulario_p), name='formulario_p'),
    path('formulario_r', login_required(views.formulario_r), name='formulario_r'),
    path('formulario_dieta', login_required(views.formulario_dieta), name='formulario_dieta'),
    path('respuesta', views.respuesta, name='respuesta'),
    path('', views.inicio, name='inicio'),
    path('index', views.index, name='index'),
    path('pesos', login_required(views.pesos), name='pesos'),
    path('configuracion', login_required(views.configuracion), name='configuracion'),
    path('<path:dummy>', RedirectView.as_view(url='/', permanent=False), name='catch-all'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)