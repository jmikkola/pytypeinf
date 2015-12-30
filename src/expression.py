from infer import InferenceError

class Expression:
    def __str__(self):
        return repr(self)

def fn_type_name(num_args):
    return 'Fn_{}'.format(num_args)

def var_name_id(name):
    return 'var_' + name

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
        scoped_var = registry.lookup_var_in_scope(self._name)
        if scoped_var is None:
            raise InferenceError('Variable {} is not defined'.format(self._name))

        scoped_var_id, is_generic = scoped_var
        if is_generic:
            generic_id = 'gen_{}.{}'.format(
                registry.generate_new_id(), scoped_var_id
            )
            registry.register_for_id(generic_id, self)
            rules.instance_of(generic_id, scoped_var_id)
            return generic_id
        else:
            return scoped_var_id

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
    def __init__(self, bindings, body_expr):
        self._bindings = bindings
        self._body = body_expr

    def add_to_rules(self, rules, registry):
        id_ = registry.add_to_registry(self)

        scoped_var_names = {
            name: 'var_{}_{}'.format(name, registry.generate_new_id())
            for (name, _) in self._bindings
        }
        registry.push_new_scope({
            name: (scoped_var_names[name], True)
            for (name, _) in self._bindings
        })

        for name, expr in self._bindings:
            expr_id = expr.add_to_rules(rules, registry)
            rules.equal(scoped_var_names[name], expr_id)

        body_id = self._body.add_to_rules(rules, registry)
        rules.equal(id_, body_id)

        registry.pop_current_scope()
        return id_

    def __repr__(self):
        return 'Let({}, {})'.format(self._bindings, self._body)

class Lambda(Expression):
    def __init__(self, arg_names, body_expr):
        self._arg_names = arg_names
        self._body = body_expr

    def add_to_rules(self, rules, registry):
        id_ = registry.add_to_registry(self)

        scoped_var_names = {
            name: 'var_{}_{}'.format(name, registry.generate_new_id())
            for name in self._arg_names
        }
        # False because this doesn't support 2nd order polymorphism
        registry.push_new_scope({
            name: (scoped_var_names[name], False)
            for name in self._arg_names
        })

        body_id = self._body.add_to_rules(rules, registry)
        arg_ids = [scoped_var_names[name] for name in self._arg_names]

        type_name = fn_type_name(len(arg_ids))
        this_type = tuple([type_name] + arg_ids + [body_id])
        rules.specify(id_, this_type)

        registry.pop_current_scope()
        return id_

    def __repr__(self):
        return 'Lambda({}, {})'.format(self._arg_names, self._body)
