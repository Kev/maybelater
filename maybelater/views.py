# Create your views here.

from django.shortcuts import render_to_response 
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import check_password
from maybelater.models import Task, Project, Context, UserJid, PRIORITIES, EFFORTS
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core import serializers


def templatePrefix(request):
    """ Return the user's chosen interface prefix, based on browser.
    """
    return "simple"

def taskSearchFilter(query, user):
    """ Generate tuple of Q filters for Tasks for this User.
    """
    return (
        Q(name__icontains=query) |
        Q(project__name__icontains=query) |
        Q(context__name__icontains=query) |
        Q(notes__icontains=query)
    ) 

def searchTasks(user, request, filterQ=()):
    """ Search the tasks for the given filter, also filtering by search term
        if request contains a GET search query
    """
    query = None
    if request is not None:
        query = request.GET.get('search', None)
    if query is not None:
        tasks = Task.objects.filter(taskSearchFilter(query, user) & filterQ & Q(user=user)).distinct()
    else:
        tasks = Task.objects.filter(filterQ & Q(user=user))
    return (taskResultToDictList(tasks), query)

def taskResultToDictList(tasks):
    """ Take the result of a Task.objects query and add to array.
    """
    todo_listing= [] 
    oddRow = 1
    for task in tasks: 
        todo_dict = {} 
        todo_dict['task_object'] = task 
        if oddRow == 1:
            todo_dict['odd_row'] = True
        oddRow = 1 - oddRow
        todo_listing.append(todo_dict)
    return todo_listing

def user_contexts(user):
    """ Return the contexts filtered by user
    """
    return Context.objects.filter(user=user)
    
def context_listing(user):
    """ List all contexts for this user
    """
    context_listing = [] 
    for context in user_contexts(user): 
        context_dict = {} 
        context_dict['context_object'] = context 
        (todo_listing, query) = activeContextTasks(context.id, user)
        context_dict['active_count'] = len(todo_listing)
        context_listing.append(context_dict)
    return context_listing

def user_projects(user):
    """ Return the projects, filtered by user
    """
    return Project.objects.filter(user=user)

def project_listing(user):
    """ List all projects
    """
    project_listing = [] 
    for project in user_projects(user): 
        project_dict = {} 
        project_dict['project_object'] = project 
        project_listing.append(project_dict)
    return project_listing

def priority_listing():
    """ List all priorities
    """
    priority_listing = [] 
    for (index, name) in PRIORITIES: 
        priority_dict = {} 
        priority_dict['index'] = index
        priority_dict['name'] = name
        priority_listing.append(priority_dict)
    return priority_listing
 
def effort_listing():
    """ List all efforts
    """
    effort_listing = [] 
    for (index, name) in EFFORTS: 
        effort_dict = {} 
        effort_dict['index'] = index
        effort_dict['name'] = name
        effort_listing.append(effort_dict)
    return effort_listing
  
def constructTaskLink(prefix, typeId):
    """ Construct the prefix for task URLs depending if there's a typeId.
    """
    link = prefix
    if typeId:
        link = "%s/%d" % (link, typeId)
    return "%s/%s" % (link, "task")

def menu_items(currentLink):
    """ Construct a list of menu items, including setting the highlighted one.
    """
    links = [#{'name':'Inbox','link':'/context/','current':False},#Inbox is treated specially in the template, it's not a real view
            {'name':'Contexts','link':'/context/','current':False},
            {'name':'Projects','link':'/project/','current':False},
            {'name':'To Complete','link':'/outstanding/','current':False},
            {'name':'Completed','link':'/completed/','current':False},
            #{'name':'Archived','link':'/archived/','current':False},
            #{'name':'Process / Review','link':'/review/','current':False}
            ]
    for linkDict in links:
        if linkDict['name'] == currentLink:
            linkDict['current'] = True
    return links


