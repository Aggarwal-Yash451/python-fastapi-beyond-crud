
auth_prefix = f"/api/v1/auth"

def test_user_creation(fake_session, fake_user_service, test_client):
    signup_data = {
            "username": "college",
            "email": "12215049@nitkkr.ac.in",
            "password": "yash123",
            "first_name": "College",
            "last_name": "Yash"
        }
    
    response = test_client.post(    
        url=f"{auth_prefix}/signup",
        json=signup_data,
    )

    assert fake_user_service.user_exists_called_once()