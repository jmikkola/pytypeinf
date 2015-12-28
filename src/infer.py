from graph import Graph

class InferenceError(Exception):
    pass

def dict_map(d, fn):
    return {k: fn(v) for k, v in d.items()}

class Rules:
    def __init__(self, known_types=None):
        if known_types is None:
            known_types = {}
        self._known_types = known_types
        self._known_vars = set()
        self._equal_rules = []
        self._specified_types = []
        self._generic_relations = []

    def add_var(self, t):
        self._known_vars.add(t)

    def equal(self, t1, t2):
        self.add_var(t1)
        self.add_var(t2)
        self._equal_rules.append( (t1, t2) )
        return self

    def specify(self, t1, given):
        self.add_var(t1)
        self._specified_types.append( (t1, given) )
        return self

    def instance_of(self, instance, general):
        self.add_var(instance)
        self.add_var(general)
        self._generic_relations.append( (instance, general) )
        return self

    def infer(self):
        types, subs = self._collapse_equal()
        return self._apply_generics(types, subs)

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
        return self._apply_generic_rules(generic_pairs, types, subs)

    def _pick_generic_pairs(self, graph, subcomponents):
        pairs = []
        for subcomponent in subcomponents:
            for var in subcomponent:
                for child_var in graph.get_children(var):
                    pairs.append( (var, child_var) )
        return pairs

    def _apply_generic_rules(self, generic_pairs, types, substitutions):
        while generic_pairs:
            instance, general = generic_pairs.pop()
            # Substitutions should have already been applied
            itype, gtype = types.get(instance), types.get(general)

            result, new_pairs = self._merge_generic(itype, gtype)
            if new_pairs:
                generic_pairs.extend(new_pairs)
            types[instance] = result

        return types, substitutions

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

        return types, subs

    def _add_replacement(self, old_subs, replaced, replacement):
        if replaced == replacement:
            return old_subs
        subs = dict_map(old_subs, lambda t: replacement if t == replaced else t)
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
        # TODO: support type constructors
        return type_spec

    def _type_vars(self, type_spec):
        # TODO: support type constructors
        return []
