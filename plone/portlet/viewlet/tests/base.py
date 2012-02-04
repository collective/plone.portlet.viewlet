from Testing import ZopeTestCase as ztc
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

class DummyViewlet(object):
    pass

@onsetup
def setup_package():
    fiveconfigure.debug_mode = True
    import plone.portlet.viewlet
    zcml.load_config('configure.zcml', plone.portlet.viewlet)
    fiveconfigure.debug_mode = False
    ztc.installPackage('plone.portlet.viewlet')

setup_package()
ptc.setupPloneSite(extension_profiles=(
    'plone.portlet.viewlet:default',
))

class TestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """
        
class FunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """
