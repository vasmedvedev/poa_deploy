from django.test import TestCase
import poa_deploy.utils as utils
import xml.etree.ElementTree as ET

def dummy_appmeta_url(url):
        return '/home/django/poa_api/poa_deploy/testing_stuff/APP-META1.XML'

class UtilsTest(TestCase):

    def test_application_url_correct(self):
        """
        application_url_correct(url) should return True if app URL is string
        and formatted correctly, False otherwise
        """

        goodurl1 = 'https://apscatalog.com/storage/Hostway/ESC-SKIN/3.0.16-1/Hostway/undefined/undefined/undefined/ESC-SKIN-3.0.16-1.app.zip'
        goodurl2 = 'https://apscatalog.com/storage/Zen%20Cart/Zen%20Cart/1.5.3-5/GlowTouch%20Technologies/undefined/undefined/undefined/ZenCart-1.5.3-5.app.zip'
        badurls = {
                  1: 3,
                  2: 'http://apscatalog.com/storage/Zen%20Cart/Zen%20Cart/1.5.3-5/GlowTouch%20Technologies/undefined/undefined/undefined/ZenCart-1.5.3-5.app.zip',
                  3: 'http://google.com',
                  4: {},
                  5: [],
                  6: '<script></script>'
        }
        self.assertEqual(utils.application_url_correct(goodurl1), True)
        self.assertEqual(utils.application_url_correct(goodurl2), True)
        for urlnum in range(1,7):
            self.assertEqual(utils.application_url_correct(badurls[urlnum]), False)

    def test_get_appmeta_url(self):
        """ test getting URL of APP-META.xml """

        url1 = 'https://apscatalog.com/storage/Hostway/ESC-SKIN/3.0.16-1/Hostway/undefined/undefined/undefined/ESC-SKIN-3.0.16-1.app.zip'
        url2 = 'https://apscatalog.com/storage/Zen%20Cart/Zen%20Cart/1.5.3-5/GlowTouch%20Technologies/undefined/undefined/undefined/ZenCart-1.5.3-5.app.zip'
        appmeta1 = 'https://apscatalog.com/storage/Hostway/ESC-SKIN/3.0.16-1/Hostway/undefined/undefined/undefined/resources/APP-META.xml'
        appmeta2 = 'https://apscatalog.com/storage/Zen%20Cart/Zen%20Cart/1.5.3-5/GlowTouch%20Technologies/undefined/undefined/undefined/resources/APP-META.xml'
        self.assertEqual(utils.get_appmeta_url(url1), appmeta1)
        self.assertEqual(utils.get_appmeta_url(url2), appmeta2)

    def test_get_appmeta_parsed(self):
        """ Testing ElementTree object retrieving from XML """

        url1 = 'https://apscatalog.com/storage/Zen%20Cart/Zen%20Cart/1.5.3-5/GlowTouch%20Technologies/undefined/undefined/undefined/resources/APP-META.xml'
        utils.urllib2.urlopen = dummy_appmeta_url
        self.assertEqual(isinstance(utils.get_app_meta_parsed(url1), ET), True)