def mergeStandardDict(request, newDict, currentLink):
    """ Merges specialist dict with the standard template args.
        Specialist keys overwrite standard keys.
    """  
    pathparts = request.path.split('/')
    newPath = ''
    foundTask = False
    for part in pathparts[1:]: #ignore the first (empty) element
        if part == "task":
            foundTask = True
            break
        newPath += "/%s" % part
    if not newPath[-1:] == "/":
        newPath += "/"
    newPath += "task/"
    (inbox_listing, inbox_query) = activeContextTasks(None, request.user)
    standard = {'user':request.user, 'menu_items':menu_items(currentLink),
     'context_listing':context_listing(request.user), 
     'inbox_count':len(inbox_listing),
     'project_listing':project_listing(request.user),   
     'effort_listing':effort_listing(), 
     'priority_listing':priority_listing(),
     'return_path':request.path,
     'newtask_path':newPath
    }
    for newKey in newDict:
        standard[newKey] = newDict[newKey]
    return standard

def user_request_okay(user, taskId=None, contextId=None, projectId=None):
    """ Checks that the user has access to the specified items.
    """
    #FIXME - needs testing
    if taskId:
        task = Task.objects.get(id=taskId)
        if not task or not task.user == user:
            return False
    if contextId:
        context = Context.objects.get(id=contextId)
        if not context or not context.user == user:
            return False
    if projectId:
        project = Project.objects.get(id=projectId)
        if not project or not project.user == user:
            return False
    return True
            

@login_required    
def all_tasks(request): 
    todo_listing = [] 
    for task in Task.objects.all(): 
        todo_dict = {} 
        todo_dict['task_object'] = task 
        todo_listing.append(todo_dict) 
    return render_to_response("%s/all_tasks.html" % templatePrefix(request), { 'todo_listing': todo_listing, 'context_listing':context_listing(), 'project_listing':project_listing() })
    

@login_required
def completed(request, taskId=None): 
    if taskId:
        taskId = int(taskId)
    if not user_request_okay(request.user, taskId=taskId):
        return render_to_response("%s/pagenotfound.html", mergeStandardDict(request, {}, ''))
    if taskId:
        selected_task = Task.objects.get(id=taskId)
        if not selected_task.completed:
            selected_task = None
    else:
        selected_task = None
    
    (todo_listing, query) = searchTasks(request.user, request, (Q(completed=True)))
    return render_to_response("%s/completed.html" % templatePrefix(request), mergeStandardDict(request, {'task_link_prefix':constructTaskLink('/completed', None),  'selected_task':selected_task, 'todo_listing': todo_listing, 'query': query  }, 'Completed'))

@login_required
def outstanding(request, taskId=None): 
    if taskId:
        taskId = int(taskId)
    if not user_request_okay(request.user, taskId=taskId):
        return render_to_response("%s/pagenotfound.html", mergeStandardDict(request, {}, ''))
    (todo_listing, query) = searchTasks(request.user, request, (Q(completed=False)))
    if taskId:
        selected_task = Task.objects.get(id=taskId)
        if selected_task.completed:
            selected_task = None
    else:
        selected_task = None
    return render_to_response("%s/outstanding.html" % templatePrefix(request), mergeStandardDict(request, {'task_link_prefix':constructTaskLink('/outstanding',None),  'selected_task':selected_task, 'todo_listing': todo_listing, 'query': query}, 'To Complete'))

@login_required
def project(request, projectId=None, taskId=None):
    if not user_request_okay(request.user, projectId=projectId, taskId=taskId):
        return render_to_response("%s/pagenotfound.html", mergeStandardDict(request, {}, ''))
    projectName = "Inbox"
    if not projectId: 
        if len(user_projects(request.user)) > 0:
            projectId = user_projects(request.user)[0].id 
        else:
            projectId = None
    else:    
        projectId = int(projectId)
    if projectId:
        projectName = Project.objects.get(id=projectId).name
    else:
        projectName = "No projects"
    if taskId:
        selected_task = Task.objects.get(id=taskId)
        if projectId and not selected_task.project.id == projectId:
            selected_task = None
    else:
        selected_task = None
    
    (todo_listing, query) = searchTasks(request.user, request, (Q(project=projectId)& Q(completed=False)))
    return render_to_response("%s/project.html" % templatePrefix(request), mergeStandardDict(request, {'task_link_prefix':constructTaskLink('/project',projectId),  'selected_task':selected_task, 'todo_listing': todo_listing, 'project_name':projectName, 'query': query}, 'Projects'))

