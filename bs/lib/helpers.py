# -*- coding: utf-8 -*-
import json
"""WebHelpers used in bs."""



from webhelpers import date, feedgenerator, html, number, misc, text


def parameters_display(parameters):
    parameters = json.loads(parameters)
    out = '<ul>'
    for k, v in parameters.iteritems():
        out += '<li>' + k + ' : ' + v + '</li>'
    out += '</ul>'
    return out
