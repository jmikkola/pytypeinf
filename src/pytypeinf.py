#!/usr/bin/env python3

import collections

class TypeInfError(Exception):
    ''' Raised when the types can't be inferred '''
    pass

class TypeInfBug(Exception):
    ''' Raised when there is a bug in the type inference algorithm '''
    pass

_TypeConstructor = collections.namedtuple('TypeConstructor', 'name components')
class TypeConstructor(_TypeConstructor):
    def apply_replacements(self, replacements):
        return TypeConstructor(
            name=self.name,
            components=[lookup_replacement(tv, replacements)
                        for tv in self.components],
        )

InferenceResult = collections.namedtuple('InferenceResult', 'replacements resolutions')
MergeResult = collections.namedtuple('MergeResult', 'tcon replacements')

def merge_type(left, right):
    if left is None and right is None:
        return MergeResult(tcon=None, replacements={})
    elif left is None:
        return MergeResult(tcon=right, replacements={})
    elif right is None:
        return MergeResult(tcon=left, replacements={})
    else:
        if left.name != right.name:
            raise TypeInfError('Type mismatch {} and {}'.format(left, right))
        elif len(left.components) != len(right.components):
            raise TypeInfError('Kind mismatch {} and {}'.format(left, right))

        equal_pairs = dict(zip(left.components, right.components))

        return MergeResult(
            tcon=left,
            replacements=equal_pairs,
        )


def lookup_replacement(typevar, replacements):
    return replacements.get(typevar, typevar)

def is_replaced(var, replacements):
    return var in replacements

def replace(replaced, replacement, replacements, replaces):
    ''' Modifies replacements and replaces

    :param replaced: type var
    :param replaced: type var
    :param replacements: dict(type var, type var)
    :param replaces: defaultdict(type var, set(type var))'''
    if is_replaced(erplacement, replacements):
        raise TypeInfBug("Can't replace already replaced variable {}".format(replacement))

    replacements.insert(replaced, replacement)
    replaces[replacement].add(replaced)

def infer_equality(equal_pairs, known_types):
    replacements = {}
    replaces = collections.defaultdict(set)

    while equal_pairs:
        tv_a, tv_b = equal_pairs.pop()
        rtv_a = lookup_replacement(tv_a, replacements)
        rtv_b = lookup_replacement(tv_b, replacements)

        # The rule doesn't do anything, go to the next one
        if rtv_a == rtv_b:
            continue

        ty_a = known_types.get(rtv_a)
        ty_b = known_types.get(rtv_b)

        merge_result = merge_types(ty_a, ty_b)

        if merge_result.tcon is not None:
            known_types[rtv_a] = merge_result.tcon

        equal_pairs.extend(merge_result.replacements)

        replaced_with_rtv_b = replaces.get(rtv_b)
        del replaces[rtv_b]

        if replaced_with_rtv_b is not None:
            for old_replaced in replaced_with_rtv_b:
                replace(old_replaced, rtv_a, replacements, replaces)

        replace(rtv_b, rtv_a, replacements, replaces)
        del known_types[rtv_b]

    return InferenceResult(
        replacements=replacements,
        resolutions=resolve_replacements(known_types, replacements),
    )

def resolve_replacements(known_types, replacements):
    return {
        tvar: tcon.apply_replacements(replacements)
        for (tvar, tcon) in known_types.iteritems()
    }

def is_more_general_than(specific, general, resolutions):
    return can_substitute_for(specific, general, resolutions, {})

def can_substitute_for(specific, general, resolutions, replacements):
    if specific in resolutions and general in resolutions:
        return is_tcon_more_general(
            resolutions[specific],
            resolutions[general],
            resolutions,
            replacements,
        )
    elif general in resolutions:
        return False
    else:
        old_replacement = replacements.get(general)
        replacements[general] = specific
        if old_replacement is None:
            return True
        else:
            return old_replacement == specific

def is_tcon_more_general(specific, general, resolutions, replacements):
    if specific.name != general.name:
        return False
    elif len(specific.components) != len(general.components):
        raise TypeInfBug(
            'Same type name but different kinds {} {}'
            .format(specific, general)
        )

    return all(
        can_substitute_for(sc, gc, resolutions, replacements)
        for (sc, gc) in zip(specific.components, general.components)
    )

def collect_subvars(var, known_types):
    result = set()
    collect_subvars_rec(var, known_types, result)
    return result

def collect_subvars_rec(var, known_types, result):
    if var in result:
        return

    result.add(var)
    if var in known_types:
        for sub_var in known_types.get(var).components:
            collect_subvars_rec(var, known_types, result)

GenericExpansion = collections.namedtuple(
    'GenericExpansion', 'equal_pairs generic_relations'
)

def expand_generics(generic_vars, equal_pairs, known_types):
    # TODO!
    return GenericExpansion([], [])
