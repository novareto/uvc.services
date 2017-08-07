# -*- coding: utf-8 -*-

from grokcore.rest import IRESTLayer

from webob.acceptparse import (
    AcceptLanguage,
    AcceptCharset,
    MIMEAccept,
)

from zope import component
from zope.security.checker import selectChecker
from zope.publisher.publish import mapply
from zope.publisher.interfaces.http import IHTTPException
from zope.security.proxy import removeSecurityProxy

from zope.publisher.http import HTTPRequest
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.app.publication.zopepublication import ZopePublication
from zope.app.publication.requestpublicationfactories import (
    HTTPFactory)

from . import IEndpoint


class JSONPublication(ZopePublication):

    def proxy(self, ob):
        # No security proxy as we handle security at the view level.
        return ob

    def getDefaultTraversal(self, request, obj):
        if IBrowserPublisher.providedBy(obj):
            return obj.browserDefault(request)

        adapter = zope.component.queryMultiAdapter(
            (obj, request), IBrowserPublisher)
        if adapter is not None:
            return adapter.browserDefault(request)
        return obj, None
    
    def callObject(self, request, ob):
        endpoint = IEndpoint(ob, None)
        if endpoint is not None:
            method = getattr(endpoint, request.method, None)
            # do the security check here
            return mapply(method, request.getPositionalArguments(), request)
        else:
            # what do we do ?
            pass


class JSONFactory(object):

    def canHandle(self, environ):
        accept = MIMEAccept(
            environ.get('HTTP_ACCEPT', 'application/json'))

        accept_charset = AcceptCharset(
            environ.get('HTTP_ACCEPT_CHARSET', 'utf-8'))

        accept_language = AcceptLanguage(
            environ.get('HTTP_ACCEPT_LANGUAGE', 'de-DE'))

        return 'application/json' in accept

    def __call__(self):
        return HTTPRequest, JSONPublication
