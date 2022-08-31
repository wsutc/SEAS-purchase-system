from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models_data import Requisitioner


def requisitioner_from_user(user: User) -> Requisitioner:
    """Returns Requisitioner object given a user"""
    object = get_object_or_404(Requisitioner, user=user)
    return object
