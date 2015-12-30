from collections import namedtuple

from graph import Graph

class InferenceError(Exception):
    pass

def dict_map(fn, d):
    return {k: fn(v) for k, v in d.items()}

class Result(namedtuple('Result', 'types subs')):
    def get_type_by_id(self, expr_id):
        subbed_id = self.subs.get(expr_id, expr_id)
        return self.types.get(subbed_id, None)

class Registry:
    def __init__(self):
        self._next_id = 1
        self._id_to_expression = {}
        self._expression_to_id = {}
        self._scope_stack = []

    def lookup_var_in_scope(self, real_name):
        for scope in self._scope_stack[::-1]:
            if real_name in scope:
                return scope[real_name]
        # TODO: support globals (like `+`)
        return None # Var is not bound

    def push_new_scope(self, scope):
        self._scope_stack.append(scope)

    def pop_current_scope(self):
        self._scope_stack.pop()

    def generate_new_id(self):
        new_id = self._next_id
        self._next_id += 1
        return new_id

    def register_for_id(self, id_, expr):
        if id_ in self._id_to_expression:
            raise Exception(
                'can\'t register ID {} to {}, already registered to {}'
                .format(id_, expr, self._id_to_expression[id_])
            )
        if expr in self._expression_to_id:
            raise Exception(
                'can\'t register {} to ID {}, already registered to ID {}'
                .format(expr, id_, self._expression_to_id[expr])
            )
        self._id_to_expression[id_] = expr
        self._expression_to_id[expr] = id_

    def ensure_registered_as(self, id_, expr):
        if id_ not in self._id_to_expression:
            self.register_for_id(id_, expr)

    def get_registered(self):
        return self._id_to_expression

    def get_id_for(self, expr):
        return self._expression_to_id.get(expr, None)

    def add_to_registry(self, expr):
        id_ = self.generate_new_id()
        self.register_for_id(id_, expr)
        return id_

class Rules:
    def __init__(self):
        self._equal_rules = []
        self._specified_types = []
        self._generic_relations = []

    def equal(self, t1, t2):
        self._equal_rules.append( (t1, t2) )
        return self

    def specify(self, t1, given):
        self._specified_types.append( (t1, given) )
        return self

    def instance_of(self, instance, general):
        self._generic_relations.append( (instance, general) )
        return self

    def infer(self):
        types, subs = self._collapse_equal()
        types1, subs1 = self._apply_generics(types, subs)
        return Result(types1, subs1)

    def _equality_pairs_from_set(self, items):
        if len(items) < 2:
            return []
        ii = iter(items)
        primary = next(ii)
        return [(primary, item) for item in ii]

    def _apply_generics(self, types, subs):
        subbed_generic_relations = [
            (subs.get(i, i), subs.get(g, g))
            for (i, g) in self._generic_relations
        ]
        generic_relations = Graph.from_edges(subbed_generic_relations)
        subcomps = generic_relations.strongly_connected_components()
        for subcomponent in subcomps:
            equality_pairs = self._equality_pairs_from_set(subcomponent)
            if equality_pairs:
                types, subs = self._apply_equal_rules(equality_pairs, types, subs)

        generic_pairs = self._pick_generic_pairs(generic_relations, subcomps)
        return self._apply_generic_rules(generic_pairs, types), subs

    def _pick_generic_pairs(self, graph, subcomponents):
        pairs = []
        for subcomponent in subcomponents:
            for var in subcomponent:
                for child_var in graph.get_children(var):
                    pairs.append( (var, child_var) )
        return pairs

    def _apply_generic_rules(self, generic_pairs, types):
        while generic_pairs:
            instance, general = generic_pairs.pop()
            # Substitutions should have already been applied
            itype, gtype = types.get(instance), types.get(general)

            result, new_pairs = self._merge_generic(itype, gtype)
            if new_pairs:
                generic_pairs.extend(new_pairs)
            if result is not None:
                types[instance] = result

        return types

    def _merge_generic(self, itype, gtype):
        if gtype is None:
            return itype, []
        elif itype is None:
            return gtype, []
        else:
            if self._type_con(itype) != self._type_con(gtype):
                raise InferenceError('{} is not a subtype of {}'
                                     .format(itype, gtype))
            new_rules = zip(self._type_vars(itype), self._type_vars(gtype))
            return itype, new_rules

    def _collapse_equal(self):
        types, adtnl_equal_rules = self._collapse_specified_types()
        equal_rules = self._equal_rules + adtnl_equal_rules
        return self._apply_equal_rules(equal_rules, types, subs={})

    def _collapse_specified_types(self):
        ''' This handles any case where twoo types have
        been given for the same variable. '''
        types = {}
        equal_rules = []

        for var, given in self._specified_types:
            result, new_rules = self._merge_types(types.get(var), given)
            if new_rules:
                equal_rules.extend(new_rules)
            types[var] = result

        return types, equal_rules

    def _apply_equal_rules(self, equal_rules, types, subs):
        while equal_rules:
            t1, t2 = equal_rules.pop()
            t1, t2 = subs.get(t1, t1), subs.get(t2, t2)
            type1, type2 = types.get(t1), types.get(t2)

            # Default to the type that is set to make the output
            # more predictable. This doesn't actually do anything
            # for the algorithm.
            if type1 is None and type2 is not None:
                replacement, replaced = t2, t1
            else:
                replacement, replaced = t1, t2

            result, new_rules = self._merge_types(type1, type2)
            if new_rules:
                equal_rules.extend(new_rules)
            subs = self._add_replacement(subs, replaced, replacement)
            if replaced in types:
                del types[replaced]

            if result is not None:
                types[replacement] = result
            elif replacement in types:
                del types[replacement]

            types = self._apply_sub_to_types(types, replaced, replacement)

        return types, subs

    def _add_replacement(self, old_subs, replaced, replacement):
        if replaced == replacement:
            return old_subs
        subs = dict_map(lambda t: replacement if t == replaced else t, old_subs)
        subs[replaced] = replacement
        return subs

    def _merge_types(self, t1, t2):
        if t1 is None:
            return t2, []
        elif t2 is None:
            return t1, []

        if self._type_con(t1) != self._type_con(t2):
            raise InferenceError('{} is not compatible with {}'.format(t1, t2))
        new_rules = zip(self._type_vars(t1), self._type_vars(t2))
        return t1, new_rules

    def _type_con(self, type_spec):
        if isinstance(type_spec, tuple):
            return type_spec[0]
        return type_spec

    def _type_vars(self, type_spec):
        if isinstance(type_spec, tuple):
            return type_spec[1:]
        return []

    def _apply_sub_to_type(self, type_spec, replaced, replacement):
        replace = lambda v: replacement if v == replaced else v
        if isinstance(type_spec, tuple):
            updated = list(map(replace, type_spec[1:]))
            return tuple([type_spec[0]] + updated)
        return type_spec

    def _apply_sub_to_types(self, types, replaced, replacement):
        replacer = lambda t: self._apply_sub_to_type(t, replaced, replacement)
        return dict_map(replacer, types)

    def dump_state(self):
        ''' for debugging '''
        return {
            'equal_rules': self._equal_rules,
            'specified_types': self._specified_types,
            'generic_relations': self._generic_relations,
        }
