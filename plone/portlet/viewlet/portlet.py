from zope.component import queryMultiAdapter, getUtility, getMultiAdapter, getAdapters
from zope.component.interfaces import IFactory

from zope.interface import implements, Interface, alsoProvides
from zope.viewlet.interfaces import IViewlet, IViewletManager
from plone.portlets.manager import PortletManager
from plone.portlets.interfaces import IPortletRenderer, IPortletManager
from Products.Five.browser import BrowserView
from plone.app.layout.globals.interfaces import IViewView

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.schema.vocabulary import SimpleVocabulary

from zope.formlib import form

from plone.portlet.viewlet import VIEWLET_BLACKLIST, MANAGER_BLACKLIST
from plone.portlet.viewlet import PloneMessageFactory as _

class IViewletPortlet(IPortletDataProvider):
    """A portlet to render a viewlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """
    
    manager_viewlet = schema.Choice(title=_(u"Viewlet"),
                                  description=_(u"Select the viewlet"),
                                  required=True,
                                  vocabulary="plone.portlet.viewlet.vocab")


class Assignment(base.Assignment):
    """Portlet assignment.
    
    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    
    implements(IViewletPortlet)
    
    manager_viewlet = None
        
    def __init__(self, manager_viewlet):
        self.manager_viewlet = manager_viewlet
        
    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Viewlet (%s)" % self.manager_viewlet

class Renderer(base.Renderer):
    """Portlet renderer.
    
    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    available = True

    def render(self):
        """ Returns a viewlet, given the names of the viewlet manager and viewlet. """
        manager, viewlet = self.data.manager_viewlet.split(' ', 1)
        if manager in MANAGER_BLACKLIST:
            raise ValueError("Viewlet manager '%s' is blacklisted" % manager)
        if viewlet in VIEWLET_BLACKLIST:
            raise ValueError("Viewlet '%s' is blacklisted" % viewlet)
        managerObj = getMultiAdapter((self.context, self.request, self.view), IViewletManager, manager)
        ## if not viewlet:
        ##     managerObj.update()
        ##    return managerObj.render()
        viewletObj = queryMultiAdapter((self.context, self.request, self.view, managerObj), IViewlet, viewlet)
        if not viewletObj:
            return None
        viewletObj = viewletObj.__of__(self.context)
        viewletObj.update()
        return viewletObj.render()


class AddForm(base.AddForm):
    """Portlet add form.
    
    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IViewletPortlet)
    
    label = _(u"Add Viewlet Portlet")
    description = _(u"This portlet displays a viewlet.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.
    
    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IViewletPortlet)

    label = _(u"Edit Viewlet Portlet")
    description = _(u"This portlet displays a viewlet.")


def vocab(context):
    request = context.REQUEST
    view = BrowserView(context, request)
    alsoProvides(view, IViewView)
    values = []
    for manager_name, manager in getAdapters((context, request, view), IViewletManager):
        if manager_name not in MANAGER_BLACKLIST:
            for viewlet_name, viewlet in getAdapters((context, request, view, manager), IViewlet):
                if viewlet_name not in VIEWLET_BLACKLIST:
                    values.append(' '.join((manager_name, viewlet_name)))
    return SimpleVocabulary.fromValues(values)
