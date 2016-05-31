# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import logging
from functools import partial

import yaml
from jinja2 import FileSystemLoader, Environment, TemplateNotFound
from salt.utils import traverse_dict_and_list

log = logging.getLogger(__name__)
strategies = ('overwrite', 'merge-first', 'merge-last', 'remove')


def ext_pillar(minion_id, pillar, *args, **kwargs):
    import salt.utils
    stack = {}
    stack_config_files = list(args)
    traverse = {
        'pillar': partial(salt.utils.traverse_dict_and_list, pillar),
        'grains': partial(salt.utils.traverse_dict_and_list, __grains__),
        'opts': partial(salt.utils.traverse_dict_and_list, __opts__),
        }
    for matcher, matchs in kwargs.iteritems():
        t, matcher = matcher.split(':', 1)
        if t not in traverse:
            raise Exception('Unknown traverse option "{0}", '
                            'should be one of {1}'.format(t, traverse.keys()))
        cfgs = matchs.get(traverse[t](matcher, None), [])
        if not isinstance(cfgs, list):
            cfgs = [cfgs]
        stack_config_files += cfgs
    for cfg in stack_config_files:
        if not os.path.isfile(cfg):
            log.warn('Ignoring pillar stack cfg "{0}": '
                     'file does not exist'.format(cfg))
            continue
        stack = _process_stack_cfg(cfg, stack, minion_id, pillar)
    return stack

def _process_stack_cfg(cfg, stack, minion_id, pillar):
    log.debug('Config: {0}'.format(cfg))
    basedir, filename = os.path.split(cfg)
    jenv = Environment(loader=FileSystemLoader(basedir))
    jenv.globals.update({
        "__opts__": __opts__,
        "__salt__": __salt__,
        "__grains__": __grains__,
        "minion_id": minion_id,
        "pillar": pillar,
        })
    # force pillar.get which doesn't return the truth
    __salt__['pillar.get'] = partial(traverse_dict_and_list, pillar)
    for path in _parse_stack_cfg(jenv.get_template(filename).render(stack=stack)):
        try:
            log.debug('YAML: basedir={0}, path={1}'.format(basedir, path))
            obj = yaml.safe_load(jenv.get_template(path).render(stack=stack))
            if not isinstance(obj, dict):
                log.info('Ignoring pillar stack template "{0}": Can\'t parse '
                         'as a valid yaml dictionnary'.format(path))
                continue
            stack = _merge_dict(stack, obj)
        except TemplateNotFound:
            log.info('Ignoring pillar stack template "{0}": can\'t find from '
                     'root dir "{1}"'.format(path, basedir))
            continue
    return stack


def _cleanup(obj):
    if obj:
        if isinstance(obj, dict):
            obj.pop('__', None)
            for k, v in obj.iteritems():
                obj[k] = _cleanup(v)
        elif isinstance(obj, list) and isinstance(obj[0], dict) \
                and '__' in obj[0]:
            del obj[0]
    return obj


def _merge_dict(stack, obj):
    strategy = obj.pop('__', 'merge-last')
    if strategy not in strategies:
        raise Exception('Unknown strategy "{0}", should be one of {1}'.format(
            strategy, strategies))
    if strategy == 'overwrite':
        return _cleanup(obj)
    else:
        for k, v in obj.iteritems():
            if strategy == 'remove':
                stack.pop(k, None)
                continue
            if k in stack:
                if strategy == 'merge-first':
                    # merge-first is same as merge-last but the other way round
                    # so let's switch stack[k] and v
                    stack_k = stack[k]
                    stack[k] = _cleanup(v)
                    v = stack_k
                if type(stack[k]) != type(v):
                    log.debug('Force overwrite, types differ: '
                              '\'{0}\' != \'{1}\''.format(stack[k], v))
                    stack[k] = _cleanup(v)
                elif isinstance(v, dict):
                    stack[k] = _merge_dict(stack[k], v)
                elif isinstance(v, list):
                    stack[k] = _merge_list(stack[k], v)
                else:
                    stack[k] = v
            else:
                stack[k] = _cleanup(v)
        return stack


def _merge_list(stack, obj):
    strategy = 'merge-last'
    if obj and isinstance(obj[0], dict) and '__' in obj[0]:
        strategy = obj[0]['__']
        del obj[0]
    if strategy not in strategies:
        raise Exception('Unknown strategy "{0}", should be one of {1}'.format(
            strategy, strategies))
    if strategy == 'overwrite':
        return obj
    elif strategy == 'remove':
        return [item for item in stack if item not in obj]
    elif strategy == 'merge-first':
        return obj + stack
    else:
        return stack + obj


def _parse_stack_cfg(content):
    """Allow top level cfg to be YAML"""
    try:
        obj = yaml.safe_load(content)
        if isinstance(obj, list):
            return obj
    except Exception as e:
        pass
    return content.splitlines()
