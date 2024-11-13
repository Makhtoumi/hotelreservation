def is_receptionist(user):
    return user.groups.filter(name='Réceptionniste').exists()
def is_coo_or_developer(user):
    return user.groups.filter(name__in=['COO', 'Developer']).exists()