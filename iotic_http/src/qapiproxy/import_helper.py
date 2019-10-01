# Copyright (c) 2017 Iotic Labs Ltd. All rights reserved.

from importlib import import_module

import logging
log = logging.getLogger(__name__)


def getItemFromModule(module, item=None):
    """Loads an item from a module.  E.g.: moduleName=a.b.c is equivalent to 'from a.b import c'. If additionally
       itemName = d, this is equivalent to 'from a.b.c import d'. Returns None on failure"""
    try:
        if item is None:
            item = module.rsplit('.', maxsplit=1)[-1]
            module = module[:-(len(item) + 1)]
        return getattr(import_module(module), item)
    except:
        log.exception('Failed to import %s.%s', module, item if item else '')


def loadConfigurableComponent(config, basename, includeBaseConfig=True, key='impl'):
    """Loads the given component from configuration, as defined (via 'impl') in the given basename config section.
    On failure returns None. includeBaseConfig indicates whether to supply base config section to component in
    addition to implementation specific section. The implementing component should accept a configuration argument
    (or two, if includeBaseConfig is set)."""
    if not (basename in config and
            key in config[basename] and
            config[basename][key] in config):
        log.error('%s section, "%s" value or "%s" section missing', basename, key, key)
        return
    implName = config[basename][key]
    log.debug('Loading component %s (%s)', basename, implName)
    component = getItemFromModule(implName)
    if component is None:
        return
    try:
        if includeBaseConfig:
            return component(dict(config[basename]), dict(config[implName]))
        else:
            return component(dict(config[implName]))
    except:
        log.exception('Failed to initialise %s', implName)
        return
