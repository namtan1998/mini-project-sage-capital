from app.models import Favorite, Category, Tag
from rest_framework.response import Response
from rest_framework import status

def handle_category(request_data, user):
    if isinstance(request_data['category'], int):
        try:
            category = Category.objects.get(user=user, id=request_data['category'])
            return category.id
        except Category.DoesNotExist:
            raise Category.DoesNotExist('Category does not exist. Please create one first')
    elif isinstance(request_data['category'], str):
        category, created = Category.objects.get_or_create(user_id=user.id, name=request_data['category'])
        return category.id
    else:
        raise ValueError('Invalid category type. Please provide a string or integer.')

def handle_tags_id(request_data, user):
    if not request_data['tags']:
        return []
    if not isinstance(request_data['tags'], list):
        raise ValueError('Invalid tags type. Please provide a list of strings or integers.')

    if not check_same_type(request_data['tags']):
        raise ValueError('Tags must be all strings or all integers.')

    tags_id = []
    for tag in request_data['tags']:
        if isinstance(tag, int):
            try:
                tag_obj = Tag.objects.get(user=user, id=tag)
                tags_id.append(tag_obj.id)
            except Tag.DoesNotExist:
                raise Tag.DoesNotExist('Tag with ID {} does not exist.'.format(tag))
        elif isinstance(tag, str):
            tag_obj, created = Tag.objects.get_or_create(user_id=user.id, name=tag)
            tags_id.append(tag_obj.id)
        else: 
            return ValueError('Invalid tag type. Please provide a string or integer.')

    return tags_id

def check_same_type(list_tags: list):
   return all(isinstance(item, type(list_tags[0])) for item in list_tags)