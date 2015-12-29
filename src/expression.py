class Expression: pass

class TypedExpression(Expression):
    def __init__(self, expr_type, expr):
        self._type = expr_type
        self._expr = expr

    def add_to_rules(self, rules, registry):
        id_ = registry.add_to_registry(self)
        rules.specify(id_, self._type)
        inner_id = self._expr.add_to_rules(rules, registry)
        rules.equal(id_, inner_id)
        return id_

class Variable(Expression):
    def __init__(self, name):
        self._name = name

    def add_to_rules(self, rules, registry):
        id_ = 'var_' + self._name
        return id_

class Literal(Expression):
    def __init__(self, lit_type, value):
        self._type = lit_type
        self._value = value

    def add_to_rules(self, rules, registry):
        id_ = registry.add_to_registry(self)
        rules.specify(id_, self._type)
        return id_

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
        type_name = 'Fn_{}'.format(len(arg_ids))
        this_type = tuple([type_name, fn_id] + arg_ids)

        rules.specify(id_, this_type)
        return id_
