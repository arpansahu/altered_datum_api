from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """Storage backend for static files (CSS, JS, images)"""
    location = getattr(settings, 'AWS_STATIC_LOCATION', 'static')
    default_acl = 'public-read'
    file_overwrite = True  # Static files can be overwritten


class PublicMediaStorage(S3Boto3Storage):
    """Storage backend for user-uploaded public media files"""
    location = getattr(settings, 'AWS_PUBLIC_MEDIA_LOCATION', 'media')
    file_overwrite = False  # Don't overwrite user uploads
    default_acl = 'public-read'


class ProtectedMediaStorage(S3Boto3Storage):
    """Storage backend for protected media files (authentication required)"""
    location = getattr(settings, 'AWS_PROTECTED_MEDIA_LOCATION', 'protected')
    file_overwrite = False
    default_acl = 'private'
    custom_domain = False  # Don't use CDN for protected files


class PrivateMediaStorage(S3Boto3Storage):
    """Storage backend for private files (signed URLs required)"""
    location = getattr(settings, 'AWS_PRIVATE_MEDIA_LOCATION', 'private')
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False  # Don't use CDN for private files
    querystring_auth = True  # Generate signed URLs

