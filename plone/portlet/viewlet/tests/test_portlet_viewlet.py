from zope.component import getUtility, getMultiAdapter
from zope.schema.interfaces import IVocabularyFactory

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from Products.Five.browser import BrowserView
from Products.Five import zcml

from plone.portlet.viewlet import portlet as module
from plone.portlet.viewlet import excludeViewlet, excludeManager

from plone.portlet.viewlet.tests.base import TestCase

class TestPortlet(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='plone.portlet.viewlet.ViewletPortlet')
        self.assertEquals(portlet.addview, 'plone.portlet.viewlet.ViewletPortlet')

    def testInterfaces(self):
        portlet = module.Assignment(manager_viewlet=u"plone.portalheader plone.logo")
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='plone.portlet.viewlet.ViewletPortlet')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={'manager_viewlet' : u"plone.portalheader plone.logo"})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], module.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = module.Assignment(manager_viewlet=u"plone.portalheader plone.logo")
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, module.EditForm))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = BrowserView(context, request)
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = module.Assignment(manager_viewlet=u"plone.portalheader plone.logo")

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, module.Renderer))


class TestRenderer(TestCase):
    
    def afterSetUp(self):
        self.setRoles(('Manager',))

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = BrowserView(context, request)
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = assignment or module.Assignment(manager_viewlet=u"plone.portalheader plone.logo")

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_render(self):
        r = self.renderer(context=self.portal, assignment=module.Assignment(manager_viewlet=u"plone.portalheader plone.logo"))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        self.failUnless('<img' in output)

    def test_blacklist(self):
        factory = getUtility(IVocabularyFactory, name='plone.portlet.viewlet.vocab')
        vocab = factory(self.folder)
        self.failUnless('plone.htmlhead plone.htmlhead.title' in vocab)
        excludeViewlet('plone.htmlhead.title')
        vocab = factory(self.folder)
        self.failIf('plone.htmlhead plone.htmlhead.title' in vocab)

        self.failUnless('plone.htmlhead plone.resourceregistries' in vocab)
        excludeManager('plone.htmlhead')
        vocab = factory(self.folder)
        self.failIf('plone.htmlhead plone.resourceregistries' in vocab)        

    def test_vocabulary_includes_iviewview_viewlets(self):
        zcml.load_string('''\
<configure xmlns:browser="http://namespaces.zope.org/browser">
<browser:viewlet
    name="plone.dummyviewlet"
    manager="plone.app.layout.viewlets.interfaces.IBelowContentBody"
    class="plone.portlet.viewlet.tests.base.DummyViewlet"
    view="plone.app.layout.globals.interfaces.IViewView"
    permission="zope2.View"
    />
</configure>''')

        factory = getUtility(IVocabularyFactory, name='plone.portlet.viewlet.vocab')
        vocab = factory(self.folder)
        self.failUnless('plone.belowcontentbody plone.dummyviewlet' in vocab)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
