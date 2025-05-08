# auctions




"""
property.js:206 
 POST http://localhost:8000/api/properties/ 500 (Internal Server Error)
property.js:236 Error creating property: Error: Unexpected token '<', "<!DOCTYPE "... is not valid JSON
    at handleApiError (property.js:36:11)
    at async createProperty (property.js:230:13)
    at async HTMLButtonElement.handleSubmit (+page.svelte:234:21)

+page.svelte:262 Error creating property: Error: Unexpected token '<', "<!DOCTYPE "... is not valid JSON
    at handleApiError (property.js:36:11)
    at async createProperty (property.js:230:13)
    at async HTMLButtonElement.handleSubmit (+page.svelte:234:21)
﻿
"""



"""
django.db.utils.OperationalError: no such table: base_location
ERROR 2025-05-07 17:07:59,827 basehttp 9780 136756523431616 "GET /api/properties/?page=1&search=asd&ordering=-created_at HTTP/1.1" 500 213005
INFO 2025-05-07 17:10:33,709 basehttp 9780 136756893574848 "GET /api/accounts/profile/ HTTP/1.1" 200 594
INFO 2025-05-07 17:12:13,172 basehttp 9780 136756893574848 "OPTIONS /api/properties HTTP/1.1" 200 0
ERROR 2025-05-07 17:12:13,287 log 9780 136756523431616 Internal Server Error: /api/properties
Traceback (most recent call last):
  File "/home/ahmed/tech-Savvy-projects/2025/new_ones/newprojects/lib/python3.12/site-packages/django/core/handlers/exception.py", line 55, in inner
    response = get_response(request)
               ^^^^^^^^^^^^^^^^^^^^^
  File "/home/ahmed/tech-Savvy-projects/2025/new_ones/newprojects/lib/python3.12/site-packages/django/utils/deprecation.py", line 122, in __call__
    response = self.process_response(request, response)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ahmed/tech-Savvy-projects/2025/new_ones/newprojects/lib/python3.12/site-packages/django/middleware/common.py", line 108, in process_response
    return self.response_redirect_class(self.get_full_path_with_slash(request))
                                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ahmed/tech-Savvy-projects/2025/new_ones/newprojects/lib/python3.12/site-packages/django/middleware/common.py", line 87, in get_full_path_with_slash
    raise RuntimeError(
RuntimeError: You called this URL via POST, but the URL doesn't end in a slash and you have APPEND_SLASH set. Django can't redirect to the slash URL while maintaining POST data. Change your form to point to localhost:8000/api/properties/ (note the trailing slash), or set APPEND_SLASH=False in your Django settings.
ERROR 2025-05-07 17:12:13,290 basehttp 9780 136756523431616 "POST /api/properties HTTP/1.1" 500 80313
INFO 2025-05-07 17:18:16,889 basehttp 9780 136756893574848 "GET /api/accounts/profile/ HTTP/1.1" 200 594
INFO 2025-05-07 17:20:56,367 basehttp 9780 136756893574848 "OPTIONS /api/properties/ HTTP/1.1" 200 0
ERROR 2025-05-07 17:20:56,500 log 9780 136756523431616 Internal Server Error: /api/properties/
Traceback (most recent call last):
  File "/home/ahmed/tech-Savvy-projects/2025/new_ones/newprojects/lib/python3.12/site-packages/django/core/handlers/exception.py", line 55, in inner
    response = get_response(request)
               ^^^^^^^^^^^^^^^^^^^^^
  File "/home/ahmed/tech-Savvy-projects/2025/new_ones/newprojects/lib/python3.12/site-packages/django/core/handlers/base.py", line 197, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ahmed/tech-Savvy-projects/2025/new_ones/newprojects/lib/python3.12/site-packages/django/views/decorators/csrf.py", line 65, in _view_wrapper
    return view_func(request, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ahmed/tech-Savvy-projects/2025/new_ones/newprojects/lib/python3.12/site-packages/django/views/generic/base.py", line 104, in view
    return self.dispatch(request, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ahmed/tech-Savvy-projects/2025/new_ones/newprojects/lib/python3.12/site-packages/rest_framework/views.py", line 515, in dispatch
    response = self.handle_exception(exc)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ahmed/tech-Savvy-projects/2025/new_ones/newprojects/lib/python3.12/site-packages/rest_framework/views.py", line 475, in handle_exception
    self.raise_uncaught_exception(exc)
  File "/home/ahmed/tech-Savvy-projects/2025/new_ones/newprojects/lib/python3.12/site-packages/rest_framework/views.py", line 486, in raise_uncaught_exception
    raise exc
  File "/home/ahmed/tech-Savvy-projects/2025/new_ones/newprojects/lib/python3.12/site-packages/rest_framework/views.py", line 512, in dispatch
    response = handler(request, *args, **kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ahmed/tech-Savvy-projects/2025/new_ones/newprojects/lib/python3.12/site-packages/rest_framework/generics.py", line 246, in post
    return self.create(request, *args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ahmed/tech-Savvy-projects/2025/new_ones/newprojects/lib/python3.12/site-packages/rest_framework/mixins.py", line 19, in create
    self.perform_create(serializer)
  File "/home/ahmed/tech-Savvy-projects/2025/new_ones/auctions/back/base/views.py", line 119, in perform_create
    serializer.save(owner=self.request.user)
  File "/home/ahmed/tech-Savvy-projects/2025/new_ones/newprojects/lib/python3.12/site-packages/rest_framework/serializers.py", line 210, in save
    self.instance = self.create(validated_data)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ahmed/tech-Savvy-projects/2025/new_ones/newprojects/lib/python3.12/site-packages/rest_framework/serializers.py", line 991, in create
    instance = ModelClass._default_manager.create(**validated_data)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ahmed/tech-Savvy-projects/2025/new_ones/newprojects/lib/python3.12/site-packages/django/db/models/manager.py", line 87, in manager_method
    return getattr(self.get_queryset(), name)(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/ahmed/tech-Savvy-projects/2025/new_ones/newprojects/lib/python3.12/site-packages/django/db/models/query.py", line 663, in create
    obj.save(force_insert=True, using=self.db)
  File "/home/ahmed/tech-Savvy-projects/2025/new_ones/auctions/back/base/models.py", line 216, in save
    prefix = self.property_type.code
             ^^^^^^^^^^^^^^^^^^
  File "/home/ahmed/tech-Savvy-projects/2025/new_ones/newprojects/lib/python3.12/site-packages/django/db/models/fields/related_descriptors.py", line 268, in __get__
    raise self.RelatedObjectDoesNotExist(
base.models.Property.property_type.RelatedObjectDoesNotExist: Property has no property_type.. Did you mean: 'property_type_id'?
ERROR 2025-05-07 17:20:56,510 basehttp 9780 136756523431616 "POST /api/properties/ HTTP/1.1" 500 169871

"""

