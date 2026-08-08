from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from quizzes.views import category_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('category/<slug:slug>/', category_page, name='category-page'),
    path('api/', include('quizzes.urls')),
    path('', TemplateView.as_view(template_name='index.html')),
]
