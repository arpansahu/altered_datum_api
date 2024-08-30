from django.contrib import admin
from django.urls import path, include
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('blog.urls', namespace='blog')),
    # Oauth
    path('auth/', include('drf_social_oauth2.urls', namespace='drf')),
    # Project URLs
    path('admin/', admin.site.urls),
    path('', include('blog.urls', namespace='blog')),
    # User Management
    path('api/user/', include('accounts.urls', namespace='accounts')),
    # Blog_API Application
    path('api/', include('blog_api.urls', namespace='blog_api')),

    # API schema and Documentation
    path('project/docs/', include_docs_urls(title='BlogAPI')),
    path('project/schema', get_schema_view(
        title="BlogAPI",
        description="API for the BlogAPI",
        version="1.0.0"
    ), name='openapi-schema'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'accounts.views.error_404'
handler500 = 'accounts.views.error_500'
handler403 = 'accounts.views.error_403'
handler400 = 'accounts.views.error_400'