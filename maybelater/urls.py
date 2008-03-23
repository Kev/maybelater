from django.conf.urls.defaults import *
from django.contrib.auth.views import *

urlpatterns = patterns('maybelater.views',
    #(r'^report/$', 'all_tasks'), #this one's just a test, don't enable it (allows you to see all tasks for all users)
    #(r'^archived/$', 'archived'),
    (r'^profile/$', 'editProfile'),
    (r'^outstanding/$', 'outstanding'),
    (r'^outstanding/task/(?P<taskId>\d+)/$', 'outstanding'),
    (r'^completed/$', 'completed'),
    (r'^completed/task/(?P<taskId>\d+)/$', 'completed'),
    (r'^task/new$', 'createTask'),
    (r'^task/edit$', 'editTask'),
    (r'^context/new$', 'createContext'),
    (r'^context/(?P<contextId>\d+)/task/(?P<taskId>\d+)/$', 'context'),
    (r'^context/task/(?P<taskId>\d+)/$', 'context'),
    (r'^context/(\d+)/$', 'context'),
    (r'^context/$', 'context'),
    (r'^project/new$', 'createProject'),
    (r'^project/(?P<projectId>\d+)/task/(?P<taskId>\d+)/$', 'project'),
    (r'^project/task/(?P<taskId>\d+)/$', 'project'),

    (r'^project/(\d+)/$', 'project'),
    (r'^project/$', 'project'),
    (r'^task/\d+/$', 'task'),
    (r'^$', 'context'),
    (r'^generate-test-data$', 'generateTestData'), #demo data - you want to disable this in production!
    
)

urlpatterns += patterns("",
    #You most likely want the admin interface, but it's possible to do without.
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^logout/$', 'django.contrib.auth.views.logout'),
    )

