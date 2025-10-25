import pytest
from datetime import datetime

from src.domain.entities.user import User


def test_create_user():
    email = "test@example.com"
    name = "Test User"
    
    user = User.create(email=email, name=name)
    
    assert user.email == email
    assert user.name == name
    assert user.is_active is True
    assert user.id is not None
    assert user.created_at is not None
    assert user.updated_at is None


def test_update_user_name():
    user = User.create(email="test@example.com", name="Original Name")
    original_created_at = user.created_at
    
    new_name = "Updated Name"
    user.update_name(new_name)
    
    assert user.name == new_name
    assert user.updated_at is not None
    assert user.updated_at > original_created_at


def test_deactivate_user():
    user = User.create(email="test@example.com", name="Test User")
    
    user.deactivate()
    
    assert user.is_active is False
    assert user.updated_at is not None


def test_activate_user():
    user = User.create(email="test@example.com", name="Test User")
    user.deactivate()
    
    user.activate()
    
    assert user.is_active is True
    assert user.updated_at is not None
