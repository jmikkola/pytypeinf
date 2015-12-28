import graph

class InferenceError(Exception):
    pass

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

    def instance_of(self, t1, t2):
        self.add_var(t1)
        self.add_var(t2)
        self._generic_relations.append( (t1, t2) )
        return self

    def infer(self):
        types, subs = self._collapse_equal()
        return types, subs

    def _collapse_equal(self):
        types = {}
        subs = {}
        equal_rules = [r for r in self._equal_rules]

        for var, given in self._specified_types:
            result, new_rules = self._merge_types(types.get(var), given)
            if new_rules:
                equal_rules.extend(new_rules)
            types[var] = result

        while equal_rules:
            t1, t2 = equal_rules.pop()
            # TODO: handle existing subs
            result, new_rules = self._merge_types(types.get(t1), types.get(t2))
            if new_rules:
                equal_rules.extend(new_rules)
            subs[t2] = t1
            if t2 in types:
                del types[t2]

            if result is not None:
                types[t1] = result
            elif t1 in types:
                del types[t1]

        return types, subs

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

def infer(rules, known_types):
    rules, subs = collapse_equal(rules)
    rules = expand_generic_relations(rules)
    rules = apply_generic_relations(rules)
    return rules_to_variables(rules, subs)

def rules_to_variables(rules, subs):
    variables = dict(rules)
    for replaced, replacement in subs.iteritems():
        variables[replaced] = variables[replacement]
    return variables

def expand_generic_relations(rules):
    # TODO
    return rules

def apply_generic_relations(rules):
    # graph = graph_from_rules(rules)
    # components = graph.strongly_connected_components()
    # -- Do they already come out sorted?
    # ordered_components = order_components(components, graph)
    # component_types = {}
    # for component in ordered_component:
    #     component_types[component] = resolve_type(component)
    return rules

def collapse_equal(rules):
    # TODO
    return rules, {}
