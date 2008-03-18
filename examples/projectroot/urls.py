from django.conf.urls.defaults import *

urlpatterns = patterns('',
    #Only use the following if you're testing locally - you should usually server this in your webserver-proper
    #"Using this method is inefficient and insecure. Do not use this in a production setting. Use this only for development."
    # (http://www.djangoproject.com/documentation/static_files/)
    #(r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/path/to/maybelater/install/static/css'}), 
    (r'^', include('maybelater.urls')),
     
)