def activeContextTasks(contextId, user, request=None):
    """ List all the tasks which are active today in the specified context.
        If no context is specified, inbox is used, and all unfinished tasks are returned.
        Return is a tuple of the listing and query.
    """
    if contextId is not None:
        q = (Q(context=contextId) & Q(completed=False))
    else:
        q = (Q(context__isnull=True) & Q(completed=False))
    return searchTasks(user, request, q)

@login_required
def context(request, contextId=None, taskId=None):
    if not user_request_okay(request.user, contextId=contextId, taskId=taskId):
        return render_to_response("%s/pagenotfound.html", mergeStandardDict(request, {}, ''))
    contextName = "Inbox"
    if contextId is not None: 
        contextId = int(contextId)
        contextName = Context.objects.get(id=contextId).name
    (todo_listing, query) = activeContextTasks(contextId, request.user, request)

    
    if taskId is not None:
        selected_task = Task.objects.get(id=taskId)
        if contextId is not None and selected_task.context is None:
            selected_task = None
        elif contextId is not None and not selected_task.context.id == contextId:
            selected_task = None
        if contextId is None and selected_task.context is not None:
            selected_task = None
    else:
        selected_task = None
    return render_to_response("%s/context.html" % templatePrefix(request), mergeStandardDict(request, {'task_link_prefix':constructTaskLink("/context",contextId), 'selected_task':selected_task, 'todo_listing': todo_listing, 'context_name':contextName, 'query': query}, 'Contexts'))

@login_required    
def task(request, taskId): 
    if not user_request_okay(request.user, taskId=taskId):
        return render_to_response("%s/pagenotfound.html", mergeStandardDict(request, {}, ''))
    taskId = int(taskId)
    taskObject = Task.objects.get(id=taskId)
    return render_to_response("%s/task.html" % templatePrefix(request), { 'task_object': taskObject })

@login_required
def createContext(request): 
    name = request.POST.get('name', '')
    parent = request.POST.get('parent', '')
    if not user_request_okay(request.user, contextId=parent):
        return render_to_response("%s/pagenotfound.html", mergeStandardDict(request, {}, ''))
    if parent:
        parent = Context.objects.get(id=int(parent))
    else:
        parent = None
    newContext = Context(name=name, parent=parent, user=request.user)
    newContext.save()
    return context(request, newContext.id)

@login_required
def createProject(request): 

    name = request.POST.get('name', '')
    parent = request.POST.get('parent', '')
    if not user_request_okay(request.user, projectId=parent):
        return render_to_response("%s/pagenotfound.html", mergeStandardDict(request, {}, ''))
    if parent:
        parent = Project.objects.get(id=int(parent))
    else:
        parent = None
    newProject = Project(name=name, parent=parent, user=request.user)
    newProject.save()
    return project(request, newProject.id)

@login_required    
def createTask(request):
    name = request.POST.get('name', None)
    projectId = request.POST.get('project', None)
    contextId = request.POST.get('context', None)
    if not user_request_okay(request.user, projectId=projectId, contextId=contextId):
        return render_to_response("%s/pagenotfound.html", mergeStandardDict(request, {}, ''))
    if projectId:
        taskProject = Project.objects.get(id=int(projectId))
    else:
        taskProject = None
    if contextId:
        taskContext = Context.objects.get(id=int(contextId))
    else:
        taskContext = None
    newTask = Task(name=name, project=taskProject, context=taskContext, user=request.user)
    newTask.save()
    redirectPath = "%s%d" % (request.POST.get('newtask_path', "/"), newTask.id)
    return HttpResponseRedirect(redirectPath)

