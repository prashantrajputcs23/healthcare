from django import template

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter(name='is_permit')
def is_permit(user, permission):
    groups = user.groups.all()
    if groups:
        try:
            for group in groups:
                if group.permissions.filter(name__icontains=permission).count() > 0:
                    return True
        except:
            return False
    else:
        return False


@register.filter(name='has_permission_list')
def has_permission_list(user, permission):
    groups = user.groups.all()
    false_count = 0
    if groups:
        try:
            for group in groups:
                for param in permission:
                    if not group.permissions.filter(name__icontains=param).count() > 0:
                        false_count += 1
            if false_count > 0:
                return False
            else:
                return True
        except:
            return False
    else:
        return False


# @register.simple_tag(takes_context=True)
@register.filter(name='url_with_param')
def url_with_param(request):
    url = ""
    for key, value in request.GET.items():
        if key != 'page':
            if 'query' in url:
                break
            url += f'&{key}={value}'
    return url


@register.filter(name='url_with_page')
def url_with_page(request):
    url = ""
    for key, value in request.GET.items():
        if 'query' in url:
            break
        elif 'page' in url:
            break
        else:
            url += f'&{key}={value}' if url != "" else f'{key}={value}'
    return url


@register.filter(name='get_status_icon')
def get_status_icon(status):
    status_string = f'<i class="bx bxs-x-circle text-danger"></i>'
    if status:
        status_string = f'<i class="bx bxs-check-circle text-success"></i>'
    return status_string


@register.filter(name='get_item')
def get_item(dictionary, key):
    """Return dictionary value for the given key."""
    return dictionary.get(key, None)
