class Expression:
    def __str__(self):
        return repr(self)

def fn_type_name(num_args):
    return 'Fn_{}'.format(num_args)

class TypedExpression(Expression):
    def __init__(self, expr_type, expr):
        self._type = expr_type
        self._expr = expr

    def add_to_rules(self, rules, registry):
        id_ = registry.add_to_registry(self)
        # TODO: handle compound type here
        rules.specify(id_, self._type)
        inner_id = self._expr.add_to_rules(rules, registry)
        rules.equal(id_, inner_id)
        return id_

    def __repr__(self):
        return 'TypedExpression({}, {})'.format(self._type, self._expr)

class Variable(Expression):
    def __init__(self, name):
        self._name = name

    def add_to_rules(self, rules, registry):
        var_id = 'var_' + self._name
        registry.ensure_registered_as(var_id, self)

        generic_id = registry.generate_new_id()
        rules.instance_of(generic_id, var_id)
        return generic_id

    def __repr__(self):
        return 'Variable({})'.format(self._name)

class Literal(Expression):
    def __init__(self, lit_type, value):
        self._type = lit_type
        self._value = value

    def add_to_rules(self, rules, registry):
        id_ = registry.add_to_registry(self)
        # TODO: handle compound type here
        rules.specify(id_, self._type)
        return id_

    def __repr__(self):
        return 'Literal({}, {})'.format(self._type, self._value)

class Application(Expression):
    def __init__(self, fn_expr, arg_exprs):
        self._fn_expr = fn_expr
        self._arg_exprs = arg_exprs

    def add_to_rules(self, rules, registry):
        id_ = registry.add_to_registry(self)

        fn_id = self._fn_expr.add_to_rules(rules, registry)
        arg_ids = [
            arg.add_to_rules(rules, registry)
            for arg in self._arg_exprs
        ]
        fn_type = tuple([fn_type_name(len(arg_ids))] + arg_ids + [id_])
        rules.specify(fn_id, fn_type)

        return id_

    def __repr__(self):
        return 'Application({}, {})'.format(self._fn_expr, self._arg_exprs)

class Let(Expression):
    def __init__(self, bind_vars, bind_exprs, body_expr):
        self._vars = bind_vars
        self._exprs = bind_exprs
        self._body = body_expr

    def add_to_rules(self, rules, registry):
        id_ = registry.add_to_registry(self)
        # TODO: so far, this is assuming that variable names are unique across
        # all scopes.

        body_id = self._body.add_to_rules(rules, registry)
        bound_var_ids = [
            Variable(name).add_to_rules(rules, registry)
            for name in self._vars
        ]
        bound_expr_ids = [
            expr.add_to_rules(rules, registry)
            for expr in self._exprs
        ]

        for var_id, expr_id in zip(bound_var_ids, bound_expr_ids):
            rules.equal(var_id, expr_id)
        rules.equal(id_, body_id)

        return id_

    def __repr__(self):
        return 'Let({}, {}, {})'.format(self._vars, self._exprs, self._body)

class Lambda(Expression):
    def __init__(self, arg_names, body_expr):
        self._arg_names = arg_names
        self._body = body_expr

    def add_to_rules(self, rules, registry):
        id_ = registry.add_to_registry(self)

        body_id = self._body.add_to_rules(rules, registry)
        arg_ids = [
            Variable(name).add_to_rules(rules, registry)
            for name in self._arg_names
        ]

        # TODO: so far, this is assuming that variable names are unique across
        # all scopes.
        type_name = fn_type_name(len(arg_ids))
        this_type = tuple([type_name] + arg_ids + [body_id])
        rules.specify(id_, this_type)

        return id_

    def __repr__(self):
        return 'Lambda({}, {})'.format(self._arg_names, self._body)