@login_required    
def editProfile(request):
    """ User profile management.
    """
    profile_error = ''
    password_error = ''
    user = request.user
    if request.POST.get('edit_profile', False):
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        if request.POST.get('jid', False):
            try:
                jidObject = UserJid.objects.get(user=user)
            except UserJid.DoesNotExist:
                jidObject = UserJid(user=user)
            jidObject.jid = request.POST.get('jid', None)
            jidObject.save()
            userJid = jidObject.jid
        else:
            try:
                userJid = UserJid.objects.get(user=user)
                userJid.delete()
            except UserJid.DoesNotExist:
                pass
    if request.POST.get('change_password', False):
        old_password = request.POST.get('old_password', None)
        new_password = request.POST.get('new_password', None)
        new_password_verify = request.POST.get('new_password_verify', None)
        if not check_password(old_password, user.password):
            password_error = "The old password doesn't match"
        elif not new_password == new_password_verify:
            password_error = "The new passwords don't match"
        elif new_password_verify == "":
            password_error = "The password cannot be empty"
        else:
            user.set_password(new_password)
            user.save()
    try:
        userJid = UserJid.objects.get(user=user).jid
    except UserJid.DoesNotExist:
        userJid = ""
    return render_to_response("%s/profile.html" % templatePrefix(request), mergeStandardDict(request, {'profile': user, 'jid':userJid, 'password_error':password_error,'profile_error':profile_error}, ''))
        
    
    

@login_required    
def changePassword(request):
    """ Change a user's password.
    """

@login_required    
def v2ui(request):
    """ Deploy the 2nd version ui (javascript).
    """    
    return render_to_response("v2.html", {}, '')
    
@login_required    
def v2_tasks(request):
    """ Reploy the 2nd version ui (javascript).
    """    
    #json_serializer = serializers.get_serializer("json")()
    #response = HttpResponse()
    #json_serializer.serialize(Task.objects.filter(Q(user=request.user)), ensure_ascii=False, stream=response)
    #return response
    queryset = Task.objects.filter(Q(user=request.user))
    root_name = 'tasks' # or it can be queryset.model._meta.verbose_name_plural
    data = '{"total": %s, "%s": %s}' % (queryset.count(), root_name, serializers.serialize('json', queryset))
    return HttpResponse(data, mimetype='text/javascript;')
    

@login_required    
def editTask(request):
    name = request.POST.get('name', None)
    projectId = request.POST.get('project', None)
    contextId = request.POST.get('context', None)
    taskId = request.POST.get('task', None)

    if projectId:
        projectId = int(projectId)
    else:
        projectId = None
    if contextId:
        contextId = int(contextId)
    else:
        contextId = None
    if taskId:
        taskId = int(taskId)
    else:
        taskId = None

    if not user_request_okay(request.user, taskId=taskId, projectId=projectId, contextId=contextId):
        return render_to_response("%s/pagenotfound.html", mergeStandardDict(request, {}, ''))
    task = Task.objects.get(id=taskId)
    if projectId:
        taskProject = Project.objects.get(id=int(projectId))
    else:
        taskProject = None
    if contextId:
        taskContext = Context.objects.get(id=int(contextId))
    else:
        taskContext = None
    task.name = name
    task.project = taskProject
    task.context = taskContext
    task.effort = int(request.POST.get('effort', None))
    task.priority = int(request.POST.get('priority', None))
    task.notes = request.POST.get('notes', '')
    newStartDate = request.POST.get('startDate', 'None')
    if request.POST.get('completed', False):
        newCompleted = True
    else:
        newCompleted = False
    task.completed = newCompleted
    if newStartDate == "None":
        newStartDate = ""
    newDueDate = request.POST.get('dueDate', 'None')
    if newDueDate == "None":
        newDueDate = ""
    task.startDate = newStartDate
    task.dueDate = newDueDate

    task.save()
    return HttpResponseRedirect(request.POST.get('return_path','/'))
    
@login_required    
def generateTestData(request):
    """ Not really a view - generate test data for a system.
    """
    projects = {}
    for name in ("Psi", "GTD", "Housework", "Inventing"):
        project = Project(name=name, user=request.user)
        project.save()
        projects[name] = project
    contexts = {}
    for name in ("Home", "Work", "On the road", "Shopping"):
        context = Context(name=name, user=request.user)
        context.save()
        contexts[name] = context
    stuff = {'Do stuff':None, 'Do Psi stuff':projects['Psi'], 'Wash dishes':projects['Housework']}
    for name in stuff:
        task = Task(name=name, project=stuff[name], user=request.user)
        task.save()
    return HttpResponse("Done")