from django.conf.urls.defaults import *


urlpatterns = patterns('gtd.todo.views',

    (r'^report/$', 'all_tasks'), #this one's just a test
    #(r'^archived/$', 'archived'),
    (r'^outstanding/$', 'outstanding'),
    (r'^completed/$', 'completed'),
    (r'^task/new$', 'createTask'),
    (r'^context/new$', 'createContext'),
    (r'^context/(?P<contextId>\d+)/task/(?P<taskId>\d+)/$$', 'context'),
    (r'^context/task/(?P<taskId>\d+)/$$', 'context'),
    (r'^context/(\d+)/$', 'context'),
    (r'^context/$', 'context'),
    (r'^project/new$', 'createProject'),
    (r'^project/(?P<projectId>\d+)/task/(?P<taskId>\d+)/$', 'project'),
    (r'^project/task/(?P<taskId>\d+)/$', 'project'),

    (r'^project/(\d+)/$', 'project'),
    (r'^project/$', 'project'),
    (r'^task/\d+/$', 'task'),
    (r'^$', 'outstanding'),
    (r'^generate-test-data$', 'generateTestData'), #demo data - you want to disable this in production!
    
)
