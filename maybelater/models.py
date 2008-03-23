from django.db import models
from django.contrib.auth.models import User

import datetime


class Project(models.Model): 
    name = models.CharField(max_length=250) 
    parent = models.ForeignKey('self', blank=True, null=True)
    user = models.ForeignKey(User)
    def __unicode__(self): 
        return self.name 
 
    class Meta: 
        ordering = ['name'] 
    class Admin: 
        pass

class Context(models.Model): 
    name = models.CharField(max_length=250) 
    parent =  models.ForeignKey('self', blank=True, null=True)
    user = models.ForeignKey(User)
    def __unicode__(self): 
        return self.name 

    class Meta: 
        ordering = ['name'] 
    class Admin: 
        pass

class UserJid(models.Model):
    """ Hold a jid for contact with a user
    """
    user = models.ForeignKey(User)
    jid = models.CharField(max_length=250, unique=True)
    authRequested = models.BooleanField(default=False)
    
    class Admin: 
        pass
   
PRIORITIES = ( 
(1, 'Very Low'), 
(2, 'Low'), 
(3, 'Normal'), 
(4, 'High'), 
(5, 'Very High'),
)

EFFORTS = ( 
(1, 'Very Low'), 
(2, 'Low'), 
(3, 'Normal'), 
(4, 'High'), 
(5, 'Very High'), 
)

class Task(models.Model): 
    priority = models.IntegerField(choices=PRIORITIES, default=2) 
    completed = models.BooleanField(default=False) 
    name = models.CharField(max_length=250) 
    notes = models.CharField(max_length=2000, null=True, blank=True) 
    project = models.ForeignKey(Project, null=True, blank=True)
    context = models.ForeignKey(Context, null=True, blank=True) 
    effort = models.IntegerField(choices=EFFORTS, default=1)
    priority = models.IntegerField(choices=PRIORITIES, default=2)
    createdDate = models.DateTimeField(default=datetime.datetime.now) 
    startDate = models.DateTimeField(null=True, blank=True) 
    dueDate = models.DateTimeField(null=True, blank=True) 
    user = models.ForeignKey(User)
 
    def __unicode__(self): 
        return self.name 
    class Meta: 
        ordering = ['-priority', 'name'] 
    class Admin: 
        pass

class TaskUrl(models.Model):
    """ URLs linked from a Task.
    """
    url = models.URLField()
    task = models.ForeignKey(Task, null=False)
    