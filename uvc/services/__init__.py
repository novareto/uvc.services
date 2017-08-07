# -*- coding: utf-8 -*-

import grok
import uvcsite

from zope.component import getMultiAdapter
from zope.interface import Interface, Attribute, implementer
from zope.location import LocationProxy
from zope.publisher.browser import applySkin
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.http import IHTTPRequest
from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces.browser import IBrowserPublisher


class IServicePublication(Interface):
    pass


class IService(Interface):
    layer = Attribute('Dedicated skin layer')


class IEndpoint(Interface):
    pass


class Endpoint(object):
    grok.implements(IBrowserPublisher, IEndpoint)

    def browserDefault(self, request):
        return self, None
    
    def __init__(self, request, context):
        self.request = request
        self.context = context

    def DELETE(self):
        pass

    def GET(self):
        pass
    
    def HEAD(self):
        pass

    def OPTIONS(self):
        pass
    
    def POST(self):
        pass

    def PUT(self):
        pass

  
class json_output(object):

    def __init__(self, indent=4, sort=None):
        self.indent = self.indent
        self.sort = sort
        
    def __call__(self, method):
        def json_wrapper(endpoint, *args, **kwargs):
            result = method(endpoint, *args, **kwargs)
            return json.dumps(
                result,
                encoding=output_charset,
                indent=pretty_print and 4 or None,
                sort_keys=pretty_print)
            

class Service(grok.MultiAdapter):
    grok.baseclass()
    grok.adapts(uvcsite.IUVCSite, IHTTPRequest)
    grok.implements(IPublishTraverse, IService)
    grok.provides(IService)

    layer = None
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        raise NotImplementedError('implement me')
    
    
class ServicesNamespace(grok.MultiAdapter):
    grok.name('services')
    grok.provides(ITraversable)
    grok.adapts(uvcsite.IUVCSite, IHTTPRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, ignore):
        if not name:
            raise NotImplementedError('Please specify a service.')

        service = getMultiAdapter(
            (self.context, self.request), IService, name=name)
        if service.layer is not None:
            applySkin(self.request, service.layer)
        return LocationProxy(service, self.context, "++services++%s" % name)
