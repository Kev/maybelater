# Create your views here.

from django.shortcuts import render_to_response 
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from maybelater.models import Task, Project, Context, PRIORITIES, EFFORTS
from django.http import HttpResponseRedirect

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
        Q(context__name__icontains=query)
    ) 

def searchTasks(request, filterQ=()):
    """ Search the tasks for the given filter, also filtering by search term
        if request contains a GET search query
    """
    query = request.GET.get('search', '')
    if query:
        tasks = Task.objects.filter(taskSearchFilter(query, request.user) & filterQ & Q(user=request.user)).distinct()
    else:
        tasks = Task.objects.filter(filterQ & Q(user=request.user))
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
    standard = {'user':request.user, 'menu_items':menu_items(currentLink),
     'context_listing':context_listing(request.user), 
     'project_listing':project_listing(request.user),   
     'effort_listing':effort_listing(), 
     'priority_listing':priority_listing(),
     'return_path':request.path
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
    else:
        selected_task = None
    (todo_listing, query) = searchTasks(request, (Q(completed=True)))
    return render_to_response("%s/completed.html" % templatePrefix(request), mergeStandardDict(request, {'task_link_prefix':constructTaskLink('/completed', None),  'selected_task':selected_task, 'todo_listing': todo_listing, 'query': query  }, 'Completed'))

@login_required
def outstanding(request, taskId=None): 
    if taskId:
        taskId = int(taskId)
    if not user_request_okay(request.user, taskId=taskId):
        return render_to_response("%s/pagenotfound.html", mergeStandardDict(request, {}, ''))
    (todo_listing, query) = searchTasks(request, (Q(completed=False)))
    if taskId:
        selected_task = Task.objects.get(id=taskId)
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
    else:
        selected_task = None
    
    (todo_listing, query) = searchTasks(request, (Q(project=projectId)& Q(completed=False)))
    return render_to_response("%s/project.html" % templatePrefix(request), mergeStandardDict(request, {'task_link_prefix':constructTaskLink('/project',projectId),  'selected_task':selected_task, 'todo_listing': todo_listing, 'project_name':projectName, 'query': query}, 'Projects'))

@login_required
def context(request, contextId=None, taskId=None):
    if not user_request_okay(request.user, contextId=contextId, taskId=taskId):
        return render_to_response("%s/pagenotfound.html", mergeStandardDict(request, {}, ''))
    contextName = "Inbox"
    if contextId: 
        contextId = int(contextId)
        contextName = Context.objects.get(id=contextId).name
        (todo_listing, query) = searchTasks(request, (Q(context=contextId) & Q(completed=False)))
    else:
        contextId = None
        (todo_listing, query) = searchTasks(request, (Q(context__isnull=True)& Q(completed=False)))
    
    if taskId:
        selected_task = Task.objects.get(id=taskId)
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
    return context(request, contextId, newTask.id)

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