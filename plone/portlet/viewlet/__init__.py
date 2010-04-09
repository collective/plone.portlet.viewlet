from zope.i18nmessageid import MessageFactory
PloneMessageFactory = MessageFactory('plone')

from Products.CMFCore.permissions import setDefaultRoles
setDefaultRoles('plone.portlet.viewlet: Add viewlet portlet', ('Manager',))

VIEWLET_BLACKLIST = set()
MANAGER_BLACKLIST = set()

def excludeViewlet(name):
    """Exclude a particular viewlet from being added"""
    VIEWLET_BLACKLIST.add(name)

def excludeManager(name):
    """Exclude viewlets from a particular viewlet manager from being added"""
    MANAGER_BLACKLIST.add(name)
