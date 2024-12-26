from django.test import TestCase


# Create your tests here.
class Txt2ImgTestCase(TestCase):
    def Txt2Img(self):
        a = 1
        b = 1
        result = a + b
        self.assertEqual(result, 2)
